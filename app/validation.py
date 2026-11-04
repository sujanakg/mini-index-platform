import logging
from dataclasses import dataclass
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)

MAX_DAILY_MOVE = 0.20  # 20%
PRICE_COLUMNS = ["open", "high", "low", "close"]


@dataclass
class Issue:
    symbol: str
    trade_date: date
    check: str
    detail: str


def validate_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, list[Issue]]:
    """Check prices. Returns (clean rows, list of issues found)."""
    df = df.sort_values(["symbol", "trade_date"]).reset_index(drop=True)
    issues: list[Issue] = []

    # Check 1: missing close price
    missing = df["close"].isna()
    for row in df[missing].itertuples():
        issues.append(Issue(row.symbol, row.trade_date, "missing_price", "close is missing"))

    # Check 2: zero or negative prices
    non_positive = (df[PRICE_COLUMNS] <= 0).any(axis=1)
    for row in df[non_positive].itertuples():
        issues.append(Issue(row.symbol, row.trade_date, "non_positive_price", "price is zero or negative"))

    # Remove the rejected rows
    clean = df[~(missing | non_positive)].copy()

    # Check 3: big jumps (flag only, keep the row)
    change = clean.groupby("symbol")["close"].pct_change()
    for idx in clean[change.abs() > MAX_DAILY_MOVE].index:
        row = clean.loc[idx]
        issues.append(
            Issue(row["symbol"], row["trade_date"], "big_jump", f"close moved {change[idx]:.1%}")
        )

    for issue in issues:
        logger.warning("%s | %s | %s | %s", issue.check, issue.symbol, issue.trade_date, issue.detail)

    return clean, issues