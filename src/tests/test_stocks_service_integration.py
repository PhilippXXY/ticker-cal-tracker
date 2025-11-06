# Disclaimer: Created by GitHub Copilot
'''
Integration tests for StocksService.

IMPORTANT: This file contains TWO types of integration tests:
1. Database integration tests (TestStocksServiceIntegration) - NO API calls, safe to run
2. External API integration tests (TestStocksServiceExternalAPIIntegration) - Uses real API calls, costs quota!

Use --db-integration flag to run only database tests.
Use --api-integration flag to run only API tests (uses quota).
'''

import unittest
import os
from datetime import datetime

from src.app.services.stocks_service import StocksService
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.adapter_factory import DatabaseAdapterFactory, DatabaseEnvironment


@unittest.skipIf(
    os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1',
    'Skipping database integration tests'
)
class TestStocksServiceIntegration(unittest.TestCase):
    '''Integration tests for StocksService with real database.
    
    These tests use the database but DO NOT make external API calls.
    Safe to run frequently - will use cached data if available.
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up test database connection.'''
        # Create LocalDatabaseAdapter directly
        cls.adapter = LocalDatabaseAdapter(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'ticker_calendar_local_dev_db'),
            user=os.getenv('DB_USER', 'ticker_dev'),
            password=os.getenv('DB_PASSWORD', 'dev_password_123')
        )
        
        # Verify database is accessible
        if not cls.adapter.health_check():
            raise unittest.SkipTest('Database is not accessible')
        
        # Initialize DatabaseAdapterFactory with DEVELOPMENT environment
        DatabaseAdapterFactory.initialize(environment=DatabaseEnvironment.DEVELOPMENT)
        
        cls.service = StocksService()
        
        # Store ticker symbols we've tested for cleanup
        cls.test_tickers = set()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up test data.'''
        # Note: In production, you might want to clean up test data
        # For now, we'll leave it as it acts as a cache
        pass
    
    def test_get_stock_caches_result(self):
        '''Test that stock data is cached in database.
        
        Note: This may call external API on first run if stock not cached.
        Subsequent runs will use cached data.
        '''
        ticker = 'AAPL'
        self.test_tickers.add(ticker)
        
        # First call - should fetch from external API
        stock1 = self.service.get_stock_from_ticker(ticker=ticker)
        self.assertEqual(stock1.symbol, ticker)
        self.assertIsNotNone(stock1.name)
        self.assertIsInstance(stock1.last_updated, datetime)
        
        # Second call - should retrieve from cache
        stock2 = self.service.get_stock_from_ticker(ticker=ticker)
        self.assertEqual(stock2.symbol, ticker)
        self.assertEqual(stock2.name, stock1.name)
        # Cache hit should have same or newer timestamp
        self.assertGreaterEqual(stock2.last_updated, stock1.last_updated)
    
    def test_get_stock_case_insensitive(self):
        '''Test ticker lookup is case-insensitive.
        
        Note: This may call external API on first run if stock not cached.
        Subsequent runs will use cached data.
        '''
        ticker_upper = 'MSFT'
        ticker_lower = 'msft'
        self.test_tickers.add(ticker_upper)
        
        stock_upper = self.service.get_stock_from_ticker(ticker=ticker_upper)
        stock_lower = self.service.get_stock_from_ticker(ticker=ticker_lower)
        
        # Should return same stock data
        self.assertEqual(stock_upper.symbol, stock_lower.symbol)
        self.assertEqual(stock_upper.name, stock_lower.name)
    
    def test_get_stock_multiple_different_stocks(self):
        '''Test retrieving multiple different stocks.
        
        Note: This may call external API on first run if stocks not cached.
        Subsequent runs will use cached data.
        '''
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        
        stocks = []
        for ticker in tickers:
            self.test_tickers.add(ticker)
            stock = self.service.get_stock_from_ticker(ticker=ticker)
            stocks.append(stock)
        
        # Verify all stocks were retrieved
        self.assertEqual(len(stocks), len(tickers))
        
        # Verify each stock has correct data
        for stock in stocks:
            self.assertIsNotNone(stock.symbol)
            self.assertIsNotNone(stock.name)
            self.assertIsInstance(stock.last_updated, datetime)
        
        # Verify stocks are different
        symbols = [stock.symbol for stock in stocks]
        self.assertEqual(len(set(symbols)), len(tickers))


@unittest.skipIf(
    os.getenv('SKIP_INTEGRATION_TESTS') == '1',
    'Skipping external API integration tests'
)
class TestStocksServiceExternalAPIIntegration(unittest.TestCase):
    '''Integration tests with real external API calls.
    
    WARNING: These tests consume API rate limits!
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up service for API testing.'''
        # Check if we have API keys
        has_alpha_vantage = bool(os.getenv('API_KEY_ALPHA_VANTAGE'))
        has_finnhub = bool(os.getenv('API_KEY_FINNHUB'))
        
        if not has_alpha_vantage and not has_finnhub:
            raise unittest.SkipTest('No API keys available')
        
        cls.service = StocksService()
    
    def test_get_stock_from_external_api(self):
        '''Test fetching stock from external API.'''
        # Use a less common ticker to avoid cache hits
        ticker = 'TSLA'
        
        stock = self.service.get_stock_from_ticker(ticker=ticker)
        
        self.assertEqual(stock.symbol, ticker)
        self.assertIsNotNone(stock.name)
        self.assertIn('Tesla', stock.name)
        self.assertIsInstance(stock.last_updated, datetime)
    
    def test_get_stock_invalid_ticker_from_api(self):
        '''Test that invalid ticker raises appropriate error.'''
        # Use a definitely invalid ticker
        invalid_ticker = 'THISSTOCKDOESNOTEXIST123456'
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker=invalid_ticker)
        
        # Should contain error about fetching from external providers
        error_msg = str(context.exception)
        self.assertTrue(
            'Failed to fetch stock from external providers' in error_msg
        )


if __name__ == '__main__':
    unittest.main()
