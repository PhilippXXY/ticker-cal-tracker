from dataclasses import dataclass
from datetime import datetime
import json
from enum import Enum

class EventType(str, Enum):
    SPLIT = "SPLIT"
    SHAREHOLDER_MEETING = "SHAREHOLDER_MEETING"
    EX_DIVIDEND = "EX_DIVIDEND"
    CUM_DIVIDEND = "CUM_DIVIDEND"
    
@dataclass
class StockEvent:
    id: int
    type: EventType
    date: datetime
    last_updated: datetime
    source: str
    
    