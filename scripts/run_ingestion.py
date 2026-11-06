import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.ingestion import fetch_prices
from app.loader import load_prices
from app.models import Security
from app.validation import validate_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ingestion")


def run(days: int = 60) -> None:
    end = date.today() + timedelta(days=1)  # end date is not included
    start = end - timedelta(days=days)

    with Session(engine) as session:
        symbols = list(session.scalars(select(Security.symbol).order_by(Security.symbol)))
        logger.info("Fetching %d symbols from %s to %s", len(symbols), start, end)

        raw = fetch_prices(symbols, start.isoformat(), end.isoformat())
        clean, issues = validate_prices(raw)
        saved = load_prices(session, clean)
        session.commit()

    logger.info(
        "Done: fetched %d rows, found %d issues, saved %d rows",
        len(raw),
        len(issues),
        saved,
    )


if __name__ == "__main__":
    run()
