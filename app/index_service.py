import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.index_calc import calculate_index
from app.models import DailyPrice, IndexLevel, Security


def read_close_prices(session: Session) -> pd.DataFrame:
    """Read all closing prices from Postgres as symbol, trade_date, close."""
    rows = session.execute(
        select(Security.symbol, DailyPrice.trade_date, DailyPrice.close)
        .join(DailyPrice, DailyPrice.security_id == Security.id)
        .where(DailyPrice.close.is_not(None))
    ).all()
    df = pd.DataFrame(rows, columns=["symbol", "trade_date", "close"])
    df["close"] = df["close"].astype(float)
    return df


def save_index_levels(session: Session, levels: pd.DataFrame) -> int:
    """Save index levels. Existing dates are updated, not duplicated."""
    if levels.empty:
        return 0

    rows = [
        {
            "index_date": r.index_date,
            "level": round(float(r.level), 4),
            "daily_return": None if pd.isna(r.daily_return) else round(float(r.daily_return), 6),
        }
        for r in levels.itertuples()
    ]

    stmt = insert(IndexLevel).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["index_date"],
        set_={"level": stmt.excluded.level, "daily_return": stmt.excluded.daily_return},
    )
    session.execute(stmt)
    return len(rows)


def rebuild_index(session: Session) -> int:
    """Read prices, calculate the index, save it. Returns rows saved."""
    prices = read_close_prices(session)
    levels = calculate_index(prices)
    return save_index_levels(session, levels)