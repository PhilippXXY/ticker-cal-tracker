from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stock:
    name: str
    symbol: str
    last_updated: datetime
    current_price: float = None
    change_percent: float = None