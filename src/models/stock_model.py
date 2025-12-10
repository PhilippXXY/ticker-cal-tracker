from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stock:
    name: str
    symbol: str
    last_updated: datetime
    