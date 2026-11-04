from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Security(Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    sector: Mapped[str | None] = mapped_column(String(50))


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("security_id", "trade_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"))
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    high: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    low: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    close: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    volume: Mapped[int | None] = mapped_column(BigInteger)


class IndexLevel(Base):
    __tablename__ = "index_levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    index_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    level: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))