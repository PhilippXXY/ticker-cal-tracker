import csv
import json
import logging
import requests
from datetime import datetime, timezone
from .external_base import ExternalApiBaseDefinition
from src.models.stock_model import Stock
from src.models.stock_event_model import StockEvent, EventType

logger = logging.getLogger(__name__)

class AlphaVantage(ExternalApiBaseDefinition):
    '''
    Alpha Vantage API client for retrieving stock information and event data.
    
    Implementation of financial data API using Alpha Vantage's REST endpoints.
    Supports stock lookup, earnings calendars, dividend information, and stock splits.
    
    API documentation: https://www.alphavantage.co/documentation/
    '''
    
    def __init__(self):
        '''
        Initialize Alpha Vantage client with API key from environment.
        
        Raises:
            ValueError: If API key is not found in environment variables.
        '''
        super().__init__(api_key_name='API_KEY_ALPHA_VANTAGE')
        
        # Define the source of the API calls for logging purposes
        self.source = self.__class__.__name__
       
    def getStockInfoFromName(self, *, name: str) -> Stock:
        '''
        Retrieve stock information by company name.
        
        Searches for companies matching the name and returns details
        for the best match found.
        
        Args:
            name: Company name to search for (e.g., 'Apple Inc')
            
        Returns:
            Stock object with company information
            
        Raises:
            ValueError: If name is invalid or no matches found
            TypeError: If name is not a string
        '''
        # Type checking
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, got {type(name).__name__}")
       
        if name and len(name.strip()) > 0:
            try:
                function = "SYMBOL_SEARCH"
                
                url = f'https://www.alphavantage.co/query?function={function}&keywords={name}&apikey={self.api_key}'
                data = requests.get(url)
                data.raise_for_status()  # Raise exception for bad HTTP status codes
                results = data.json()
                
                # Check for rate limit or error messages from Alpha Vantage
                if 'Information' in results or 'Note' in results or 'Error Message' in results:
                    error_msg = results.get('Information') or results.get('Note') or results.get('Error Message')
                    raise ValueError(f"Alpha Vantage API error: {error_msg}")
                
                if 'bestMatches' in results and len(results['bestMatches']) > 0:
                    # Take the first (best) match
                    first_match = results['bestMatches'][0]
                    stock_symbol = first_match.get('1. symbol', '').upper()
                    stock_name = first_match.get('2. name', '')
                    
                    if stock_symbol and stock_name:
                        return Stock(
                            name=stock_name,
                            symbol=stock_symbol,
                            last_updated=datetime.now(timezone.utc)
                        )
                    else:
                        raise ValueError(f"Invalid data in search results for name: {name}")
                else:
                    raise ValueError(f"No stocks found for name: {name}")
                    
            except requests.RequestException as e:
                raise ValueError(f"Network error fetching stock data for name '{name}': {str(e)}") from e
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON response for name '{name}': {str(e)}") from e
            except Exception as e:
                raise ValueError(f"Unexpected error fetching stock data for name '{name}': {str(e)}") from e
        else:
            raise ValueError(f"Invalid name provided: {name}")
    
    def getStockInfoFromSymbol(self, *, symbol: str) -> Stock:
        '''
        Retrieve stock information by ticker symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            Stock object with company information
            
        Raises:
            ValueError: If symbol is invalid or no data found
            TypeError: If symbol is not a string
        '''
        # Type checking
        if not isinstance(symbol, str):
            raise TypeError(f"Symbol must be a string, got {type(symbol).__name__}")
            
        if symbol and len(symbol) > 0:
            try:
                function = "SYMBOL_SEARCH"
                
                url = f'https://www.alphavantage.co/query?function={function}&keywords={symbol}&apikey={self.api_key}'
                data = requests.get(url)
                data.raise_for_status()  # Raise exception for bad HTTP status codes
                results = data.json()
                
                # Check for rate limit or error messages from Alpha Vantage
                if 'Information' in results or 'Note' in results or 'Error Message' in results:
                    error_msg = results.get('Information') or results.get('Note') or results.get('Error Message')
                    raise ValueError(f"Alpha Vantage API error: {error_msg}")
                
                if 'bestMatches' in results and len(results['bestMatches']) > 0:
                    # Find exact symbol match or take the first result
                    match = None
                    for item in results['bestMatches']:
                        if item.get('1. symbol', '').upper() == symbol.upper():
                            match = item
                            break
                    
                    # If no exact match, take the first result
                    if not match:
                        match = results['bestMatches'][0]
                    
                    stock_symbol = match.get('1. symbol', '').upper()
                    stock_name = match.get('2. name', '')
                    
                    if stock_symbol and stock_name:
                        return Stock(
                            name=stock_name,
                            symbol=stock_symbol,
                            last_updated=datetime.now(timezone.utc)
                        )
                    else:
                        raise ValueError(f"Invalid data in search results for symbol: {symbol}")
                else:
                    raise ValueError(f"No stock data found for symbol: {symbol}")
                    
            except Exception as e:
                raise ValueError(f"Error fetching stock data for symbol {symbol}: {str(e)}")
        else:
            raise ValueError(f"Invalid symbol provided: {symbol}") 
        
        
        
              
    def getStockEventDatesFromStock(self, *, stock: Stock, event_types: list[EventType]) -> list[StockEvent]:
        '''
        Retrieve stock events for a given stock and event types.
        
        Fetches earnings announcements, dividend events, and stock splits
        based on the requested event types.
        
        Args:
            stock: Stock object to get events for
            event_types: List of EventType enums to fetch (e.g., EARNINGS_ANNOUNCEMENT, DIVIDEND_EX)
            
        Returns:
            List of StockEvent objects matching the requested event types
            
        Raises:
            TypeError: If stock is not a Stock object or event_types is not a list
            ValueError: If event_types is empty or contains invalid types
        '''
        # Type checking
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        if not isinstance(event_types, list):
            raise TypeError(f"event_types must be a list, got {type(event_types).__name__}")
        if not event_types:
            raise ValueError("event_types cannot be empty")
        
        # Validate all items in event_types are EventType enums
        for event_type in event_types:
            if not isinstance(event_type, EventType):
                raise TypeError(f"All event_types must be EventType enums, got {type(event_type).__name__}")
        
        result_items = []
        
        # Check for earnings
        if EventType.EARNINGS_ANNOUNCEMENT in event_types:
            result_items.extend(self._getEarningsAnnouncementsFromStock(stock=stock))
        
        # As the method returns a list of more than one EventType we have to delete them if necessary
        dividend_types = {EventType.DIVIDEND_EX, EventType.DIVIDEND_DECLARATION, EventType.DIVIDEND_RECORD, EventType.DIVIDEND_PAYMENT}
        if any(event_type in dividend_types for event_type in event_types):
            all_dividend_events = self._getDividendsFromStock(stock=stock)
            # Filter to only include requested dividend types
            filtered_dividends = [event for event in all_dividend_events
                                  if event.type in event_types]
            result_items.extend(filtered_dividends)
            
        # Check for stock splits
        if EventType.STOCK_SPLIT in event_types:
            result_items.extend(self._getSplitsFromStock(stock=stock))
        
        return result_items
        
    def _getEarningsAnnouncementsFromStock(self, *, stock: Stock) -> list[StockEvent]:
        '''
        Fetch earnings announcement events for a stock.
        
        Uses Alpha Vantage's EARNINGS_CALENDAR API to retrieve upcoming
        and recent earnings report dates for the next 12 months.
        
        Args:
            stock: Stock object to get earnings for
            
        Returns:
            List of StockEvent objects with EARNINGS_ANNOUNCEMENT type
            
        Raises:
            TypeError: If stock is not a Stock object
            ValueError: If API request fails or returns invalid data
        '''
        # Type checking
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        
        function = "EARNINGS_CALENDAR"
        symbol = stock.symbol.upper()
        horizon = "12month"
        result_items = []
        
        try:
            url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&horizon={horizon}&apikey={self.api_key}'
            
            with requests.Session() as s:
                download = s.get(url)
                download.raise_for_status()  # Raise exception for bad status codes
                decoded_content = download.content.decode('utf-8')
                
                # Check if response is JSON error message instead of CSV
                if decoded_content.strip().startswith('{'):
                    error_response = json.loads(decoded_content)
                    if 'Information' in error_response or 'Note' in error_response or 'Error Message' in error_response:
                        error_msg = error_response.get('Information') or error_response.get('Note') or error_response.get('Error Message')
                        raise ValueError(f"Alpha Vantage API error: {error_msg}")
                
                data = csv.DictReader(decoded_content.splitlines(), delimiter=',')

                for row in data:
                    # Match symbol to ensure correct data
                    if row.get("symbol") == symbol:
                        date_str = row.get("reportDate")
                        if date_str:
                            try:
                                # Parse date string to datetime object
                                date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                                result_items.append(
                                    StockEvent(
                                        stock=stock,
                                        type=EventType.EARNINGS_ANNOUNCEMENT,
                                        date=date,
                                        last_updated=datetime.now(timezone.utc),
                                        source=self.source
                                    )
                                )
                            except ValueError as e:
                                logger.warning(f"Invalid date format for earnings: {date_str}, error: {e}")
                                continue
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching earnings data for {symbol}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching earnings for {symbol}: {str(e)}")
        
        return result_items
        
    def _getDividendsFromStock(self, *, stock: Stock) -> list[StockEvent]:
        '''
        Fetch dividend events for a stock.
        
        Uses Alpha Vantage's DIVIDENDS API to retrieve all dividend-related
        dates including ex-dividend, declaration, record, and payment dates.
        
        Args:
            stock: Stock object to get dividends for
            
        Returns:
            List of StockEvent objects with various dividend event types
            
        Raises:
            TypeError: If stock is not a Stock object
            ValueError: If API request fails or returns invalid data
        '''
        # Type checking
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        
        function = "DIVIDENDS"
        symbol = stock.symbol.upper()
        result_items = []
        
        try:
            url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self.api_key}'
            data = requests.get(url)
            data.raise_for_status()  # Raise exception for bad status codes
            results = data.json()
            
            # Check for rate limit or error messages from Alpha Vantage
            if 'Information' in results or 'Note' in results or 'Error Message' in results:
                error_msg = results.get('Information') or results.get('Note') or results.get('Error Message')
                raise ValueError(f"Alpha Vantage API error: {error_msg}")
            
            # Check if the response symbol matches (it's at the root level)
            if results.get("symbol") == symbol:
                # Iterate over each 'data' entry
                for item in results.get("data", []):
                    
                    # Map API fields to EventType enums
                    return_dates_types = [
                        ["ex_dividend_date", EventType.DIVIDEND_EX],
                        ["declaration_date", EventType.DIVIDEND_DECLARATION],
                        ["record_date", EventType.DIVIDEND_RECORD],
                        ["payment_date", EventType.DIVIDEND_PAYMENT]
                    ]
                    
                    for dividend_type in return_dates_types:
                        date_str = item.get(dividend_type[0])
                        if date_str:
                            try:
                                # Parse date string to datetime object
                                date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                                # Create for each item a StockEvent
                                result_items.append(
                                    StockEvent(
                                        stock=stock,
                                        type=dividend_type[1],
                                        date=date,
                                        last_updated=datetime.now(timezone.utc),
                                        source=self.source
                                    )
                                )
                            except ValueError as e:
                                # Only log if date_str is not "None" (expected for future unannounced dates)
                                if date_str != "None" or date_str is None:
                                    logger.warning(f"Invalid date format for dividend {dividend_type[0]}: {date_str}, error: {e}")
                                continue
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching dividend data for {symbol}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching dividends for {symbol}: {str(e)}")
            
        return result_items
        
    def _getSplitsFromStock(self, *, stock: Stock) -> list[StockEvent]:
        '''
        Fetch stock split events for a stock.
        
        Uses Alpha Vantage's SPLITS API to retrieve historical and
        upcoming stock split information.
        
        Args:
            stock: Stock object to get splits for
            
        Returns:
            List of StockEvent objects with STOCK_SPLIT type
            
        Raises:
            TypeError: If stock is not a Stock object
            ValueError: If API request fails or returns invalid data
        '''
        # Type checking
        if not isinstance(stock, Stock):
            raise TypeError(f"Stock must be a Stock object, got {type(stock).__name__}")
        
        function = "SPLITS"
        symbol = stock.symbol.upper()
        result_items = []
        
        try:
            url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self.api_key}'
            data = requests.get(url)
            data.raise_for_status()  # Raise exception for bad status codes
            results = data.json()
            
            # Check for rate limit or error messages from Alpha Vantage
            if 'Information' in results or 'Note' in results or 'Error Message' in results:
                error_msg = results.get('Information') or results.get('Note') or results.get('Error Message')
                raise ValueError(f"Alpha Vantage API error: {error_msg}")
            
            # Check if the response symbol matches (it's at the root level)
            if results.get("symbol") == symbol:
                # Iterate over each 'data' entry
                for item in results.get("data", []):
                    date_str = item.get("effective_date")
                    if date_str:
                        try:
                            # Parse date string to datetime object
                            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                            # Create for each item a StockEvent
                            result_items.append(
                                StockEvent(
                                    stock=stock,
                                    type=EventType.STOCK_SPLIT,
                                    date=date,
                                    last_updated=datetime.now(timezone.utc),
                                    source=self.source
                                )
                            )
                        except ValueError as e:
                            logger.warning(f"Invalid date format for split effective_date: {date_str}, error: {e}")
                            continue
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching split data for {symbol}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching splits for {symbol}: {str(e)}")
        
        return result_items
