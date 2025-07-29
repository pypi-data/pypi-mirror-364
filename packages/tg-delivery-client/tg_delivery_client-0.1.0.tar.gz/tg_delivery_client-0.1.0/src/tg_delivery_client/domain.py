from dataclasses import dataclass, field


@dataclass(slots=True)
class SendCommand:
    chat_id: int
    text: str | None = None
    i18n_key: str | None = None
    i18n_args: dict[str, object] = field(default_factory=dict)
    reply_markup: dict[str, object] | None = None
    image_url: str | None = None

