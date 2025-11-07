'''
Integration tests for background tasks.

IMPORTANT: This file contains database integration tests that require a running database.
These tests DO NOT make external API calls - they use mocked external API responses.
Safe to run frequently.
'''

import unittest
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock

from src.app.background.tasks import update_stale_stock_events
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.adapter_factory import DatabaseAdapterFactory, DatabaseEnvironment
from src.models.stock_model import Stock
from src.models.stock_event_model import StockEvent, EventType


@unittest.skipIf(
    os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1',
    'Skipping database integration tests'
)
class TestBackgroundTasksIntegration(unittest.TestCase):
    '''Integration tests for background tasks with real database.
    
    These tests use the database but DO NOT make external API calls.
    External API calls are mocked to avoid using quota.
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
        
        cls.test_tickers = []
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up test data.'''
        # Clean up test stocks and their events
        for ticker in cls.test_tickers:
            try:
                # Delete stock events first (due to foreign key)
                cls.adapter.execute_update(
                    query="DELETE FROM stock_events WHERE stock_ticker = :ticker",
                    params={'ticker': ticker}
                )
                # Delete stock
                cls.adapter.execute_update(
                    query="DELETE FROM stocks WHERE ticker = :ticker",
                    params={'ticker': ticker}
                )
            except Exception:
                pass  # Ignore cleanup errors
        
        cls.adapter.close()
    
    def setUp(self):
        '''Set up for each test.'''
        # Clean up any existing test data
        self._cleanup_test_stocks()
    
    def tearDown(self):
        '''Clean up after each test.'''
        self._cleanup_test_stocks()
    
    def _cleanup_test_stocks(self):
        '''Remove test stocks from database.'''
        test_tickers = ['TESTSTOCK1', 'TESTSTOCK2', 'TESTSTOCK3', 'STALETEST']
        for ticker in test_tickers:
            try:
                self.adapter.execute_update(
                    query="DELETE FROM stock_events WHERE stock_ticker = :ticker",
                    params={'ticker': ticker}
                )
                self.adapter.execute_update(
                    query="DELETE FROM stocks WHERE ticker = :ticker",
                    params={'ticker': ticker}
                )
            except Exception:
                pass
    
    def _insert_test_stock(self, ticker, name, last_updated):
        '''Helper to insert a test stock into the database.'''
        self.adapter.execute_update(
            query="""
                INSERT INTO stocks (ticker, name, last_updated)
                VALUES (:ticker, :name, :last_updated)
                ON CONFLICT (ticker) DO UPDATE
                SET name = EXCLUDED.name,
                    last_updated = EXCLUDED.last_updated
            """,
            params={
                'ticker': ticker,
                'name': name,
                'last_updated': last_updated,
            }
        )
        self.test_tickers.append(ticker)
    
    @patch('src.app.background.tasks.StocksService')
    def test_update_stale_stock_events_with_real_database(self, mock_stocks_service_class):
        '''Test that stale stocks are correctly identified and updated in real database.'''
        # Arrange: Insert test stocks with different last_updated dates
        now = datetime.now(timezone.utc)
        stale_date = now - timedelta(days=10)  # 10 days old (stale)
        fresh_date = now - timedelta(days=3)   # 3 days old (fresh)
        
        # Insert stale stock
        self._insert_test_stock('TESTSTOCK1', 'Test Stock 1', stale_date)
        self._insert_test_stock('TESTSTOCK2', 'Test Stock 2', stale_date)
        
        # Insert fresh stock (should not be updated)
        self._insert_test_stock('TESTSTOCK3', 'Test Stock 3', fresh_date)
        
        # Mock the StocksService to avoid real API calls
        mock_service = Mock()
        mock_stocks_service_class.return_value = mock_service
        
        # Act: Run the background task
        update_stale_stock_events()
        
        # Assert: Verify that only stale stocks were processed
        self.assertEqual(mock_service.upsert_stock_events.call_count, 2)
        
        # Verify the correct stocks were updated
        calls = mock_service.upsert_stock_events.call_args_list
        updated_tickers = {call[1]['stock'].symbol for call in calls}
        self.assertIn('TESTSTOCK1', updated_tickers)
        self.assertIn('TESTSTOCK2', updated_tickers)
        self.assertNotIn('TESTSTOCK3', updated_tickers)
        
        # Verify all event types were requested for each stock
        for call in calls:
            event_types = call[1]['event_types']
            self.assertEqual(len(event_types), len(list(EventType)))
    
    @patch('src.app.services.stocks_service.ExternalApiFacade')
    def test_update_stale_stock_events_updates_timestamp(self, mock_external_api_class):
        '''Test that last_updated timestamp is updated after processing.'''
        # Arrange: Insert a stale stock
        stale_date = datetime.now(timezone.utc) - timedelta(days=10)
        self._insert_test_stock('STALETEST', 'Stale Test Corp', stale_date)
        
        # Mock the external API to return empty events
        mock_external_api = Mock()
        mock_external_api.getStockEventDatesFromStock.return_value = []
        mock_external_api_class.return_value = mock_external_api
        
        # Record the time before running the task
        time_before = datetime.now(timezone.utc)
        
        # Act: Run the background task
        update_stale_stock_events()
        
        # Assert: Verify the stock's last_updated was updated
        result = list(self.adapter.execute_query(
            query="SELECT last_updated FROM stocks WHERE ticker = :ticker",
            params={'ticker': 'STALETEST'}
        ))
        
        self.assertEqual(len(result), 1)
        updated_time = result[0]['last_updated']
        
        # Parse datetime if returned as string
        if isinstance(updated_time, str):
            updated_time = datetime.fromisoformat(updated_time)
        
        # Verify the timestamp was updated to a recent time
        self.assertGreater(updated_time, time_before - timedelta(seconds=10))
        self.assertGreater(updated_time, stale_date)
    
    @patch('src.app.services.stocks_service.ExternalApiFacade')
    def test_update_stale_stock_events_stores_events(self, mock_external_api_class):
        '''Test that stock events are actually stored in the database.'''
        # Arrange: Insert a stale stock
        stale_date = datetime.now(timezone.utc) - timedelta(days=10)
        self._insert_test_stock('TESTSTOCK1', 'Test Stock 1', stale_date)
        
        # Create a Stock object for the mock events
        test_stock = Stock(
            symbol='TESTSTOCK1',
            name='Test Stock 1',
            last_updated=stale_date
        )
        
        # Mock the external API to return test events
        mock_external_api = Mock()
        test_event_date = datetime.now(timezone.utc)
        current_time = datetime.now(timezone.utc)
        mock_events = [
            StockEvent(
                stock=test_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=test_event_date,
                last_updated=current_time,
                source='test_api'
            ),
            StockEvent(
                stock=test_stock,
                type=EventType.DIVIDEND_PAYMENT,
                date=test_event_date,
                last_updated=current_time,
                source='test_api'
            ),
        ]
        mock_external_api.getStockEventDatesFromStock.return_value = mock_events
        mock_external_api_class.return_value = mock_external_api
        
        # Act: Run the background task
        update_stale_stock_events()
        
        # Assert: Verify events were stored in database
        events = list(self.adapter.execute_query(
            query="""
                SELECT type, event_date, source 
                FROM stock_events 
                WHERE stock_ticker = :ticker
            """,
            params={'ticker': 'TESTSTOCK1'}
        ))
        
        # Should have at least the events we mocked
        self.assertGreaterEqual(len(events), 2)
        
        # Verify event types
        event_types = [e['type'] for e in events]
        self.assertIn('EARNINGS_ANNOUNCEMENT', event_types)
        self.assertIn('DIVIDEND_PAYMENT', event_types)
    
    @patch('src.app.background.tasks.StocksService')
    def test_update_stale_stock_events_empty_database(self, mock_stocks_service_class):
        '''Test that task handles empty database gracefully.'''
        # Arrange: Ensure no stale stocks exist (already cleaned up in setUp)
        mock_service = Mock()
        mock_stocks_service_class.return_value = mock_service
        
        # Act: Run the background task
        update_stale_stock_events()
        
        # Assert: No updates should be attempted
        self.assertEqual(mock_service.upsert_stock_events.call_count, 0)


if __name__ == '__main__':
    unittest.main()
