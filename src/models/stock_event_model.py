from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.models.stock_model import Stock

class EventType(str, Enum):
    EARNINGS_ANNOUNCEMENT = "EARNINGS_ANNOUNCEMENT"
    DIVIDEND_EX = "DIVIDEND_EX"
    DIVIDEND_DECLARATION = "DIVIDEND_DECLARATION"
    DIVIDEND_RECORD = "DIVIDEND_RECORD"
    DIVIDEND_PAYMENT = "DIVIDEND_PAYMENT"
    STOCK_SPLIT = "STOCK_SPLIT"
    
    @property
    def db_column(self) -> str:
        '''
        Get the corresponding database column name for this event type.
        '''
        column_mapping = {
            EventType.EARNINGS_ANNOUNCEMENT: "include_earnings_announcement",
            EventType.DIVIDEND_EX: "include_dividend_ex",
            EventType.DIVIDEND_DECLARATION: "include_dividend_declaration",
            EventType.DIVIDEND_RECORD: "include_dividend_record",
            EventType.DIVIDEND_PAYMENT: "include_dividend_payment",
            EventType.STOCK_SPLIT: "include_stock_split"
        }
        return column_mapping[self]
    
@dataclass
class StockEvent:
    stock: Stock
    type: EventType
    date: datetime
    last_updated: datetime
    source: str
    
    
