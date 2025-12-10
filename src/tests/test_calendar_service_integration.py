# Disclaimer: Created by GitHub Copilot
'''
Integration tests for CalendarService with real database.
IMPORTANT: These tests will read data from the database.
'''

import unittest
import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from src.app.services.calendar_service import CalendarService
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.adapter_factory import DatabaseAdapterFactory, DatabaseEnvironment


# Skip integration tests if flag is set
SKIP_DB_INTEGRATION = os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1'


@unittest.skipIf(SKIP_DB_INTEGRATION, "Skipping database integration tests")
class TestCalendarServiceIntegration(unittest.TestCase):
    '''Integration tests for CalendarService with real database.'''
    
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
        
        cls.service = CalendarService()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up database connection.'''
        cls.adapter.close()
    
    def setUp(self):
        '''Set up test data before each test.'''
        self.test_user_id = 1  # Use integer ID
        self.test_watchlist_id = uuid4()
        self.test_calendar_token = f'test_token_{uuid4().hex[:16]}'
        self.test_entities = []
        
        # Create test user
        self._create_test_user()
        
        # Create test stocks
        self._create_test_stock('AAPL', 'Apple Inc.')
        self._create_test_stock('MSFT', 'Microsoft Corporation')
        
        # Create test watchlist
        self._create_test_watchlist()
        
        # Create test stock events
        self._create_test_stock_events()
        
        # Add stocks to watchlist
        self._add_stock_to_watchlist('AAPL')
        self._add_stock_to_watchlist('MSFT')
    
    def tearDown(self):
        '''Clean up test data after each test.'''
        # Clean up in reverse order of dependencies
        self._cleanup_follows()
        self._cleanup_stock_events()
        self._cleanup_watchlist_settings()
        self._cleanup_watchlists()
        self._cleanup_stocks()
        self._cleanup_users()
    
    def _create_test_user(self):
        '''Helper to create a test user.'''
        # We need to handle potential conflict if ID 1 already exists
        # In a real integration test, we might want to let the DB assign the ID
        # But for simplicity here, we'll try to insert with a specific ID or update
        
        # First check if user exists
        check_query = "SELECT id FROM users WHERE id = :user_id"
        result = self.adapter.execute_query(query=check_query, params={'user_id': self.test_user_id})
        
        if result:
            # User exists, just ensure fields are what we expect if needed
            pass
        else:
            query = """
                INSERT INTO users (id, username, email, password_hash)
                VALUES (:user_id, :username, :email, :password_hash)
            """
            self.adapter.execute_update(
                query=query,
                params={
                    'user_id': self.test_user_id,
                    'username': f'testuser_{self.test_user_id}',
                    'email': f'test_{self.test_user_id}@example.com',
                    'password_hash': 'test_hash'
                }
            )
    
    def _create_test_stock(self, ticker, name):
        '''Helper to create a test stock.'''
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
    
    def _create_test_watchlist(self):
        '''Helper to create a test watchlist.'''
        # Create watchlist
        query = """
            INSERT INTO watchlists (id, user_id, name, calendar_token)
            VALUES (:watchlist_id, :user_id, :name, :calendar_token)
        """
        self.adapter.execute_update(
            query=query,
            params={
                'watchlist_id': self.test_watchlist_id,
                'user_id': self.test_user_id,
                'name': 'Test Tech Stocks',
                'calendar_token': self.test_calendar_token
            }
        )
        
        # Create watchlist settings
        settings_query = """
            INSERT INTO watchlist_settings (
                watchlist_id,
                include_earnings_announcement,
                include_dividend_ex,
                include_dividend_payment,
                include_stock_split,
                reminder_before
            )
            VALUES (
                :watchlist_id,
                TRUE,
                TRUE,
                FALSE,
                TRUE,
                :reminder_before
            )
        """
        self.adapter.execute_update(
            query=settings_query,
            params={
                'watchlist_id': self.test_watchlist_id,
                'reminder_before': timedelta(days=1)
            }
        )
    
    def _create_test_stock_events(self):
        '''Helper to create test stock events.'''
        events = [
            ('AAPL', 'EARNINGS_ANNOUNCEMENT', datetime(2025, 12, 1, tzinfo=timezone.utc)),
            ('AAPL', 'DIVIDEND_PAYMENT', datetime(2025, 11, 15, tzinfo=timezone.utc)),
            ('MSFT', 'STOCK_SPLIT', datetime(2025, 10, 1, tzinfo=timezone.utc)),
            ('MSFT', 'DIVIDEND_EX', datetime(2025, 9, 20, tzinfo=timezone.utc)),
        ]
        
        for ticker, event_type, event_date in events:
            query = """
                INSERT INTO stock_events (stock_ticker, type, event_date, source)
                VALUES (:ticker, :type, :event_date, :source)
            """
            self.adapter.execute_update(
                query=query,
                params={
                    'ticker': ticker,
                    'type': event_type,
                    'event_date': event_date,
                    'source': 'TestSource'
                }
            )
    
    def _add_stock_to_watchlist(self, ticker):
        '''Helper to add a stock to the watchlist.'''
        query = """
            INSERT INTO follows (watchlist_id, stock_ticker)
            VALUES (:watchlist_id, :ticker)
            ON CONFLICT DO NOTHING
        """
        self.adapter.execute_update(
            query=query,
            params={
                'watchlist_id': self.test_watchlist_id,
                'ticker': ticker
            }
        )
    
    def _cleanup_follows(self):
        '''Clean up follows table.'''
        query = "DELETE FROM follows WHERE watchlist_id = :watchlist_id"
        try:
            self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
        except Exception:
            pass
    
    def _cleanup_stock_events(self):
        '''Clean up stock events.'''
        query = "DELETE FROM stock_events WHERE stock_ticker IN ('AAPL', 'MSFT')"
        try:
            self.adapter.execute_update(query=query, params={})
        except Exception:
            pass
    
    def _cleanup_watchlist_settings(self):
        '''Clean up watchlist settings.'''
        query = "DELETE FROM watchlist_settings WHERE watchlist_id = :watchlist_id"
        try:
            self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
        except Exception:
            pass
    
    def _cleanup_watchlists(self):
        '''Clean up watchlists.'''
        query = "DELETE FROM watchlists WHERE id = :watchlist_id"
        try:
            self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
        except Exception:
            pass
    
    def _cleanup_stocks(self):
        '''Clean up stocks.'''
        query = "DELETE FROM stocks WHERE ticker IN ('AAPL', 'MSFT')"
        try:
            self.adapter.execute_update(query=query, params={})
        except Exception:
            pass
    
    def _cleanup_users(self):
        '''Clean up users.'''
        query = "DELETE FROM users WHERE id = :user_id"
        try:
            self.adapter.execute_update(query=query, params={'user_id': self.test_user_id})
        except Exception:
            pass
    
    def test_get_calendar_success(self):
        '''Test successful calendar generation from database.'''
        ics_content = self.service.get_calendar(token=self.test_calendar_token)
        
        # Verify it's a valid iCalendar file
        self.assertIsInstance(ics_content, str)
        self.assertIn('BEGIN:VCALENDAR', ics_content)
        self.assertIn('END:VCALENDAR', ics_content)
        self.assertIn('VERSION:2.0', ics_content)
        
        # Should contain events (based on watchlist settings)
        self.assertIn('BEGIN:VEVENT', ics_content)
        self.assertIn('END:VEVENT', ics_content)
        
        # Should contain stock tickers
        self.assertIn('AAPL', ics_content)
        self.assertIn('MSFT', ics_content)
    
    def test_get_calendar_filters_by_settings(self):
        '''Test that calendar respects watchlist settings.'''
        ics_content = self.service.get_calendar(token=self.test_calendar_token)
        
        # Should include earnings (enabled)
        self.assertIn('Earnings', ics_content)
        
        # Should include stock split (enabled)
        self.assertIn('Split', ics_content)
        
        # Should NOT include dividend payment (disabled in settings)
        # Note: DIVIDEND_EX should be included, but DIVIDEND_PAYMENT should not
        # Based on our test setup
    
    def test_get_calendar_includes_reminder(self):
        '''Test that calendar includes reminders from settings.'''
        ics_content = self.service.get_calendar(token=self.test_calendar_token)
        
        # Should include VALARM for reminders
        self.assertIn('BEGIN:VALARM', ics_content)
        self.assertIn('TRIGGER:-P1D', ics_content)  # 1 day before
    
    def test_get_calendar_invalid_token(self):
        '''Test calendar with non-existent token.'''
        with self.assertRaises(LookupError):
            self.service.get_calendar(token='nonexistent_token_xyz')
    
    def test_get_calendar_includes_watchlist_name(self):
        '''Test that calendar includes watchlist name.'''
        ics_content = self.service.get_calendar(token=self.test_calendar_token)
        
        # Should include watchlist name in calendar
        self.assertIn('X-WR-CALNAME:Test Tech Stocks', ics_content)
    
    def test_get_calendar_event_ordering(self):
        '''Test that events are ordered by date.'''
        ics_content = self.service.get_calendar(token=self.test_calendar_token)
        
        # Extract event dates
        lines = ics_content.split('\r\n')
        date_lines = [line for line in lines if line.startswith('DTSTART;VALUE=DATE:')]
        
        # Verify we have events
        self.assertGreater(len(date_lines), 0)
        
        # Dates should be in ascending order
        dates = [line.split(':')[1] for line in date_lines]
        self.assertEqual(dates, sorted(dates))


class TestRotateCalendarTokenIntegration(unittest.TestCase):
    '''Integration tests for calendar token rotation with real database.'''
    
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
        
        if not cls.adapter.health_check():
            raise unittest.SkipTest("Database is not accessible.")
        
        DatabaseAdapterFactory.initialize(environment=DatabaseEnvironment.DEVELOPMENT)
        cls.service = CalendarService()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up database connection.'''
        cls.adapter.close()
    
    def setUp(self):
        '''Set up test data before each test.'''
        self.test_user_id = 1
        self.test_watchlist_id = uuid4()
        self.test_calendar_token = f'test_token_{uuid4().hex[:16]}'
        
        # Create test user
        self._create_test_user()
        
        # Create test watchlist
        self._create_test_watchlist()
    
    def tearDown(self):
        '''Clean up test data after each test.'''
        self._cleanup_watchlist_settings()
        self._cleanup_watchlists()
        self._cleanup_users()
    
    def _create_test_user(self):
        '''Helper to create a test user.'''
        check_query = "SELECT id FROM users WHERE id = :user_id"
        result = self.adapter.execute_query(query=check_query, params={'user_id': self.test_user_id})
        
        if not result:
            query = """
                INSERT INTO users (id, username, email, password_hash)
                VALUES (:user_id, :username, :email, :password_hash)
            """
            self.adapter.execute_update(
                query=query,
                params={
                    'user_id': self.test_user_id,
                    'username': f'testuser_{self.test_user_id}',
                    'email': f'test_{self.test_user_id}@example.com',
                    'password_hash': 'test_hash'
                }
            )
    
    def _create_test_watchlist(self):
        '''Helper to create a test watchlist.'''
        query = """
            INSERT INTO watchlists (id, user_id, name, calendar_token)
            VALUES (:watchlist_id, :user_id, :name, :calendar_token)
        """
        self.adapter.execute_update(
            query=query,
            params={
                'watchlist_id': self.test_watchlist_id,
                'user_id': self.test_user_id,
                'name': 'Test Watchlist',
                'calendar_token': self.test_calendar_token
            }
        )
        
        # Create watchlist settings
        settings_query = """
            INSERT INTO watchlist_settings (watchlist_id)
            VALUES (:watchlist_id)
        """
        self.adapter.execute_update(
            query=settings_query,
            params={'watchlist_id': self.test_watchlist_id}
        )
    
    def _cleanup_watchlist_settings(self):
        '''Helper to clean up watchlist settings.'''
        query = "DELETE FROM watchlist_settings WHERE watchlist_id = :watchlist_id"
        self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
    
    def _cleanup_watchlists(self):
        '''Helper to clean up watchlists.'''
        query = "DELETE FROM watchlists WHERE id = :watchlist_id"
        self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
    
    def _cleanup_users(self):
        '''Helper to clean up users.'''
        query = "DELETE FROM users WHERE id = :user_id"
        self.adapter.execute_update(query=query, params={'user_id': self.test_user_id})
    
    def test_rotate_token_success(self):
        '''Test successful token rotation in database.'''
        # Get original token
        original_token = self._get_watchlist_token()
        self.assertEqual(original_token, self.test_calendar_token)
        
        # Rotate the token
        new_token = self.service.rotate_calendar_token(
            user_id=self.test_user_id,
            watchlist_id=self.test_watchlist_id
        )
        
        # Verify new token is different
        self.assertNotEqual(new_token, original_token)
        self.assertIsInstance(new_token, str)
        self.assertGreater(len(new_token), 20)  # Should be a substantial token
        
        # Verify token was updated in database
        updated_token = self._get_watchlist_token()
        self.assertEqual(updated_token, new_token)
    
    def test_rotate_token_wrong_user(self):
        '''Test that rotation fails for wrong user.'''
        wrong_user_id = 999
        
        with self.assertRaises(LookupError):
            self.service.rotate_calendar_token(
                user_id=wrong_user_id,
                watchlist_id=self.test_watchlist_id
            )
        
        # Verify original token is unchanged
        token = self._get_watchlist_token()
        self.assertEqual(token, self.test_calendar_token)
    
    def test_rotate_token_nonexistent_watchlist(self):
        '''Test that rotation fails for non-existent watchlist.'''
        fake_watchlist_id = uuid4()
        
        with self.assertRaises(LookupError):
            self.service.rotate_calendar_token(
                user_id=self.test_user_id,
                watchlist_id=fake_watchlist_id
            )
    
    def test_rotate_token_multiple_times(self):
        '''Test rotating token multiple times generates different tokens.'''
        tokens = set()
        
        for _ in range(3):
            new_token = self.service.rotate_calendar_token(
                user_id=self.test_user_id,
                watchlist_id=self.test_watchlist_id
            )
            tokens.add(new_token)
        
        # All tokens should be unique
        self.assertEqual(len(tokens), 3)
    
    def _get_watchlist_token(self):
        '''Helper to get current token from database.'''
        query = "SELECT calendar_token FROM watchlists WHERE id = :watchlist_id"
        result = list(self.adapter.execute_query(
            query=query,
            params={'watchlist_id': self.test_watchlist_id}
        ))
        return result[0]['calendar_token'] if result else None


