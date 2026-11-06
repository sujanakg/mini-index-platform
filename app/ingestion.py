import pandas as pd
import yfinance as yf


def fetch_prices(symbols: list[str], start: str, end: str) -> pd.DataFrame:
    """Download daily prices for the given symbols.

    start and end are 'YYYY-MM-DD'. The end date is NOT included.
    Returns one row per stock per day.
    """
    raw = yf.download(
        symbols,
        start=start,
        end=end,
        group_by="ticker",
        auto_adjust=False,
        progress=False,
    )

    frames = []
    for symbol in symbols:
        one_stock = raw[symbol].reset_index()
        one_stock["symbol"] = symbol
        frames.append(one_stock)

    df = pd.concat(frames, ignore_index=True)
    df = df.rename(
        columns={
            "Date": "trade_date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df[["symbol", "trade_date", "open", "high", "low", "close", "volume"]]
