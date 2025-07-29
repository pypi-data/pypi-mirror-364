from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from functools import partial
from typing import TYPE_CHECKING, Any, Self

import aiormq
from aiormq.exceptions import ChannelClosed, ConnectionClosed
from pamqp.commands import Basic

from .options import AmqpPublisherConfig, PublishOptions
from .ports import CommandSender

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aiormq.types import ArgumentsType
    from pamqp.common import FieldArray, FieldTable

    from .domain import SendCommand

HeaderPrimitive = bytes | bytearray | Decimal | float | int | str | datetime | None
if TYPE_CHECKING:
    HeaderValue = HeaderPrimitive | FieldArray | FieldTable
else:  # pragma: no cover
    HeaderValue = HeaderPrimitive | Any

HeadersDict = dict[str, HeaderValue]


def _prepare_headers(h: Mapping[str, object] | None) -> HeadersDict | None:
    if h is None:
        return None
    return dict(h)  # type: ignore[arg-type]


class AmqpCommandPublisher(CommandSender):
    __slots__ = ("_cfg", "_channel", "_closing", "_connection", "_queue", "_url")

    def __init__(self, url: str, queue_name: str, cfg: AmqpPublisherConfig | None = None) -> None:
        self._url = url
        self._queue = queue_name
        self._cfg = cfg or AmqpPublisherConfig()
        self._connection: aiormq.abc.AbstractConnection | None = None
        self._channel: aiormq.abc.AbstractChannel | None = None
        self._closing = False

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def connect(self) -> None:
        if self._connection and not self._connection.is_closed:
            return

        self._connection = await aiormq.connect(self._url)
        conn = self._connection
        if conn is None:
            raise RuntimeError("aiormq.connect() returned None")

        ch = await conn.channel()
        await self._enable_confirms(ch)

        if self._cfg.ensure_queue:
            args: ArgumentsType | None = None
            if self._cfg.max_priority:
                args = {"x-max-priority": self._cfg.max_priority}

            await ch.queue_declare(
                self._queue,
                durable=True,
                auto_delete=False,
                exclusive=False,
                arguments=args,
            )

        self._channel = ch

    async def close(self) -> None:
        if self._closing:
            return
        self._closing = True

        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            await asyncio.sleep(0)
        finally:
            self._channel = None
            self._connection = None
            self._closing = False

    async def send(self, cmd: SendCommand, *, opts: PublishOptions) -> None:
        payload = self._cfg.serializer.serialize(cmd)
        await self._cfg.retry_policy.run(
            partial(self._send_once_with_reconnect, payload, opts),
        )

    async def _send_once_with_reconnect(self, payload: bytes, opts: PublishOptions) -> None:
        try:
            await self._send_once(payload, opts)
        except (ConnectionClosed, ChannelClosed):
            await asyncio.sleep(0.1)
            await self.connect()
            await self._send_once(payload, opts)

    async def _send_once(self, payload: bytes, opts: PublishOptions) -> None:
        await self._ensure_open()
        ch = self._require_channel()
        props = self._make_properties(opts)
        await self._publish(ch, payload, props)

    async def _publish(
        self,
        ch: aiormq.abc.AbstractChannel,
        payload: bytes,
        props: Basic.Properties,
    ) -> None:
        try:
            await ch.basic_publish(body=payload, routing_key=self._queue, properties=props)
        except TypeError:
            await ch.basic_publish(payload, self._queue, props)  # type: ignore[misc,arg-type]

    def _make_properties(self, opts: PublishOptions) -> Basic.Properties:
        return Basic.Properties(
            delivery_mode=2,
            priority=opts.priority,
            headers=_prepare_headers(opts.headers),
            content_type=self._cfg.serializer.content_type,
            content_encoding=self._cfg.serializer.content_encoding,
        )

    def _require_channel(self) -> aiormq.abc.AbstractChannel:
        ch = self._channel
        if ch is None or ch.is_closed:
            raise RuntimeError("Channel is not available")
        return ch

    async def _ensure_open(self) -> None:
        if self._channel and not self._channel.is_closed:
            return
        await self.connect()

    async def _enable_confirms(self, ch: aiormq.abc.AbstractChannel) -> None:
        if hasattr(ch, "confirm_select"):
            await ch.confirm_select()
        elif hasattr(ch, "confirm_delivery"):
            await ch.confirm_delivery()
