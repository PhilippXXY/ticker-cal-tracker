# Disclaimer: Created by GitHub Copilot
'''
Unit tests for WatchlistService.
'''

import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timezone

from src.app.services.watchlists_service import WatchlistService
from src.models.stock_event_model import EventType
from src.models.stock_model import Stock


class TestWatchlistServiceInitialization(unittest.TestCase):
    '''Test WatchlistService initialization.'''
    
    @patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance')
    @patch('src.app.services.watchlists_service.StocksService')
    def test_init(self, mock_stocks_service, mock_db_factory):
        '''Test service initializes with correct dependencies.'''
        mock_db = Mock()
        mock_db_factory.return_value = mock_db
        
        service = WatchlistService()
        
        self.assertIsNotNone(service.db)
        self.assertIsNotNone(service.stocks_service)
        mock_db_factory.assert_called_once()


class TestCreateWatchlist(unittest.TestCase):
    '''Test watchlist creation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        self.mock_stocks_service = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService', return_value=self.mock_stocks_service):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.app.utils.calendar_utils.generate_calendar_url')
    def test_create_watchlist_success(self, mock_gen_url):
        '''Test successful watchlist creation.'''
        mock_gen_url.return_value = 'https://example.com/cal/abc123'
        
        # Mock INSERT returning watchlist_id
        self.mock_db.execute_query.return_value = [{'id': self.watchlist_id}]
        self.mock_db.execute_update.return_value = 1
        
        # Mock get_watchlist_by_id
        expected_watchlist = {
            'id': self.watchlist_id,
            'name': 'Tech Stocks',
            'calendar_url': 'https://example.com/cal/abc123',
            'created_at': datetime.now(timezone.utc),
            'include_earnings_announcement': True,
            'include_dividend_ex': True,
            'include_dividend_declaration': False,
            'include_dividend_record': False,
            'include_dividend_payment': False,
            'include_stock_split': True,
        }
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=expected_watchlist):
            watchlist_settings = {
                EventType.EARNINGS_ANNOUNCEMENT: True,
                EventType.DIVIDEND_EX: True,
                EventType.DIVIDEND_DECLARATION: False,
                EventType.DIVIDEND_RECORD: False,
                EventType.DIVIDEND_PAYMENT: False,
                EventType.STOCK_SPLIT: True,
            }
            
            result = self.service.create_watchlist(
                user_id=self.user_id,
                name='Tech Stocks',
                watchlist_settings=watchlist_settings,
            )
        
        self.assertEqual(result['id'], self.watchlist_id)
        self.assertEqual(result['name'], 'Tech Stocks')
        self.mock_db.execute_query.assert_called_once()
        self.mock_db.execute_update.assert_called_once()
    
    def test_create_watchlist_invalid_user_id(self):
        '''Test creation fails with non-UUID user_id.'''
        watchlist_settings = {EventType.EARNINGS_ANNOUNCEMENT: True}
        
        with self.assertRaises(ValueError) as context:
            self.service.create_watchlist(
                user_id='not-a-uuid',  # type: ignore
                name='Test',
                watchlist_settings=watchlist_settings,
            )
        
        self.assertIn('user_id must be a UUID instance', str(context.exception))
    
    def test_create_watchlist_empty_name(self):
        '''Test creation fails with empty name.'''
        watchlist_settings = {EventType.EARNINGS_ANNOUNCEMENT: True}
        
        with self.assertRaises(ValueError) as context:
            self.service.create_watchlist(
                user_id=self.user_id,
                name='',
                watchlist_settings=watchlist_settings,
            )
        
        self.assertIn('name is required', str(context.exception))
    
    def test_create_watchlist_no_settings(self):
        '''Test creation fails without settings.'''
        with self.assertRaises(ValueError) as context:
            self.service.create_watchlist(
                user_id=self.user_id,
                name='Test',
                watchlist_settings={},
            )
        
        self.assertIn('settings are required', str(context.exception))
    
    @patch('src.app.utils.calendar_utils.generate_calendar_url')
    def test_create_watchlist_db_error(self, mock_gen_url):
        '''Test creation handles database errors.'''
        mock_gen_url.return_value = 'https://example.com/cal/abc123'
        self.mock_db.execute_query.side_effect = Exception('Database error')
        
        watchlist_settings = {EventType.EARNINGS_ANNOUNCEMENT: True}
        
        with self.assertRaises(Exception) as context:
            self.service.create_watchlist(
                user_id=self.user_id,
                name='Test',
                watchlist_settings=watchlist_settings,
            )
        
        self.assertIn('Failed to create watchlist', str(context.exception))


class TestGetAllWatchlistsForUser(unittest.TestCase):
    '''Test fetching all watchlists for a user.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
    
    def test_get_all_watchlists_success(self):
        '''Test successful fetch of all watchlists.'''
        mock_results = [
            {
                'id': uuid4(),
                'name': 'Tech Stocks',
                'calendar_url': 'https://example.com/cal1',
                'created_at': datetime.now(timezone.utc),
                'include_earnings_announcement': True,
                'include_dividend_ex': True,
            },
            {
                'id': uuid4(),
                'name': 'Energy Stocks',
                'calendar_url': 'https://example.com/cal2',
                'created_at': datetime.now(timezone.utc),
                'include_earnings_announcement': False,
                'include_dividend_ex': True,
            },
        ]
        
        self.mock_db.execute_query.return_value = mock_results
        
        result = self.service.get_all_watchlists_for_user(user_id=self.user_id)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Tech Stocks')
        self.assertEqual(result[1]['name'], 'Energy Stocks')
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_all_watchlists_empty(self):
        '''Test fetch returns empty list when no watchlists.'''
        self.mock_db.execute_query.return_value = []
        
        result = self.service.get_all_watchlists_for_user(user_id=self.user_id)
        
        self.assertEqual(len(result), 0)
    
    def test_get_all_watchlists_invalid_user_id(self):
        '''Test fetch fails with non-UUID user_id.'''
        with self.assertRaises(TypeError) as context:
            self.service.get_all_watchlists_for_user(user_id='not-a-uuid')  # type: ignore
        
        self.assertIn('user_id must be a UUID instance', str(context.exception))
    
    def test_get_all_watchlists_db_error(self):
        '''Test fetch handles database errors.'''
        self.mock_db.execute_query.side_effect = Exception('Database error')
        
        with self.assertRaises(Exception) as context:
            self.service.get_all_watchlists_for_user(user_id=self.user_id)
        
        self.assertIn('Failed to fetch watchlists for user', str(context.exception))


