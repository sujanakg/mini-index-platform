from collections.abc import Iterator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.deps import get_db
from app.main import app
from app.models import DailyPrice, IndexLevel, Security


@pytest.fixture()
def client() -> Iterator[TestClient]:
    # A fresh temporary database in memory
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    # Known sample data
    with Session(engine) as session:
        tcs = Security(symbol="TCS.NS", name="Tata Consultancy Services", sector="IT")
        infy = Security(symbol="INFY.NS", name="Infosys", sector="IT")
        session.add_all([tcs, infy])
        session.flush()

        tcs_closes = [Decimal("100.00"), Decimal("110.00"), Decimal("121.00")]
        for day, close in zip((1, 2, 3), tcs_closes):
            session.add(DailyPrice(security_id=tcs.id, trade_date=date(2026, 10, day), close=close))
            session.add(DailyPrice(security_id=infy.id, trade_date=date(2026, 10, day), close=Decimal("200.00")))

        session.add_all(
            [
                IndexLevel(index_date=date(2026, 10, 1), level=Decimal("1000.0000"), daily_return=None),
                IndexLevel(index_date=date(2026, 10, 2), level=Decimal("1050.0000"), daily_return=Decimal("0.050000")),
                IndexLevel(index_date=date(2026, 10, 3), level=Decimal("1102.5000"), daily_return=Decimal("0.050000")),
            ]
        )
        session.commit()

    # Make the API use this temporary database instead of the real one
    def override_get_db() -> Iterator[Session]:
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()