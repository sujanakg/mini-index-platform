import pandas as pd

BASE_VALUE = 1000.0


def calculate_index(prices: pd.DataFrame, base_value: float = BASE_VALUE) -> pd.DataFrame:
    """Equal-weighted index.

    prices needs the columns: symbol, trade_date, close.
    Returns one row per date with: index_date, level, daily_return.
    """
    if prices.empty:
        return pd.DataFrame(columns=["index_date", "level", "daily_return"])

    # One column per stock, one row per date
    wide = prices.pivot(index="trade_date", columns="symbol", values="close").sort_index()

    # Each stock's daily return, then the average across stocks
    stock_returns = wide.pct_change(fill_method=None)
    index_returns = stock_returns.mean(axis=1)  # first day is NaN (no previous day)

    # Chain the returns together, starting from the base value
    levels = base_value * (1 + index_returns.fillna(0)).cumprod()

    return pd.DataFrame(
        {
            "index_date": wide.index,
            "level": levels.to_numpy(),
            "daily_return": index_returns.to_numpy(),
        }
    )
