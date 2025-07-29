from typing import Protocol

from .domain import SendCommand
from .options import PublishOptions


class CommandSender(Protocol):
    async def send(self, cmd: SendCommand, *, opts: PublishOptions) -> None: ...
