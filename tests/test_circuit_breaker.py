from execution.circuit_breaker import CircuitBreaker


def test_rate_limit_allows_within_limit():
    cb = CircuitBreaker()
    for _ in range(10):
        assert cb.check_rate_limit("polymarket") is True


def test_rate_limit_blocks_over_limit():
    cb = CircuitBreaker()
    for _ in range(10):
        cb.check_rate_limit("polymarket")
    assert cb.check_rate_limit("polymarket") is False


def test_loss_threshold_halts():
    cb = CircuitBreaker()
    assert cb.check_loss_threshold(-50.0) is True
    assert cb.check_loss_threshold(-101.0) is False
    assert cb.halted is True


def test_reset_clears_halt():
    cb = CircuitBreaker()
    cb.check_loss_threshold(-200.0)
    assert cb.halted is True
    cb.reset()
    assert cb.halted is False
