
from datetime import datetime, timezone
from uuid import UUID
from src.database.adapter_factory import DatabaseAdapterFactory
from src.models.stock_model import Stock
from src.external.external_api_facade import ExternalApiFacade

class StocksService:
    
    def __init__(self):
        '''
        Initialise the service with database.
        '''
        self.db = DatabaseAdapterFactory.get_instance()
        self.external_api = ExternalApiFacade()
        
    def get_stock_from_ticker(self, *, ticker: str) -> Stock:
        '''
        Retrieve stock information by ticker symbol, using cache-first strategy.
        
        This method implements a two-tier lookup:
        1. Check local database cache for previously fetched stock data
        2. If not cached, fetch from external API providers and cache the result
        
        Args:
            ticker: Stock ticker symbol. Case-insensitive.
        
        Returns:
            Stock object containing name, symbol, and last_updated timestamp.
        
        Raises:
            ValueError: If ticker is not a non-empty string.
            Exception: If database query fails or external API call fails.
        '''
        # Validate input parameter
        if not isinstance(ticker, str) or not ticker.strip():
            raise ValueError('ticker must be a non-empty string.')
        
        # Normalize ticker to uppercase for consistent storage and lookup
        normalized_ticker = ticker.strip().upper()
        
        # First, check if stock data is already cached in the database
        fetch_query = """
            SELECT ticker, name, last_updated
            FROM stocks
            WHERE ticker = :ticker
            LIMIT 1
        """
        
        try:
            results = list(self.db.execute_query(
                query=fetch_query,
                params={'ticker': normalized_ticker},
            ))
        except Exception as exc:
            raise Exception(f'Failed to query local stock cache: {str(exc)}') from exc
        
        # If found in cache, return the cached stock data
        if results:
            record = results[0]
            last_updated = record.get('last_updated')
            
            # Handle various timestamp formats from database
            # Some adapters return strings, others return datetime objects
            if isinstance(last_updated, str):
                try:
                    last_updated = datetime.fromisoformat(last_updated)
                except ValueError:
                    # Fallback if ISO format parsing fails
                    last_updated = datetime.now(timezone.utc)
            elif not isinstance(last_updated, datetime):
                # Handle None or other unexpected types
                last_updated = datetime.now(timezone.utc)
            
            return Stock(
                name=record['name'],
                symbol=record['ticker'],
                last_updated=last_updated,
            )
        
        # Cache miss: fetch stock data from external API providers
        try:
            stock = self.external_api.getStockInfoFromSymbol(symbol=normalized_ticker)
        except Exception as exc:
            raise Exception(f'Failed to fetch stock from external providers: {str(exc)}') from exc
        
        # Normalize the stock data for storage
        stock_to_store = Stock(
            name=stock.name,
            symbol=stock.symbol.upper(),
            last_updated=stock.last_updated if isinstance(stock.last_updated, datetime) else datetime.now(timezone.utc),
        )
        
        # Cache the fetched stock data for future lookups
        # Uses UPSERT pattern to handle both new inserts and updates
        insert_query = """
            INSERT INTO stocks (ticker, name, last_updated)
            VALUES (:ticker, :name, :last_updated)
            ON CONFLICT (ticker) DO UPDATE
            SET name = EXCLUDED.name,
                last_updated = EXCLUDED.last_updated
        """
        
        try:
            self.db.execute_update(
                query=insert_query,
                params={
                    'ticker': stock_to_store.symbol,
                    'name': stock_to_store.name,
                    'last_updated': stock_to_store.last_updated,
                },
            )
        except Exception as exc:
            # Log error but still return the stock data since we fetched it successfully
            raise Exception(f'Failed to persist stock data: {str(exc)}') from exc
        
        return stock_to_store
        
