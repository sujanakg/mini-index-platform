import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import DailyPrice, Security


def _price(value: float) -> float | None:
    return None if pd.isna(value) else round(float(value), 2)


def load_prices(session: Session, df: pd.DataFrame) -> int:
    """Save clean prices into daily_prices. Returns how many rows were saved."""
    if df.empty:
        return 0

    # Map each symbol to its id in the securities table
    ids = dict(session.execute(select(Security.symbol, Security.id)).all())

    rows = [
        {
            "security_id": ids[r.symbol],
            "trade_date": r.trade_date,
            "open": _price(r.open),
            "high": _price(r.high),
            "low": _price(r.low),
            "close": _price(r.close),
            "volume": None if pd.isna(r.volume) else int(r.volume),
        }
        for r in df.itertuples()
    ]

    stmt = insert(DailyPrice).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["security_id", "trade_date"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
        },
    )
    session.execute(stmt)
    return len(rows)