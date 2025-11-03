import logging
from external.alpha_vantage import AlphaVantage
from external.finnhub import Finnhub
from models.stock_event_model import EventType, StockEvent
from models.stock_model import Stock

logger = logging.getLogger(__name__)


class ExternalApiFacade:
    '''
    Unified facade for external financial data APIs.
    
    Provides a single interface to retrieve stock information and event data
    from multiple external providers. Automatically handles fallback logic
    between APIs based on availability and rate limits.
    
    Priority:
    - Stock lookups: Finnhub (primary) -> Alpha Vantage (fallback)
    - Event data: Alpha Vantage (only provider)
    '''
    
    def __init__(self):
        '''
        Initialize facade with API clients.
        
        Raises:
            ValueError: If required API keys are missing from environment
        '''
        self.alpha_vantage = AlphaVantage()
        self.finnhub = Finnhub()
    
    def getStockInfoFromName(self, *, name: str) -> Stock:
        '''
        Retrieve stock information by company name.
        
        Uses Finnhub as primary source with Alpha Vantage fallback.
        
        Args:
            name: Company name to search for (e.g., 'Apple Inc')
            
        Returns:
            Stock object with company information
            
        Raises:
            TypeError: If name is not a string
            ValueError: If name is invalid or no matches found in any API
        '''
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
        '''
        Retrieve stock information by ticker symbol.
        
        Uses Finnhub as primary source with Alpha Vantage fallback.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            Stock object with company information
            
        Raises:
            TypeError: If symbol is not a string
            ValueError: If symbol is invalid or no data found in any API
        '''
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
    
    def getStockEventDatesFromStock(self, *, stock: Stock, event_types: list[EventType]) -> list[StockEvent]:
        '''
        Retrieve stock events for a given stock and event types.
        
        Only Alpha Vantage provides event data (earnings, dividends, splits).
        
        Args:
            stock: Stock object to get events for
            event_types: List of EventType enums to fetch
            
        Returns:
            List of StockEvent objects matching the requested event types
            
        Raises:
            TypeError: If stock is not a Stock object or event_types is not a list
            ValueError: If event_types is empty, contains invalid types, or API request fails
        '''
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        if not isinstance(event_types, list):
            raise TypeError(f"event_types must be a list, got {type(event_types).__name__}")
        if not event_types:
            raise ValueError("event_types cannot be empty")
        
        # Alpha Vantage is the only provider for event data
        return self.alpha_vantage.getStockEventDatesFromStock(stock=stock, event_types=event_types)