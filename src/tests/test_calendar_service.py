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


if __name__ == '__main__':
    unittest.main()
