import time
import structlog
from collections import deque
from execution.config import MAX_LOSS_THRESHOLD, MAX_ORDERS_PER_MINUTE_POLYMARKET, MAX_ORDERS_PER_MINUTE_KALSHI

log = structlog.get_logger()


class CircuitBreaker:
    def __init__(self) -> None:
        self._halted = False
        self._order_timestamps: dict[str, deque[float]] = {
            "polymarket": deque(),
            "kalshi": deque(),
        }
        self._rate_limits = {
            "polymarket": MAX_ORDERS_PER_MINUTE_POLYMARKET,
            "kalshi": MAX_ORDERS_PER_MINUTE_KALSHI,
        }

    def check_rate_limit(self, venue: str) -> bool:
        now = time.monotonic()
        window = self._order_timestamps.get(venue, deque())
        while window and now - window[0] > 60:
            window.popleft()
        limit = self._rate_limits.get(venue, 10)
        if len(window) >= limit:
            log.warning("rate_limit_exceeded", venue=venue, count=len(window), limit=limit)
            return False
        window.append(now)
        return True

    def check_loss_threshold(self, current_pnl: float) -> bool:
        if current_pnl <= MAX_LOSS_THRESHOLD:
            self._halted = True
            log.error("circuit_breaker_halt", current_pnl=current_pnl, threshold=MAX_LOSS_THRESHOLD)
            return False
        return True

    @property
    def halted(self) -> bool:
        return self._halted

    def reset(self) -> None:
        self._halted = False
        log.info("circuit_breaker_reset")


circuit_breaker = CircuitBreaker()
