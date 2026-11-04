from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Security

# Yahoo Finance uses ".NS" at the end for NSE stocks
STOCKS = [
    ("RELIANCE.NS", "Reliance Industries", "Energy"),
    ("TCS.NS", "Tata Consultancy Services", "IT"),
    ("HDFCBANK.NS", "HDFC Bank", "Financials"),
    ("INFY.NS", "Infosys", "IT"),
    ("ICICIBANK.NS", "ICICI Bank", "Financials"),
    ("HINDUNILVR.NS", "Hindustan Unilever", "FMCG"),
    ("ITC.NS", "ITC", "FMCG"),
    ("SBIN.NS", "State Bank of India", "Financials"),
    ("BHARTIARTL.NS", "Bharti Airtel", "Telecom"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank", "Financials"),
    ("LT.NS", "Larsen & Toubro", "Industrials"),
    ("AXISBANK.NS", "Axis Bank", "Financials"),
    ("ASIANPAINT.NS", "Asian Paints", "Consumer"),
    ("MARUTI.NS", "Maruti Suzuki", "Auto"),
    ("SUNPHARMA.NS", "Sun Pharmaceutical", "Pharma"),
    ("TITAN.NS", "Titan Company", "Consumer"),
    ("ULTRACEMCO.NS", "UltraTech Cement", "Materials"),
    ("BAJFINANCE.NS", "Bajaj Finance", "Financials"),
    ("WIPRO.NS", "Wipro", "IT"),
    ("NESTLEIND.NS", "Nestle India", "FMCG"),
]


def seed() -> None:
    with Session(engine) as session:
        added = 0
        for symbol, name, sector in STOCKS:
            exists = session.scalar(select(Security).where(Security.symbol == symbol))
            if exists is None:
                session.add(Security(symbol=symbol, name=name, sector=sector))
                added += 1
        session.commit()
        print(f"Added {added} new securities.")


if __name__ == "__main__":
    seed()