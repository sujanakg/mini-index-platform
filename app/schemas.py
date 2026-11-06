from datetime import date

from pydantic import BaseModel, ConfigDict


class SecurityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    name: str
    sector: str | None


class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None


class IndexLevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    index_date: date
    level: float
    daily_return: float | None
