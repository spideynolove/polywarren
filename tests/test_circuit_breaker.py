import pytest
from execution.circuit_breaker import CircuitBreaker


@pytest.mark.anyio
async def test_rate_limit_allows_within_limit():
    cb = CircuitBreaker()
    for _ in range(10):
        assert await cb.check_rate_limit("polymarket") is True


@pytest.mark.anyio
async def test_rate_limit_blocks_over_limit():
    cb = CircuitBreaker()
    for _ in range(10):
        await cb.check_rate_limit("polymarket")
    assert await cb.check_rate_limit("polymarket") is False


@pytest.mark.anyio
async def test_rate_limit_unknown_venue_tracks():
    cb = CircuitBreaker()
    for _ in range(10):
        await cb.check_rate_limit("unknown_venue")
    assert await cb.check_rate_limit("unknown_venue") is False


def test_loss_threshold_allows_above_threshold():
    cb = CircuitBreaker()
    assert cb.check_loss_threshold(-50.0) is True
    assert cb.halted is False


def test_loss_threshold_halts_at_threshold():
    cb = CircuitBreaker()
    assert cb.check_loss_threshold(-100.0) is False
    assert cb.halted is True


def test_loss_threshold_halts_below_threshold():
    cb = CircuitBreaker()
    assert cb.check_loss_threshold(-200.0) is False
    assert cb.halted is True


def test_reset_clears_halt():
    cb = CircuitBreaker()
    cb.check_loss_threshold(-200.0)
    assert cb.halted is True
    cb.reset()
    assert cb.halted is False
