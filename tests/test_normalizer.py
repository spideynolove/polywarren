from signal_engine.normalizer import normalize_polymarket, normalize_kalshi


def test_normalize_polymarket_valid():
    raw = {"asset_id": "abc123", "price": "0.72", "timestamp": "1700000000000000000", "size": "100"}
    tick = normalize_polymarket(raw)
    assert tick is not None
    assert tick.symbol == "abc123"
    assert tick.venue == "polymarket"
    assert abs(tick.yes_price - 0.72) < 1e-6
    assert abs(tick.no_price - 0.28) < 1e-3


def test_normalize_polymarket_missing_price():
    raw = {"asset_id": "abc123"}
    tick = normalize_polymarket(raw)
    assert tick is not None
    assert tick.yes_price == 0.0


def test_normalize_polymarket_bad_data():
    tick = normalize_polymarket({"price": "not_a_number"})
    assert tick is None


def test_normalize_kalshi_valid():
    raw = {"market_ticker": "KXBTC-25", "yes_price": "72"}
    tick = normalize_kalshi(raw)
    assert tick is not None
    assert tick.symbol == "KXBTC-25"
    assert tick.venue == "kalshi"
    assert abs(tick.yes_price - 0.72) < 1e-6


def test_normalize_kalshi_bad_data():
    tick = normalize_kalshi({"yes_price": "abc"})
    assert tick is None
