from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stock:
    isin: str
    name: str
    symbol: str
    last_updated: datetime
    