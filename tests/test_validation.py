import logging
from datetime import date, timedelta

import pandas as pd
import pytest

from app.validation import validate_prices


def make_df(closes_by_symbol: dict[str, list]) -> pd.DataFrame:
    """Build a small price table. Every price column gets the same value."""
    rows = []
    for symbol, closes in closes_by_symbol.items():
        for i, close in enumerate(closes):
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": date(2026, 10, 1) + timedelta(days=i),
                    "open": close,
                    "high": close,
                    "low": close,
                    "close": close,
                    "volume": 1000,
                }
            )
    return pd.DataFrame(rows)


def test_clean_data_has_no_issues() -> None:
    clean, issues = validate_prices(make_df({"TCS.NS": [100, 101, 102]}))
    assert issues == []
    assert len(clean) == 3


def test_missing_close_is_rejected() -> None:
    clean, issues = validate_prices(make_df({"TCS.NS": [100, None, 101]}))
    assert [i.check for i in issues] == ["missing_price"]
    assert len(clean) == 2


def test_negative_price_is_rejected() -> None:
    clean, issues = validate_prices(make_df({"TCS.NS": [100, -5]}))
    assert [i.check for i in issues] == ["non_positive_price"]
    assert len(clean) == 1


def test_zero_price_is_rejected() -> None:
    clean, issues = validate_prices(make_df({"TCS.NS": [100, 0]}))
    assert [i.check for i in issues] == ["non_positive_price"]
    assert len(clean) == 1


def test_big_jump_is_flagged_but_kept() -> None:
    clean, issues = validate_prices(make_df({"TCS.NS": [100, 130]}))
    assert [i.check for i in issues] == ["big_jump"]
    assert issues[0].symbol == "TCS.NS"
    assert len(clean) == 2  # flagged for review, not deleted


def test_move_below_threshold_is_not_flagged() -> None:
    _, issues = validate_prices(make_df({"TCS.NS": [100, 119]}))  # +19%
    assert issues == []


def test_jumps_are_checked_per_stock_not_across_stocks() -> None:
    # A and B have very different price levels, but each moves only about 1%
    _, issues = validate_prices(make_df({"A": [100, 101], "B": [5000, 5050]}))
    assert issues == []


def test_missing_price_does_not_create_a_fake_jump() -> None:
    _, issues = validate_prices(make_df({"TCS.NS": [100, None, 101]}))
    assert "big_jump" not in [i.check for i in issues]


def test_issues_are_logged(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        validate_prices(make_df({"TCS.NS": [100, None]}))
    assert "missing_price" in caplog.text
    assert "TCS.NS" in caplog.text