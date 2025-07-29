from collections.abc import Mapping
from dataclasses import dataclass, field

from .retry import RetryPolicy
from .serializers import CommandSerializer, JsonCommandSerializer


@dataclass(slots=True)
class PublishOptions:
    priority: int
    headers: Mapping[str, object] | None = None


@dataclass(slots=True)
class AmqpPublisherConfig:
    ensure_queue: bool = True
    max_priority: int = 10
    serializer: CommandSerializer = field(default_factory=JsonCommandSerializer)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
