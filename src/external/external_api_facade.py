import logging
from .alpha_vantage import AlphaVantage
from .finnhub import Finnhub
from .yfinance_adapter import YFinanceAdapter
from src.models.stock_event_model import EventType, StockEvent
from src.models.stock_model import Stock

logger = logging.getLogger(__name__)


class ExternalApiFacade:
   
    def __init__(self):
        self.alpha_vantage = AlphaVantage()
        self.finnhub = Finnhub()
        self.yfinance = YFinanceAdapter()
    
    def getStockInfoFromName(self, *, name: str) -> Stock:

        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, got {type(name).__name__}")
        
        # Try Finnhub first (higher rate limit)
        finnhub_error = None
        try:
            logger.debug(f"Attempting to fetch stock by name '{name}' using Finnhub")
            return self.finnhub.getStockInfoFromName(name=name)
        except ValueError as e:
            finnhub_error = str(e)
            logger.warning(f"Finnhub lookup failed for name '{name}': {finnhub_error}")
            
        # Fallback to Alpha Vantage
        alpha_vantage_error = None
        try:
            logger.debug(f"Falling back to Alpha Vantage for name '{name}'")
            return self.alpha_vantage.getStockInfoFromName(name=name)
        except ValueError as e:
            alpha_vantage_error = str(e)
            logger.error(f"Alpha Vantage lookup also failed for name '{name}': {alpha_vantage_error}")
            error_msg = (
                f"Failed to fetch stock data for name '{name}' from all sources. "
                f"Finnhub: {finnhub_error}, Alpha Vantage: {alpha_vantage_error}"
            )
            raise ValueError(error_msg)
    
    def getStockInfoFromSymbol(self, *, symbol: str) -> Stock:
        if not isinstance(symbol, str):
            raise TypeError(f"Symbol must be a string, got {type(symbol).__name__}")
        
        # Try Finnhub first (higher rate limit)
        try:
            logger.debug(f"Attempting to fetch stock by symbol '{symbol}' using Finnhub")
            return self.finnhub.getStockInfoFromSymbol(symbol=symbol)
        except ValueError as e:
            logger.warning(f"Finnhub lookup failed for symbol '{symbol}': {str(e)}")
            
        # Fallback to Alpha Vantage
        try:
            logger.debug(f"Falling back to Alpha Vantage for symbol '{symbol}'")
            return self.alpha_vantage.getStockInfoFromSymbol(symbol=symbol)
        except ValueError as e:
            logger.error(f"Alpha Vantage lookup also failed for symbol '{symbol}': {str(e)}")
            raise ValueError(f"Failed to fetch stock data for symbol '{symbol}' from all sources")
    
    def getStockPrice(self, *, symbol: str) -> dict:
        # Try yfinance (Primary)
        try:
            return self.yfinance.getStockPrice(symbol=symbol)
        except Exception as e:
            logger.warning(f"yfinance price lookup failed for {symbol}: {e}")
            # Potential fallback to Finnhub here if we wanted to mix them
            raise ValueError(f"Failed to fetch stock price for {symbol}")
    
    def getStockEventDatesFromStock(self, *, stock: Stock, event_types: list[EventType]) -> list[StockEvent]:
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        if not isinstance(event_types, list):
            raise TypeError(f"event_types must be a list, got {type(event_types).__name__}")
        if not event_types:
            raise ValueError("event_types cannot be empty")
        
        # Alpha Vantage is the only provider for event data
        return self.alpha_vantage.getStockEventDatesFromStock(stock=stock, event_types=event_types)
