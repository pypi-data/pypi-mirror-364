import json
from typing import Protocol

from .domain import SendCommand


class CommandSerializer(Protocol):
    @property
    def content_type(self) -> str: ...
    @property
    def content_encoding(self) -> str: ...
    def serialize(self, cmd: SendCommand) -> bytes: ...


class JsonCommandSerializer:
    __slots__ = ()

    @property
    def content_type(self) -> str:
        return "application/json"

    @property
    def content_encoding(self) -> str:
        return "utf-8"

    @staticmethod
    def serialize(cmd: SendCommand) -> bytes:
        return json.dumps(
            {
                "chat_id": cmd.chat_id,
                "text": cmd.text,
                "i18n_key": cmd.i18n_key,
                "i18n_args": cmd.i18n_args,
                "reply_markup": cmd.reply_markup,
                "image_url": cmd.image_url,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
