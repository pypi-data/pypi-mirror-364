from .amqp_publisher import AmqpCommandPublisher
from .domain import SendCommand
from .options import AmqpPublisherConfig, PublishOptions
from .ports import CommandSender


class TgDeliveryClient:
    __slots__ = ("_sender",)

    def __init__(self, sender: CommandSender) -> None:
        self._sender = sender

    async def __aenter__(self) -> "TgDeliveryClient":
        if hasattr(self._sender, "connect"):
            await self._sender.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        if hasattr(self._sender, "close"):
            await self._sender.close()

    async def send_text(
        self,
        chat_id: int,
        text: str,
        priority: int,
        *,
        reply_markup: dict[str, object] | None = None,
    ) -> None:
        cmd = SendCommand(chat_id=chat_id, text=text, reply_markup=reply_markup)
        await self._sender.send(cmd, opts=PublishOptions(priority=priority))

    async def send_i18n_text(
        self,
        chat_id: int,
        i18n_key: str,
        priority: int,
        *,
        reply_markup: dict[str, object] | None = None,
        i18n_args: dict[str, object] | None = None,
    ) -> None:
        cmd = SendCommand(
            chat_id=chat_id,
            i18n_key=i18n_key,
            i18n_args=i18n_args or {},
            reply_markup=reply_markup,
        )
        await self._sender.send(cmd, opts=PublishOptions(priority=priority))

    async def send_image(
        self,
        chat_id: int,
        image_url: str,
        priority: int,
        *,
        reply_markup: dict[str, object] | None = None,
        text: str | None = None,
    ) -> None:
        cmd = SendCommand(
            chat_id=chat_id,
            text=text,
            image_url=image_url,
            reply_markup=reply_markup,
        )
        await self._sender.send(cmd, opts=PublishOptions(priority=priority))

    async def send_image_i18n(
        self,
        chat_id: int,
        image_url: str,
        i18n_key: str,
        priority: int,
        *,
        reply_markup: dict[str, object] | None = None,
        i18n_args: dict[str, object] | None = None,
    ) -> None:
        cmd = SendCommand(
            chat_id=chat_id,
            image_url=image_url,
            i18n_key=i18n_key,
            i18n_args=i18n_args or {},
            reply_markup=reply_markup,
        )
        await self._sender.send(cmd, opts=PublishOptions(priority=priority))


async def create_amqp_client(
    url: str,
    queue_name: str = "tg-delivery",
    *,
    config: AmqpPublisherConfig | None = None,
) -> TgDeliveryClient:
    sender = AmqpCommandPublisher(url, queue_name, cfg=config)
    return TgDeliveryClient(sender)
