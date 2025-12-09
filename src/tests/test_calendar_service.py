# Disclaimer: Created by GitHub Copilot
'''
Unit tests for CalendarService.
'''

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.app.services.calendar_service import CalendarService
from src.models.stock_event_model import EventType


class TestCalendarServiceInitialization(unittest.TestCase):
    '''Test CalendarService initialization.'''
    
    @patch('src.app.services.calendar_service.DatabaseAdapterFactory.get_instance')
    def test_init(self, mock_db_factory):
        '''Test service initializes with database adapter.'''
        mock_db = Mock()
        mock_db_factory.return_value = mock_db
        
        service = CalendarService()
        
        self.assertIsNotNone(service.db)
        mock_db_factory.assert_called_once()


class TestGetCalendar(unittest.TestCase):
    '''Test calendar retrieval and generation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.calendar_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            self.service = CalendarService()
        
        self.calendar_token = 'test_token_12345'
        self.watchlist_id = uuid4()
        self.default_watchlist = {
            'id': self.watchlist_id,
            'name': 'Tech Stocks',
            'reminder_before': timedelta(days=1),
        }
    
    def _set_db_results(self, *, watchlist=None, events=None):
        watchlist_rows = [watchlist or self.default_watchlist]
        event_rows = events if events is not None else []
        self.mock_db.execute_query.side_effect = [watchlist_rows, event_rows]
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_success(self, mock_build_ics):
        '''Test successful calendar generation.'''
        events = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'stock_last_updated': datetime(2025, 1, 1, tzinfo=timezone.utc),
                'type': 'EARNINGS_ANNOUNCEMENT',
                'event_date': datetime(2025, 2, 1, tzinfo=timezone.utc),
                'event_last_updated': datetime(2025, 1, 15, tzinfo=timezone.utc),
                'source': 'AlphaVantage',
            }
        ]
        self._set_db_results(events=events)
        mock_build_ics.return_value = 'BEGIN:VCALENDAR\r\n...\r\nEND:VCALENDAR\r\n'
        
        result = self.service.get_calendar(token=self.calendar_token)
        
        self.assertEqual(self.mock_db.execute_query.call_count, 2)
        metadata_call, events_call = self.mock_db.execute_query.call_args_list
        self.assertEqual(metadata_call.kwargs['params']['token'], self.calendar_token)
        self.assertEqual(events_call.kwargs['params']['watchlist_id'], self.watchlist_id)
        
        mock_build_ics.assert_called_once()
        call_args = mock_build_ics.call_args
        self.assertEqual(len(call_args.kwargs['stock_events']), 1)
        self.assertEqual(call_args.kwargs['watchlist_name'], 'Tech Stocks')
        self.assertEqual(call_args.kwargs['reminder_before'], timedelta(days=1))
        self.assertIn('BEGIN:VCALENDAR', result)
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_multiple_events(self, mock_build_ics):
        '''Test calendar generation with multiple events.'''
        events = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'stock_last_updated': datetime(2025, 1, 1, tzinfo=timezone.utc),
                'type': 'EARNINGS_ANNOUNCEMENT',
                'event_date': datetime(2025, 2, 1, tzinfo=timezone.utc),
                'event_last_updated': datetime(2025, 1, 15, tzinfo=timezone.utc),
                'source': 'AlphaVantage',
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'stock_last_updated': datetime(2025, 1, 2, tzinfo=timezone.utc),
                'type': 'DIVIDEND_PAYMENT',
                'event_date': datetime(2025, 3, 1, tzinfo=timezone.utc),
                'event_last_updated': datetime(2025, 2, 1, tzinfo=timezone.utc),
                'source': 'Finnhub',
            }
        ]
        self._set_db_results(events=events)
        mock_build_ics.return_value = 'calendar_content'
        
        self.service.get_calendar(token=self.calendar_token)
        
        stock_events = mock_build_ics.call_args.kwargs['stock_events']
        self.assertEqual(len(stock_events), 2)
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_empty_results(self, mock_build_ics):
        '''Test calendar generation with no events still returns metadata name.'''
        no_name_watchlist = {
            'id': self.watchlist_id,
            'name': None,
            'reminder_before': timedelta(days=1),
        }
        self._set_db_results(watchlist=no_name_watchlist, events=[])
        mock_build_ics.return_value = 'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'
        
        self.service.get_calendar(token=self.calendar_token)
        
        call_args = mock_build_ics.call_args
        self.assertEqual(len(call_args.kwargs['stock_events']), 0)
        self.assertEqual(call_args.kwargs['watchlist_name'], 'Stock Events')
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_no_reminder(self, mock_build_ics):
        '''Test calendar generation without reminder.'''
        no_reminder_watchlist = {
            'id': self.watchlist_id,
            'name': 'Growth Stocks',
            'reminder_before': None,
        }
        events = [
            {
                'ticker': 'TSLA',
                'name': 'Tesla Inc.',
                'stock_last_updated': datetime(2025, 1, 1, tzinfo=timezone.utc),
                'type': 'STOCK_SPLIT',
                'event_date': datetime(2025, 4, 1, tzinfo=timezone.utc),
                'event_last_updated': datetime(2025, 3, 1, tzinfo=timezone.utc),
                'source': 'AlphaVantage',
            }
        ]
        self._set_db_results(watchlist=no_reminder_watchlist, events=events)
        mock_build_ics.return_value = 'calendar_content'
        
        self.service.get_calendar(token=self.calendar_token)
        
        self.assertIsNone(mock_build_ics.call_args.kwargs['reminder_before'])
    
    def test_get_calendar_db_error(self):
        '''Test calendar generation handles database errors from metadata query.'''
        self.mock_db.execute_query.side_effect = Exception('Database connection failed')
        
        with self.assertRaises(Exception) as context:
            self.service.get_calendar(token=self.calendar_token)
        
        self.assertIn('Database connection failed', str(context.exception))
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_filters_event_types(self, mock_build_ics):
        '''Test that SQL query filters by watchlist settings.'''
        self._set_db_results(events=[])
        mock_build_ics.return_value = 'calendar_content'
        
        self.service.get_calendar(token=self.calendar_token)
        
        query = self.mock_db.execute_query.call_args_list[1].kwargs['query']
        self.assertIn('include_earnings_announcement', query)
        self.assertIn('include_dividend_ex', query)
        self.assertIn('include_dividend_payment', query)
        self.assertIn('include_stock_split', query)
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_uses_parameterized_query(self, mock_build_ics):
        '''Test that queries use parameter binding for security.'''
        self._set_db_results(events=[])
        mock_build_ics.return_value = 'calendar_content'
        
        token = 'secure_token_abc123'
        self.service.get_calendar(token=token)
        
        metadata_call, events_call = self.mock_db.execute_query.call_args_list
        self.assertIn(':token', metadata_call.kwargs['query'])
        self.assertEqual(metadata_call.kwargs['params']['token'], token)
        self.assertIn(':watchlist_id', events_call.kwargs['query'])
        self.assertEqual(events_call.kwargs['params']['watchlist_id'], self.watchlist_id)
        self.assertNotIn('LIKE', events_call.kwargs['query'])
    
    @patch('src.app.utils.calendar_utils.build_ics')
    def test_get_calendar_converts_stock_event_types(self, mock_build_ics):
        '''Test that event types are properly converted from strings.'''
        events = [
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet Inc.',
                'stock_last_updated': datetime.now(timezone.utc),
                'type': 'DIVIDEND_EX',
                'event_date': datetime(2025, 5, 1, tzinfo=timezone.utc),
                'event_last_updated': datetime.now(timezone.utc),
                'source': 'Finnhub',
            }
        ]
        self._set_db_results(events=events)
        mock_build_ics.return_value = 'calendar_content'
        
        self.service.get_calendar(token=self.calendar_token)
        
        stock_events = mock_build_ics.call_args.kwargs['stock_events']
        self.assertEqual(stock_events[0].type, EventType.DIVIDEND_EX)
    
    def test_get_calendar_missing_watchlist(self):
        '''Test LookupError raised when token not found.'''
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(LookupError):
            self.service.get_calendar(token='missing')
    
    def test_get_calendar_empty_token(self):
        '''Test validation for empty token input.'''
        with self.assertRaises(ValueError):
            self.service.get_calendar(token='   ')


class TestRotateCalendarToken(unittest.TestCase):
    '''Test calendar token rotation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.calendar_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            self.service = CalendarService()
        
        self.user_id = 1
        self.watchlist_id = uuid4()
    
    @patch('src.app.utils.calendar_utils.generate_calendar_token')
    def test_rotate_token_success(self, mock_generate_token):
        '''Test successful token rotation.'''
        new_token = 'new_secure_token_xyz789'
        mock_generate_token.return_value = new_token
        
        self.mock_db.execute_query.return_value = [{'calendar_token': new_token}]
        
        result = self.service.rotate_calendar_token(
            user_id=self.user_id,
            watchlist_id=self.watchlist_id
        )
        
        self.assertEqual(result, new_token)
        mock_generate_token.assert_called_once()
        
        # Verify database update was called with correct parameters
        self.mock_db.execute_query.assert_called_once()
        call_kwargs = self.mock_db.execute_query.call_args.kwargs
        self.assertIn('UPDATE watchlists', call_kwargs['query'])
        self.assertIn('calendar_token', call_kwargs['query'])
        self.assertEqual(call_kwargs['params']['new_token'], new_token)
        self.assertEqual(call_kwargs['params']['watchlist_id'], self.watchlist_id)
        self.assertEqual(call_kwargs['params']['user_id'], self.user_id)
    
    @patch('src.app.utils.calendar_utils.generate_calendar_token')
    def test_rotate_token_watchlist_not_found(self, mock_generate_token):
        '''Test LookupError raised when watchlist not found.'''
        mock_generate_token.return_value = 'new_token'
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(LookupError) as context:
            self.service.rotate_calendar_token(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('not found', str(context.exception).lower())
    
    @patch('src.app.utils.calendar_utils.generate_calendar_token')
    def test_rotate_token_wrong_user(self, mock_generate_token):
        '''Test that token rotation fails when watchlist doesn't belong to user.'''
        mock_generate_token.return_value = 'new_token'
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(LookupError):
            self.service.rotate_calendar_token(
                user_id=999,  # Different user
                watchlist_id=self.watchlist_id
            )
    
    def test_rotate_token_invalid_user_id(self):
        '''Test ValueError raised for invalid user_id type.'''
        with self.assertRaises(ValueError) as context:
            self.service.rotate_calendar_token(
                user_id='not-an-int', # pyright: ignore[reportArgumentType]
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('user_id must be an integer', str(context.exception))
    
    def test_rotate_token_invalid_watchlist_id(self):
        '''Test ValueError raised for invalid watchlist_id type.'''
        with self.assertRaises(ValueError) as context:
            self.service.rotate_calendar_token(
                user_id=self.user_id,
                watchlist_id='not-a-uuid' # pyright: ignore[reportArgumentType]
            )
        
        self.assertIn('watchlist_id must be a UUID', str(context.exception))
    
    @patch('src.app.utils.calendar_utils.generate_calendar_token')
    def test_rotate_token_uses_parameterized_query(self, mock_generate_token):
        '''Test that update uses parameterized query for security.'''
        mock_generate_token.return_value = 'token123'
        self.mock_db.execute_query.return_value = [{'calendar_token': 'token123'}]
        
        self.service.rotate_calendar_token(
            user_id=self.user_id,
            watchlist_id=self.watchlist_id
        )
        
        call_kwargs = self.mock_db.execute_query.call_args.kwargs
        self.assertIn(':new_token', call_kwargs['query'])
        self.assertIn(':watchlist_id', call_kwargs['query'])
        self.assertIn(':user_id', call_kwargs['query'])
    
    @patch('src.app.utils.calendar_utils.generate_calendar_token')
    def test_rotate_token_db_error(self, mock_generate_token):
        '''Test handling of database errors.'''
        mock_generate_token.return_value = 'new_token'
        self.mock_db.execute_query.side_effect = Exception('Database connection failed')
        
        with self.assertRaises(Exception) as context:
            self.service.rotate_calendar_token(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('Database connection failed', str(context.exception))


class TestGetCalendarToken(unittest.TestCase):
    '''Test calendar token retrieval.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.calendar_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            self.service = CalendarService()
        
        self.user_id = 1
        self.watchlist_id = uuid4()
        self.test_token = 'existing_token_abc123'
    
    def test_get_token_success(self):
        '''Test successful token retrieval.'''
        self.mock_db.execute_query.return_value = [{'calendar_token': self.test_token}]
        
        result = self.service.get_calendar_token(
            user_id=self.user_id,
            watchlist_id=self.watchlist_id
        )
        
        self.assertEqual(result, self.test_token)
        
        # Verify database query was called with correct parameters
        self.mock_db.execute_query.assert_called_once()
        call_kwargs = self.mock_db.execute_query.call_args.kwargs
        self.assertIn('SELECT calendar_token', call_kwargs['query'])
        self.assertIn('FROM watchlists', call_kwargs['query'])
        self.assertEqual(call_kwargs['params']['watchlist_id'], self.watchlist_id)
        self.assertEqual(call_kwargs['params']['user_id'], self.user_id)
    
    def test_get_token_watchlist_not_found(self):
        '''Test LookupError raised when watchlist not found.'''
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(LookupError) as context:
            self.service.get_calendar_token(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('not found', str(context.exception).lower())
    
    def test_get_token_wrong_user(self):
        '''Test that retrieval fails when watchlist doesn't belong to user.'''
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(LookupError):
            self.service.get_calendar_token(
                user_id=999,  # Different user
                watchlist_id=self.watchlist_id
            )
    
    def test_get_token_invalid_user_id(self):
        '''Test ValueError raised for invalid user_id type.'''
        with self.assertRaises(ValueError) as context:
            self.service.get_calendar_token(
                user_id='not-an-int', # pyright: ignore[reportArgumentType]
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('user_id must be an integer', str(context.exception))
    
    def test_get_token_invalid_watchlist_id(self):
        '''Test ValueError raised for invalid watchlist_id type.'''
        with self.assertRaises(ValueError) as context:
            self.service.get_calendar_token(
                user_id=self.user_id,
                watchlist_id='not-a-uuid' # pyright: ignore[reportArgumentType]
            )
        
        self.assertIn('watchlist_id must be a UUID', str(context.exception))
    
    def test_get_token_uses_parameterized_query(self):
        '''Test that query uses parameterized query for security.'''
        self.mock_db.execute_query.return_value = [{'calendar_token': self.test_token}]
        
        self.service.get_calendar_token(
            user_id=self.user_id,
            watchlist_id=self.watchlist_id
        )
        
        call_kwargs = self.mock_db.execute_query.call_args.kwargs
        self.assertIn(':watchlist_id', call_kwargs['query'])
        self.assertIn(':user_id', call_kwargs['query'])
    
    def test_get_token_db_error(self):
        '''Test handling of database errors.'''
        self.mock_db.execute_query.side_effect = Exception('Database connection failed')
        
        with self.assertRaises(Exception) as context:
            self.service.get_calendar_token(
                user_id=self.user_id,
                watchlist_id=self.watchlist_id
            )
        
        self.assertIn('Database connection failed', str(context.exception))


if __name__ == '__main__':
    unittest.main()
