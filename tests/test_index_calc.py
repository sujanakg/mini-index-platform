from datetime import date, timedelta

import pandas as pd
import pytest

from app.index_calc import calculate_index


def make_prices(data: dict[str, list]) -> pd.DataFrame:
    rows = []
    for symbol, closes in data.items():
        for i, close in enumerate(closes):
            rows.append({"symbol": symbol, "trade_date": date(2026, 10, 1) + timedelta(days=i), "close": close})
    return pd.DataFrame(rows)


def test_first_day_equals_base_value():
    result = calculate_index(make_prices({"A": [100, 110], "B": [200, 200]}))
    assert result.loc[0, "level"] == 1000.0
    assert pd.isna(result.loc[0, "daily_return"])


def test_equal_weighted_return():
    result = calculate_index(make_prices({"A": [100, 110], "B": [200, 200]}))
    assert result.loc[1, "daily_return"] == pytest.approx(0.05)
    assert result.loc[1, "level"] == pytest.approx(1050.0)


def test_returns_compound_over_days():
    result = calculate_index(make_prices({"A": [100, 110, 121], "B": [200, 200, 200]}))
    assert result.loc[2, "level"] == pytest.approx(1102.5)


def test_missing_price_is_skipped():
    result = calculate_index(make_prices({"A": [100, None], "B": [200, 210]}))
    assert result.loc[1, "daily_return"] == pytest.approx(0.05)


def test_empty_input_returns_empty_result():
    empty = pd.DataFrame(columns=["symbol", "trade_date", "close"])
    assert calculate_index(empty).empty
