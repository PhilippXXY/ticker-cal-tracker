# Disclaimer: Created by GitHub Copilot
'''
Integration tests for WatchlistService with real database.
IMPORTANT: These tests will modify data in the database.
'''

import unittest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timezone

from src.app.services.watchlists_service import WatchlistService
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.adapter_factory import DatabaseAdapterFactory, DatabaseEnvironment
from src.models.stock_event_model import EventType
from src.models.stock_model import Stock


# Skip integration tests if flag is set
SKIP_DB_INTEGRATION = os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1'


@unittest.skipIf(SKIP_DB_INTEGRATION, "Skipping database integration tests")
class TestWatchlistServiceIntegration(unittest.TestCase):
    '''Integration tests for WatchlistService with real database.'''
    
    @classmethod
    def setUpClass(cls):
        '''Set up database connection for all tests.'''
        cls.adapter = LocalDatabaseAdapter(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'ticker_calendar_local_dev_db'),
            user=os.getenv('DB_USER', 'ticker_dev'),
            password=os.getenv('DB_PASSWORD', 'dev_password_123')
        )
        
        # Verify database is accessible
        if not cls.adapter.health_check():
            raise unittest.SkipTest(
                "Database is not accessible. Run 'python database/local/manage_db.py setup' first."
            )
        
        # Initialize the DatabaseAdapterFactory for integration tests
        DatabaseAdapterFactory.initialize(environment=DatabaseEnvironment.DEVELOPMENT)
        
        cls.service = WatchlistService()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up database connection.'''
        cls.adapter.close()
    
    def setUp(self):
        '''Set up test data before each test.'''
        self.test_user_id = uuid4()
        self.test_watchlists = []
        self.test_stocks = []
        
        # Create a test user in the database
        self._create_test_user()
    
    def tearDown(self):
        '''Clean up test data after each test.'''
        # Delete test watchlists (cascades to watchlist_settings and watchlist_follows)
        for watchlist_id in self.test_watchlists:
            try:
                self.service.delete_watchlist(user_id=self.test_user_id, watchlist_id=watchlist_id)
            except Exception:
                pass
        
        # Clean up test stocks
        for ticker in self.test_stocks:
            try:
                query = "DELETE FROM stocks WHERE ticker = :ticker"
                self.adapter.execute_update(query=query, params={'ticker': ticker})
            except Exception:
                pass
        
        # Clean up test user
        try:
            query = "DELETE FROM users WHERE id = :user_id"
            self.adapter.execute_update(query=query, params={'user_id': self.test_user_id})
        except Exception:
            pass
    
    def _create_test_user(self):
        '''Helper to create a test user in the database.'''
        query = """
            INSERT INTO users (id, email, password)
            VALUES (:user_id, :email, :password)
            ON CONFLICT (id) DO NOTHING
        """
        self.adapter.execute_update(
            query=query,
            params={
                'user_id': self.test_user_id,
                'email': f'test_{self.test_user_id.hex[:8]}@example.com',
                'password': 'test_hash_not_real'
            }
        )
    
    def _create_test_stock(self, ticker='TESTSTOCK', name='Test Stock Inc.'):
        '''Helper to create a test stock in the database.'''
        query = """
            INSERT INTO stocks (ticker, name, last_updated)
            VALUES (:ticker, :name, :last_updated)
            ON CONFLICT (ticker) DO NOTHING
        """
        self.adapter.execute_update(
            query=query,
            params={
                'ticker': ticker,
                'name': name,
                'last_updated': datetime.now(timezone.utc)
            }
        )
        return ticker
    
    def _add_stock_to_watchlist_with_mock(self, user_id, watchlist_id, ticker, name):
        '''Helper to add stock to watchlist with mocked StocksService.'''
        mock_stock = Stock(
            name=name,
            symbol=ticker,
            last_updated=datetime.now(timezone.utc)
        )
        with patch.object(self.service.stocks_service, 'get_stock_from_ticker', return_value=mock_stock):
            return self.service.add_stock_to_watchlist(
                user_id=user_id,
                watchlist_id=watchlist_id,
                stock_ticker=ticker,
            )
        return ticker
    
    def test_create_and_get_watchlist(self):
        '''Test creating a watchlist and retrieving it.'''
        watchlist_settings = {
            EventType.EARNINGS_ANNOUNCEMENT: True,
            EventType.DIVIDEND_EX: False,
            EventType.DIVIDEND_DECLARATION: True,
            EventType.DIVIDEND_RECORD: False,
            EventType.DIVIDEND_PAYMENT: True,
            EventType.STOCK_SPLIT: False,
        }
        
        # Create watchlist
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Integration Test Watchlist',
            watchlist_settings=watchlist_settings,
        )
        
        self.assertIsNotNone(created)
        self.assertIn('id', created)
        self.assertEqual(created['name'], 'Integration Test Watchlist')
        self.assertTrue(created['include_earnings_announcement'])
        self.assertFalse(created['include_dividend_ex'])
        
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Retrieve watchlist
        retrieved = self.service.get_watchlist_by_id(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], watchlist_id) # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(retrieved['name'], 'Integration Test Watchlist') # pyright: ignore[reportOptionalSubscript]
        self.assertTrue(retrieved['include_earnings_announcement']) # pyright: ignore[reportOptionalSubscript]
        self.assertFalse(retrieved['include_dividend_ex']) # pyright: ignore[reportOptionalSubscript]
    
    def test_get_all_watchlists_for_user(self):
        '''Test retrieving all watchlists for a user.'''
        # Create multiple watchlists
        watchlist_settings = {event_type: True for event_type in EventType}
        
        watchlist1 = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Tech Stocks',
            watchlist_settings=watchlist_settings,
        )
        self.test_watchlists.append(watchlist1['id'])
        
        watchlist2 = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Energy Stocks',
            watchlist_settings=watchlist_settings,
        )
        self.test_watchlists.append(watchlist2['id'])
        
        # Retrieve all watchlists
        all_watchlists = self.service.get_all_watchlists_for_user(user_id=self.test_user_id)
        
        self.assertGreaterEqual(len(all_watchlists), 2)
        names = [wl['name'] for wl in all_watchlists]
        self.assertIn('Tech Stocks', names)
        self.assertIn('Energy Stocks', names)
    
    def test_update_watchlist_name(self):
        '''Test updating watchlist name.'''
        watchlist_settings = {event_type: True for event_type in EventType}
        
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Original Name',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Update name
        updated = self.service.update_watchlist(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            name='Updated Name',
        )
        
        self.assertTrue(updated)
        
        # Verify update
        retrieved = self.service.get_watchlist_by_id(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(retrieved['name'], 'Updated Name') # pyright: ignore[reportOptionalSubscript]
    
    def test_update_watchlist_settings(self):
        '''Test updating watchlist event settings.'''
        watchlist_settings = {event_type: True for event_type in EventType}
        
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Settings Test',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Update settings
        new_settings = {
            EventType.EARNINGS_ANNOUNCEMENT: False,
            EventType.DIVIDEND_EX: False,
        }
        
        updated = self.service.update_watchlist(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            watchlist_settings=new_settings,
        )
        
        self.assertTrue(updated)
        
        # Verify update
        retrieved = self.service.get_watchlist_by_id(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertFalse(retrieved['include_earnings_announcement']) # pyright: ignore[reportOptionalSubscript]
        self.assertFalse(retrieved['include_dividend_ex']) # pyright: ignore[reportOptionalSubscript]
    
    def test_add_and_remove_stock_from_watchlist(self):
        '''Test adding and removing a stock from watchlist.'''
        # Create test stock
        ticker = self._create_test_stock('TESTINT', 'Test Integration Stock')
        
        # Create watchlist
        watchlist_settings = {event_type: True for event_type in EventType}
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Stock Test Watchlist',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Add stock to watchlist using helper with mock
        added = self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker,
            name='Test Integration Stock'
        )
        self.assertTrue(added)
        
        # Verify stock is in watchlist
        stocks = self.service.get_watchlist_stocks(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(len(stocks), 1)
        self.assertEqual(stocks[0]['ticker'], ticker)
        
        # Remove stock from watchlist
        removed = self.service.remove_stock_to_watchlist(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            stock_ticker=ticker,
        )
        self.assertTrue(removed)
        
        # Verify stock is no longer in watchlist
        stocks_after = self.service.get_watchlist_stocks(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(len(stocks_after), 0)
    
    def test_add_multiple_stocks_to_watchlist(self):
        '''Test adding multiple stocks to a watchlist.'''
        # Create test stocks
        ticker1 = self._create_test_stock('TEST1', 'Test Stock 1')
        ticker2 = self._create_test_stock('TEST2', 'Test Stock 2')
        ticker3 = self._create_test_stock('TEST3', 'Test Stock 3')
        
        # Create watchlist
        watchlist_settings = {event_type: True for event_type in EventType}
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Multi-Stock Watchlist',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Add multiple stocks using helper with mocks
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker1,
            name='Test Stock 1'
        )
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker2,
            name='Test Stock 2'
        )
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker3,
            name='Test Stock 3'
        )
        
        # Verify all stocks are in watchlist
        stocks = self.service.get_watchlist_stocks(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(len(stocks), 3)
        tickers = [stock['ticker'] for stock in stocks]
        self.assertIn(ticker1, tickers)
        self.assertIn(ticker2, tickers)
        self.assertIn(ticker3, tickers)
    
    def test_delete_watchlist(self):
        '''Test deleting a watchlist.'''
        watchlist_settings = {event_type: True for event_type in EventType}
        
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='To Be Deleted',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        
        # Delete watchlist
        deleted = self.service.delete_watchlist(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertTrue(deleted)
        
        # Verify watchlist is deleted
        retrieved = self.service.get_watchlist_by_id(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertIsNone(retrieved)
    
    def test_watchlist_isolation_between_users(self):
        '''Test that watchlists are isolated between different users.'''
        user1_id = uuid4()
        user2_id = uuid4()
        
        # Create test users
        for user_id in [user1_id, user2_id]:
            query = """
                INSERT INTO users (id, email, password)
                VALUES (:user_id, :email, :password)
                ON CONFLICT (id) DO NOTHING
            """
            self.adapter.execute_update(
                query=query,
                params={
                    'user_id': user_id,
                    'email': f'test_{user_id.hex[:8]}@example.com',
                    'password': 'test_hash_not_real'
                }
            )
        
        watchlist_settings = {event_type: True for event_type in EventType}
        
        # User 1 creates watchlist
        watchlist1 = self.service.create_watchlist(
            user_id=user1_id,
            name='User 1 Watchlist',
            watchlist_settings=watchlist_settings,
        )
        self.test_watchlists.append(watchlist1['id'])
        
        # User 2 creates watchlist
        watchlist2 = self.service.create_watchlist(
            user_id=user2_id,
            name='User 2 Watchlist',
            watchlist_settings=watchlist_settings,
        )
        self.test_watchlists.append(watchlist2['id'])
        
        # User 1 should not see User 2's watchlist
        user1_watchlists = self.service.get_all_watchlists_for_user(user_id=user1_id)
        user1_ids = [wl['id'] for wl in user1_watchlists]
        self.assertIn(watchlist1['id'], user1_ids)
        self.assertNotIn(watchlist2['id'], user1_ids)
        
        # User 2 should not see User 1's watchlist
        user2_watchlists = self.service.get_all_watchlists_for_user(user_id=user2_id)
        user2_ids = [wl['id'] for wl in user2_watchlists]
        self.assertIn(watchlist2['id'], user2_ids)
        self.assertNotIn(watchlist1['id'], user2_ids)
        
        # Clean up both users' watchlists and users
        self.service.delete_watchlist(user_id=user1_id, watchlist_id=watchlist1['id'])
        self.service.delete_watchlist(user_id=user2_id, watchlist_id=watchlist2['id'])
        
        # Clean up users
        for user_id in [user1_id, user2_id]:
            try:
                query = "DELETE FROM users WHERE id = :user_id"
                self.adapter.execute_update(query=query, params={'user_id': user_id})
            except Exception:
                pass

    
    def test_duplicate_stock_in_watchlist(self):
        '''Test adding the same stock twice to a watchlist (should not duplicate).'''
        ticker = self._create_test_stock('TESTDUP', 'Test Duplicate Stock')
        
        watchlist_settings = {event_type: True for event_type in EventType}
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Duplicate Test',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        self.test_watchlists.append(watchlist_id)
        
        # Add stock first time using helper with mock
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker,
            name='Test Duplicate Stock'
        )
        
        # Add stock second time (should not error, just be idempotent)
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker,
            name='Test Duplicate Stock'
        )
        
        # Verify only one instance
        stocks = self.service.get_watchlist_stocks(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(len(stocks), 1)
    
    def test_cascade_delete_watchlist_with_stocks(self):
        '''Test that deleting a watchlist also removes its stock associations.'''
        ticker = self._create_test_stock('TESTCAS', 'Test Cascade Stock')
        
        watchlist_settings = {event_type: True for event_type in EventType}
        created = self.service.create_watchlist(
            user_id=self.test_user_id,
            name='Cascade Test',
            watchlist_settings=watchlist_settings,
        )
        watchlist_id = created['id']
        
        # Add stock using helper with mock
        self._add_stock_to_watchlist_with_mock(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id,
            ticker=ticker,
            name='Test Cascade Stock'
        )
        
        # Verify stock is in watchlist
        stocks = self.service.get_watchlist_stocks(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertEqual(len(stocks), 1)
        
        # Delete watchlist
        deleted = self.service.delete_watchlist(
            user_id=self.test_user_id,
            watchlist_id=watchlist_id
        )
        self.assertTrue(deleted)
        
        # Verify we can't get stocks from deleted watchlist
        with self.assertRaises(ValueError):
            self.service.get_watchlist_stocks(
                user_id=self.test_user_id,
                watchlist_id=watchlist_id
            )


if __name__ == '__main__':
    unittest.main()
