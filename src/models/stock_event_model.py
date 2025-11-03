from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from models.stock_model import Stock

class EventType(str, Enum):
    EARNINGS_ANNOUNCEMENT = "EARNINGS_ANNOUNCEMENT"
    DIVIDEND_EX = "DIVIDEND_EX"
    DIVIDEND_DECLARATION = "DIVIDEND_DECLARATION"
    DIVIDEND_RECORD = "DIVIDEND_RECORD"
    DIVIDEND_PAYMENT = "DIVIDEND_PAYMENT"
    STOCK_SPLIT = "STOCK_SPLIT"
    
@dataclass
class StockEvent:
    stock: Stock
    type: EventType
    date: datetime
    last_updated: datetime
    source: str
    
    