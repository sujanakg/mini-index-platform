import logging

from sqlalchemy.orm import Session

from app.database import engine
from app.index_service import rebuild_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("index")


def run() -> None:
    with Session(engine) as session:
        saved = rebuild_index(session)
        session.commit()
    logger.info("Index rebuilt: %d daily levels saved", saved)


if __name__ == "__main__":
    run()