class TestGetWatchlistById(unittest.TestCase):
    '''Test fetching a specific watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_get_watchlist_by_id_success(self):
        '''Test successful fetch of watchlist by ID.'''
        mock_result = {
            'id': self.watchlist_id,
            'name': 'Tech Stocks',
            'calendar_url': 'https://example.com/cal',
            'created_at': datetime.now(timezone.utc),
            'include_earnings_announcement': True,
        }
        
        self.mock_db.execute_query.return_value = [mock_result]
        
        result = self.service.get_watchlist_by_id(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], self.watchlist_id) # pyright: ignore[reportOptionalSubscript]
        self.assertEqual(result['name'], 'Tech Stocks') # pyright: ignore[reportOptionalSubscript]
    
    def test_get_watchlist_by_id_not_found(self):
        '''Test fetch returns None when watchlist not found.'''
        self.mock_db.execute_query.return_value = []
        
        result = self.service.get_watchlist_by_id(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertIsNone(result)
    
    def test_get_watchlist_by_id_db_error(self):
        '''Test fetch handles database errors.'''
        self.mock_db.execute_query.side_effect = Exception('Database error')
        
        with self.assertRaises(Exception) as context:
            self.service.get_watchlist_by_id(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertIn('Failed to fetch watchlist', str(context.exception))


class TestGetWatchlistStocks(unittest.TestCase):
    '''Test fetching stocks in a watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_get_watchlist_stocks_success(self):
        '''Test successful fetch of watchlist stocks.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        mock_stocks = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'last_updated': datetime.now(timezone.utc),
                'followed_at': datetime.now(timezone.utc),
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corp.',
                'last_updated': datetime.now(timezone.utc),
                'followed_at': datetime.now(timezone.utc),
            },
        ]
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_query.return_value = mock_stocks
            
            result = self.service.get_watchlist_stocks(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ticker'], 'AAPL')
        self.assertEqual(result[1]['ticker'], 'MSFT')
    
    def test_get_watchlist_stocks_not_found(self):
        '''Test fetch fails when watchlist not found.'''
        with patch.object(self.service, 'get_watchlist_by_id', return_value=None):
            with self.assertRaises(ValueError) as context:
                self.service.get_watchlist_stocks(user_id=self.user_id, watchlist_id=self.watchlist_id)
            
            self.assertIn('Watchlist not found', str(context.exception))
    
    def test_get_watchlist_stocks_empty(self):
        '''Test fetch returns empty list when no stocks.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_query.return_value = []
            
            result = self.service.get_watchlist_stocks(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertEqual(len(result), 0)
    
    def test_get_watchlist_stocks_db_error(self):
        '''Test fetch handles database errors.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_query.side_effect = Exception('Database error')
            
            with self.assertRaises(Exception) as context:
                self.service.get_watchlist_stocks(user_id=self.user_id, watchlist_id=self.watchlist_id)
            
            self.assertIn('Failed to fetch watchlist stocks', str(context.exception))


class TestUpdateWatchlist(unittest.TestCase):
    '''Test updating watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_update_watchlist_name_only(self):
        '''Test updating watchlist name only.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Old Name'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 1
            
            result = self.service.update_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                name='New Name',
            )
        
        self.assertTrue(result)
        self.mock_db.execute_update.assert_called_once()
    
    def test_update_watchlist_settings_only(self):
        '''Test updating watchlist settings only.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        watchlist_settings = {
            EventType.EARNINGS_ANNOUNCEMENT: False,
            EventType.DIVIDEND_EX: True,
        }
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 1
            
            result = self.service.update_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                watchlist_settings=watchlist_settings,
            )
        
        self.assertTrue(result)
        self.mock_db.execute_update.assert_called_once()
    
    def test_update_watchlist_name_and_settings(self):
        '''Test updating both name and settings.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Old Name'}
        watchlist_settings = {EventType.EARNINGS_ANNOUNCEMENT: False}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 1
            
            result = self.service.update_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                name='New Name',
                watchlist_settings=watchlist_settings,
            )
        
        self.assertTrue(result)
        self.assertEqual(self.mock_db.execute_update.call_count, 2)
    
    def test_update_watchlist_not_found(self):
        '''Test update fails when watchlist not found.'''
        with patch.object(self.service, 'get_watchlist_by_id', return_value=None):
            result = self.service.update_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                name='New Name',
            )
        
        self.assertFalse(result)
    
    def test_update_watchlist_empty_name(self):
        '''Test update fails with empty name.'''
        with self.assertRaises(ValueError) as context:
            self.service.update_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                name='',
            )
        
        self.assertIn('name must not be empty', str(context.exception))


class TestAddStockToWatchlist(unittest.TestCase):
    '''Test adding stock to watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        self.mock_stocks_service = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService', return_value=self.mock_stocks_service):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_add_stock_success(self):
        '''Test successfully adding stock to watchlist.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        mock_stock = Stock(name='Apple Inc.', symbol='AAPL', last_updated=datetime.now(timezone.utc))
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_stocks_service.get_stock_from_ticker.return_value = mock_stock
            self.mock_db.execute_update.return_value = 1
            
            result = self.service.add_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='AAPL',
            )
        
        self.assertTrue(result)
        self.mock_stocks_service.get_stock_from_ticker.assert_called_once_with(ticker='AAPL')
        self.mock_db.execute_update.assert_called_once()
    
    def test_add_stock_normalizes_ticker(self):
        '''Test ticker is normalized to uppercase.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        mock_stock = Stock(name='Apple Inc.', symbol='AAPL', last_updated=datetime.now(timezone.utc))
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_stocks_service.get_stock_from_ticker.return_value = mock_stock
            self.mock_db.execute_update.return_value = 1
            
            self.service.add_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='  aapl  ',
            )
        
        self.mock_stocks_service.get_stock_from_ticker.assert_called_once_with(ticker='AAPL')
    
    def test_add_stock_empty_ticker(self):
        '''Test add fails with empty ticker.'''
        with self.assertRaises(ValueError) as context:
            self.service.add_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='',
            )
        
        self.assertIn('ticker must not be empty', str(context.exception))
    
    def test_add_stock_watchlist_not_found(self):
        '''Test add fails when watchlist not found.'''
        with patch.object(self.service, 'get_watchlist_by_id', return_value=None):
            with self.assertRaises(LookupError) as context:
                self.service.add_stock_to_watchlist(
                    user_id=self.user_id,
                    watchlist_id=self.watchlist_id,
                    stock_ticker='AAPL',
                )
            
            self.assertIn('Watchlist', str(context.exception))
            self.assertIn('not found', str(context.exception))
    
    def test_add_stock_stock_not_found(self):
        '''Test add fails when stock not found.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_stocks_service.get_stock_from_ticker.side_effect = Exception('Stock not found')
            
            with self.assertRaises(LookupError) as context:
                self.service.add_stock_to_watchlist(
                    user_id=self.user_id,
                    watchlist_id=self.watchlist_id,
                    stock_ticker='INVALID',
                )
            
            self.assertIn('Stock', str(context.exception))
            self.assertIn('not found', str(context.exception))
    
    def test_add_stock_db_error(self):
        '''Test add handles database errors.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        mock_stock = Stock(name='Apple Inc.', symbol='AAPL', last_updated=datetime.now(timezone.utc))
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_stocks_service.get_stock_from_ticker.return_value = mock_stock
            self.mock_db.execute_update.side_effect = Exception('Database error')
            
            with self.assertRaises(Exception) as context:
                self.service.add_stock_to_watchlist(
                    user_id=self.user_id,
                    watchlist_id=self.watchlist_id,
                    stock_ticker='AAPL',
                )
            
            self.assertIn('Failed to add stock to watchlist', str(context.exception))


