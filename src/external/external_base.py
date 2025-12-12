import os
from abc import ABC, abstractmethod

from src.models.stock_model import Stock

class ExternalApiBaseDefinition(ABC):
    '''Base class for external financial data API integrations.
    
    Provides common initialization and abstract methods for stock data retrieval.
    '''
    
    def __init__(self, *, api_key_name: str):
        '''Initialize with API key from environment variables.
        
        Args:
            api_key_name: Name of the environment variable containing the API key
            
        Raises:
            ValueError: If API key is not found in environment
        '''
        self.api_key = os.getenv(api_key_name)
        if not self.api_key:
            raise ValueError(f"API key '{api_key_name}' not found in environment variables")
    
    @abstractmethod
    def getStockInfoFromSymbol(self, *, symbol: str) -> "Stock":
        '''Retrieve stock information by ticker symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Stock: Stock information object
   
        :see: models.stock_model.Stock
        '''
        pass

    @abstractmethod
    def getStockInfoFromName(self, *, name: str) -> "Stock":
        '''Retrieve stock information by company name.
        
        Args:
            name: Company name (e.g., 'Apple Inc.')
            
        Returns:
            Stock: Stock information object
            
        :see: models.stock_model.Stock
        '''
        pass