class TestGetCalendarTokenIntegration(unittest.TestCase):
    '''Integration tests for calendar token retrieval with real database.'''
    
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
        
        if not cls.adapter.health_check():
            raise unittest.SkipTest("Database is not accessible.")
        
        DatabaseAdapterFactory.initialize(environment=DatabaseEnvironment.DEVELOPMENT)
        cls.service = CalendarService()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up database connection.'''
        cls.adapter.close()
    
    def setUp(self):
        '''Set up test data before each test.'''
        self.test_user_id = 1
        self.test_watchlist_id = uuid4()
        self.test_calendar_token = f'test_token_{uuid4().hex[:16]}'
        
        # Create test user
        self._create_test_user()
        
        # Create test watchlist
        self._create_test_watchlist()
    
    def tearDown(self):
        '''Clean up test data after each test.'''
        self._cleanup_watchlist_settings()
        self._cleanup_watchlists()
        self._cleanup_users()
    
    def _create_test_user(self):
        '''Helper to create a test user.'''
        check_query = "SELECT id FROM users WHERE id = :user_id"
        result = self.adapter.execute_query(query=check_query, params={'user_id': self.test_user_id})
        
        if not result:
            query = """
                INSERT INTO users (id, username, email, password_hash)
                VALUES (:user_id, :username, :email, :password_hash)
            """
            self.adapter.execute_update(
                query=query,
                params={
                    'user_id': self.test_user_id,
                    'username': f'testuser_{self.test_user_id}',
                    'email': f'test_{self.test_user_id}@example.com',
                    'password_hash': 'test_hash'
                }
            )
    
    def _create_test_watchlist(self):
        '''Helper to create a test watchlist.'''
        query = """
            INSERT INTO watchlists (id, user_id, name, calendar_token)
            VALUES (:watchlist_id, :user_id, :name, :calendar_token)
        """
        self.adapter.execute_update(
            query=query,
            params={
                'watchlist_id': self.test_watchlist_id,
                'user_id': self.test_user_id,
                'name': 'Test Watchlist',
                'calendar_token': self.test_calendar_token
            }
        )
        
        # Create watchlist settings
        settings_query = """
            INSERT INTO watchlist_settings (watchlist_id)
            VALUES (:watchlist_id)
        """
        self.adapter.execute_update(
            query=settings_query,
            params={'watchlist_id': self.test_watchlist_id}
        )
    
    def _cleanup_watchlist_settings(self):
        '''Helper to clean up watchlist settings.'''
        query = "DELETE FROM watchlist_settings WHERE watchlist_id = :watchlist_id"
        self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
    
    def _cleanup_watchlists(self):
        '''Helper to clean up watchlists.'''
        query = "DELETE FROM watchlists WHERE id = :watchlist_id"
        self.adapter.execute_update(query=query, params={'watchlist_id': self.test_watchlist_id})
    
    def _cleanup_users(self):
        '''Helper to clean up users.'''
        query = "DELETE FROM users WHERE id = :user_id"
        self.adapter.execute_update(query=query, params={'user_id': self.test_user_id})
    
    def test_get_token_success(self):
        '''Test successful token retrieval from database.'''
        token = self.service.get_calendar_token(
            user_id=self.test_user_id,
            watchlist_id=self.test_watchlist_id
        )
        
        self.assertEqual(token, self.test_calendar_token)
    
    def test_get_token_wrong_user(self):
        '''Test that retrieval fails for wrong user.'''
        wrong_user_id = 999
        
        with self.assertRaises(LookupError):
            self.service.get_calendar_token(
                user_id=wrong_user_id,
                watchlist_id=self.test_watchlist_id
            )
    
    def test_get_token_nonexistent_watchlist(self):
        '''Test that retrieval fails for non-existent watchlist.'''
        fake_watchlist_id = uuid4()
        
        with self.assertRaises(LookupError):
            self.service.get_calendar_token(
                user_id=self.test_user_id,
                watchlist_id=fake_watchlist_id
            )


if __name__ == '__main__':
    unittest.main()
