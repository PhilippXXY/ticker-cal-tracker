import logging
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.external.external_base import ExternalApiBaseDefinition
from src.models.stock_model import Stock
from src.models.stock_event_model import StockEvent, EventType

logger = logging.getLogger(__name__)

class Finnhub(ExternalApiBaseDefinition):
    '''
    Mock implementation replacing Finnhub API.
    '''
    
    def __init__(self):
        '''
        Initialize the Mock API client.
        '''
        # No API key needed for mock
        self.api_key = None
        self.client = None

    def getStockInfoFromSymbol(self, *, symbol: str) -> Stock:
        '''
        Get mock stock information by symbol.
        '''
        return Stock(
            name=f"{symbol} (Mock)",
            symbol=symbol,
            last_updated=datetime.now(timezone.utc)
        )

    def getStockInfoFromName(self, *, name: str) -> Stock:
        '''
        Get mock stock information by name.
        '''
        # Simple mock logic: use name as symbol (truncated)
        symbol = name[:4].upper()
        return Stock(
            name=name,
            symbol=symbol,
            last_updated=datetime.now(timezone.utc)
        )

    def getStockEventDatesFromStock(self, *, stock: Stock, event_types: List[EventType]) -> List[StockEvent]:
        '''
        Get mock stock events.
        '''
        return []

    def get_quote(self, *, symbol: str) -> Optional[Dict[str, Any]]:
        '''
        Get mock quote data.
        '''
        # Generate random mock price
        base_price = random.uniform(100, 200)
        change = random.uniform(-5, 5)
        percent_change = (change / base_price) * 100
        
        return {
            'c': round(base_price, 2),
            'd': round(change, 2),
            'dp': round(percent_change, 2),
            'h': round(base_price + 5, 2),
            'l': round(base_price - 5, 2),
            'o': round(base_price - 2, 2),
            'pc': round(base_price - change, 2),
            't': int(datetime.now().timestamp())
        }
