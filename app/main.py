import logging
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import DailyPrice, IndexLevel, Security
from app.schemas import IndexLevelOut, PriceOut, SecurityOut

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("api")

app = FastAPI(title="Mini Index Data Platform", version="0.1.0")


def _check_range(from_date: date | None, to_date: date | None) -> None:
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="'from' must not be after 'to'")


def _get_security(db: Session, symbol: str) -> Security:
    security = db.scalar(select(Security).where(Security.symbol == symbol.upper()))
    if security is None:
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    return security


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check that the API is running and can reach the database."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check failed: database unreachable")
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "database": "up"}


@app.get("/constituents", response_model=list[SecurityOut])
def constituents(db: Session = Depends(get_db)) -> list[Security]:
    """List the stocks that make up the index."""
    return list(db.scalars(select(Security).order_by(Security.symbol)))


@app.get("/prices/{symbol}", response_model=list[PriceOut])
def prices(
    symbol: str,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
) -> list[DailyPrice]:
    """Daily prices for one stock, optionally between two dates."""
    _check_range(from_date, to_date)
    security = _get_security(db, symbol)

    stmt = select(DailyPrice).where(DailyPrice.security_id == security.id)
    if from_date:
        stmt = stmt.where(DailyPrice.trade_date >= from_date)
    if to_date:
        stmt = stmt.where(DailyPrice.trade_date <= to_date)
    return list(db.scalars(stmt.order_by(DailyPrice.trade_date)))


@app.get("/index/latest", response_model=IndexLevelOut)
def index_latest(db: Session = Depends(get_db)) -> IndexLevel:
    """The most recent index level."""
    latest = db.scalar(select(IndexLevel).order_by(IndexLevel.index_date.desc()).limit(1))
    if latest is None:
        raise HTTPException(status_code=404, detail="No index data yet")
    return latest


@app.get("/index/history", response_model=list[IndexLevelOut])
def index_history(
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
) -> list[IndexLevel]:
    """Index levels over time, optionally between two dates."""
    _check_range(from_date, to_date)

    stmt = select(IndexLevel)
    if from_date:
        stmt = stmt.where(IndexLevel.index_date >= from_date)
    if to_date:
        stmt = stmt.where(IndexLevel.index_date <= to_date)
    return list(db.scalars(stmt.order_by(IndexLevel.index_date)))