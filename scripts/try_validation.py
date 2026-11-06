import logging
from datetime import date

import pandas as pd

from app.validation import validate_prices

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

prices = [100, None, -5, 200]
df = pd.DataFrame(
    {
        "symbol": ["TCS.NS"] * 4,
        "trade_date": [date(2026, 10, d) for d in (26, 27, 28, 29)],
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [1000] * 4,
    }
)

clean, issues = validate_prices(df)
print(clean[["symbol", "trade_date", "close"]])
print("Issues found:", len(issues))
