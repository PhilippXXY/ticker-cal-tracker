import finnhub
import logging
from datetime import datetime, timezone
from finnhub.exceptions import FinnhubAPIException

from .external_base import ExternalApiBaseDefinition
from src.models.stock_model import Stock

logger = logging.getLogger(__name__)

class Finnhub(ExternalApiBaseDefinition):
    '''
    Finnhub API client for retrieving stock information.
    
    Implementation of financial data API using Finnhub's REST endpoints.
    Supports lookup by symbol and company name.
    
    API documentation: https://finnhub.io/docs/api/
    '''
    
    def __init__(self):
        '''
        Initialize Finnhub client with API key from environment.
        '''
        super().__init__(api_key_name='API_KEY_FINNHUB')
        self.finnhub_client = finnhub.Client(api_key=self.api_key)
        
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
                # Call Finnhub company profile API
                data = self.finnhub_client.company_profile2(symbol=symbol)
                logger.debug(f"Company profile data for symbol '{symbol}': {data}")
                
                if data and 'name' in data:
                    # Build Stock object from API response
                    return Stock(  
                        name=data.get('name', ''),
                        symbol=data.get('ticker', symbol),
                        last_updated=datetime.now(timezone.utc)
                    )
                else:
                    raise ValueError(f"No stock data found for symbol: {symbol}")
            
            except FinnhubAPIException as e:
                # Handle Finnhub-specific API errors (rate limits, invalid requests, etc.)
                raise ValueError(f"Finnhub API error for symbol {symbol}: {str(e)}")
            except Exception as e:
                raise ValueError(f"Error fetching stock data for symbol {symbol}: {str(e)}")
        else:
            raise ValueError(f"Invalid symbol provided: {symbol}")
    
    
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
        '''     
        if name and len(name.strip()) > 0:
            try:
                # Search companies by name
                search_results = self.finnhub_client.symbol_lookup(name)
                logger.debug(f"Search results for '{name}': {search_results}")
                
                if search_results and 'result' in search_results and len(search_results['result']) > 0:
                    # Take the first (best) match
                    first_match = search_results['result'][0]
                    symbol = first_match.get('symbol', '')
                    
                    if symbol:
                        # Get detailed company information using symbol
                        profile_data = self.finnhub_client.company_profile2(symbol=symbol)
                        
                        if profile_data and 'name' in profile_data:
                            return Stock(
                                name=profile_data.get('name', ''),
                                symbol=symbol.upper(),
                                last_updated=datetime.now(timezone.utc)
                            )
                        else:
                            raise ValueError(f"No detailed data found for symbol: {symbol}")
                    else:
                        raise ValueError(f"No valid symbol found in search results for name: {name}")
                else:
                    raise ValueError(f"No stocks found for name: {name}")
            
            except FinnhubAPIException as e:
                # Handle Finnhub-specific API errors (rate limits, invalid requests, etc.)
                raise ValueError(f"Finnhub API error for name '{name}': {str(e)}")
            except Exception as e:
                raise ValueError(f"Error fetching stock data for name '{name}': {str(e)}")
        else:
            raise ValueError(f"Invalid name provided: {name}")
