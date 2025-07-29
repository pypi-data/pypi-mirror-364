import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetryPolicy:
    __slots__ = ("_rnd", "attempts", "base_delay", "jitter", "max_delay", "multiplier")

    def __init__(
        self,
        attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 5.0,
        multiplier: float = 2.0,
        *,
        jitter: bool = True,
    ) -> None:
        self.attempts = attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self._rnd = random.SystemRandom()

    async def run(self, fn: Callable[[], Awaitable[T]]) -> T:
        delay = self.base_delay
        last_exc: Exception | None = None

        for attempt in range(self.attempts):
            try:
                return await fn()
            except Exception as exc:  # noqa: BLE001 — осознанный catch
                last_exc = exc
                if attempt == self.attempts - 1:
                    break

                sleep_for, delay = self._next_sleep_and_delay(delay)
                await asyncio.sleep(sleep_for)

        if last_exc is None:
            raise RuntimeError("RetryPolicy finished without result or exception")
        raise last_exc

    def _next_sleep_and_delay(self, current_delay: float) -> tuple[float, float]:
        next_delay = self._next_delay(current_delay)
        sleep_for = self._pick_sleep(next_delay if self.jitter else current_delay)
        return sleep_for, next_delay

    def _next_delay(self, current: float) -> float:
        return min(self.max_delay, current * self.multiplier)

    def _pick_sleep(self, delay: float) -> float:
        if self.jitter:
            return self._rnd.uniform(delay / 2, delay)
        return delay