class TestDeleteWatchlist(unittest.TestCase):
    '''Test deleting watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_delete_watchlist_success(self):
        '''Test successful watchlist deletion.'''
        self.mock_db.execute_update.return_value = 1
        
        result = self.service.delete_watchlist(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertTrue(result)
        self.mock_db.execute_update.assert_called_once()
    
    def test_delete_watchlist_not_found(self):
        '''Test delete returns False when watchlist not found.'''
        self.mock_db.execute_update.return_value = 0
        
        result = self.service.delete_watchlist(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertFalse(result)
    
    def test_delete_watchlist_db_error(self):
        '''Test delete handles database errors.'''
        self.mock_db.execute_update.side_effect = Exception('Database error')
        
        with self.assertRaises(Exception) as context:
            self.service.delete_watchlist(user_id=self.user_id, watchlist_id=self.watchlist_id)
        
        self.assertIn('Failed to delete watchlist', str(context.exception))


class TestRemoveStockFromWatchlist(unittest.TestCase):
    '''Test removing stock from watchlist.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.watchlists_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.watchlists_service.StocksService'):
                self.service = WatchlistService()
        
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    def test_remove_stock_success(self):
        '''Test successfully removing stock from watchlist.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 1
            
            result = self.service.remove_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='AAPL',
            )
        
        self.assertTrue(result)
        self.mock_db.execute_update.assert_called_once()
    
    def test_remove_stock_normalizes_ticker(self):
        '''Test ticker is normalized to uppercase.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 1
            
            self.service.remove_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='  aapl  ',
            )
        
        # Verify the query was called with uppercase ticker
        call_args = self.mock_db.execute_update.call_args
        self.assertEqual(call_args[1]['params']['ticker'], 'AAPL')
    
    def test_remove_stock_empty_ticker(self):
        '''Test remove fails with empty ticker.'''
        with self.assertRaises(ValueError) as context:
            self.service.remove_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='',
            )
        
        self.assertIn('ticker must not be empty', str(context.exception))
    
    def test_remove_stock_watchlist_not_found(self):
        '''Test remove fails when watchlist not found.'''
        with patch.object(self.service, 'get_watchlist_by_id', return_value=None):
            with self.assertRaises(LookupError) as context:
                self.service.remove_stock_to_watchlist(
                    user_id=self.user_id,
                    watchlist_id=self.watchlist_id,
                    stock_ticker='AAPL',
                )
            
            self.assertIn('Watchlist', str(context.exception))
            self.assertIn('not found', str(context.exception))
    
    def test_remove_stock_not_in_watchlist(self):
        '''Test remove returns False when stock not in watchlist.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.return_value = 0
            
            result = self.service.remove_stock_to_watchlist(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id,
                stock_ticker='AAPL',
            )
        
        self.assertFalse(result)
    
    def test_remove_stock_db_error(self):
        '''Test remove handles database errors.'''
        mock_watchlist = {'id': self.watchlist_id, 'name': 'Tech Stocks'}
        
        with patch.object(self.service, 'get_watchlist_by_id', return_value=mock_watchlist):
            self.mock_db.execute_update.side_effect = Exception('Database error')
            
            with self.assertRaises(Exception) as context:
                self.service.remove_stock_to_watchlist(
                    user_id=self.user_id,
                    watchlist_id=self.watchlist_id,
                    stock_ticker='AAPL',
                )
            
            self.assertIn('Failed to remove stock from watchlist', str(context.exception))


if __name__ == '__main__':
    unittest.main()
