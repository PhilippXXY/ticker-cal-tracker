import csv
import logging
import requests
from datetime import datetime, timezone
from external.external_base import ExternalApiBaseDefinition
from models.stock_model import Stock
from models.stock_event_model import StockEvent, EventType

logger = logging.getLogger(__name__)

class AlphaVantage(ExternalApiBaseDefinition):
    
    def __init__(self):
        '''
        Initialize Alpha Vantage client with API key from environment.
        '''
        super().__init__(api_key_name='API_KEY_ALPHA_VANTAGE')
        
        # Define the source of the API calls for logging purposes
        self.source = self.__class__.__name__
       
    def getStockInfoFromName(self, *, name: str) -> Stock:
       
        if name and len(name.strip()) > 0:
            try:
                function = "SYMBOL_SEARCH"
                
                url = f'https://www.alphavantage.co/query?function={function}&keywords={name}&apikey={self.api_key}'
                data = requests.get(url)
                results = data.json()
                
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
                    
            except Exception as e:
                raise ValueError(f"Error fetching stock data for name '{name}': {str(e)}")
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
        '''
        if symbol and len(symbol) > 0:
            try:
                function = "SYMBOL_SEARCH"
                
                url = f'https://www.alphavantage.co/query?function={function}&keywords={symbol}&apikey={self.api_key}'
                data = requests.get(url)
                results = data.json()
                
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
        
        function = "EARNINGS_CALENDAR"
        symbol = str(Stock.symbol).upper()
        horizon = "12month"
        result_items = []
        
        url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&horizon={horizon}&apikey={self.api_key}'
        
        
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            data = csv.DictReader(decoded_content.splitlines(), delimiter=',')

            for row in data:
                if row.get("symbol") == symbol:
                    date_str = row.get("reportDate")
                    if date_str:
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
        
        return result_items
        
    def _getDividendsFromStock(self, *, stock: Stock) -> list[StockEvent]:
        
        function = "DIVIDENDS"
        symbol = str(Stock.symbol).upper()
        result_items = []
        
        url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self.api_key}'
        data = requests.get(url)
        results = data.json()
        
        # Check if the response symbol matches (it's at the root level)
        if results.get("symbol") == symbol:
            # Iterate over each 'data' entry
            for item in results.get("data", []):
                
                return_dates_types = [
                    ["ex_dividend_date", EventType.DIVIDEND_EX],
                    ["declaration_date", EventType.DIVIDEND_DECLARATION],
                    ["record_date", EventType.DIVIDEND_DECLARATION],
                    ["payment_date", EventType.DIVIDEND_PAYMENT]
                    ]
                
                for dividend_type in return_dates_types:
                    date_str = item.get(dividend_type[0])
                    if date_str:
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
            
        return result_items
        
    def _getSplitsFromStock(self, *, stock: Stock) -> list[StockEvent]:
        
        function = "SPLITS"
        symbol = str(Stock.symbol).upper()
        result_items = []
        
        url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self.api_key}'
        data = requests.get(url)
        results = data.json()
        
        # Check if the response symbol matches (it's at the root level)
        if results.get("symbol") == symbol:
            # Iterate over each 'data' entry
            for item in results.get("data", []):
                date_str = item.get("effective_date")
                if date_str:
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
        
        return result_items
