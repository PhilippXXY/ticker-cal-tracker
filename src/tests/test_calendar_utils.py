# Disclaimer: Created by GitHub Copilot
'''
Unit tests for calendar_utils module.
'''

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.app.utils.calendar_utils import (
    generate_calendar_token,
    build_ics,
    _create_vevent,
    _get_event_details,
    _create_valarm
)
from src.models.stock_event_model import StockEvent, EventType
from src.models.stock_model import Stock


class TestGenerateCalendarToken(unittest.TestCase):
    '''Test calendar token generation.'''
    
    def test_generate_token_returns_string(self):
        '''Test that token generation returns a string.'''
        token = generate_calendar_token()
        self.assertIsInstance(token, str)
    
    def test_generate_token_is_unique(self):
        '''Test that generated tokens are unique.'''
        token1 = generate_calendar_token()
        token2 = generate_calendar_token()
        self.assertNotEqual(token1, token2)
    
    def test_generate_token_is_url_safe(self):
        '''Test that generated tokens are URL-safe.'''
        token = generate_calendar_token()
        # URL-safe base64 uses: A-Z, a-z, 0-9, -, _
        allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
        self.assertTrue(all(c in allowed_chars for c in token))
    
    def test_generate_token_has_reasonable_length(self):
        '''Test that tokens have a reasonable length for security.'''
        token = generate_calendar_token()
        # secrets.token_urlsafe(32) generates 43 characters
        self.assertGreater(len(token), 30)


class TestBuildIcs(unittest.TestCase):
    '''Test iCalendar file generation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        self.event = StockEvent(
            stock=self.stock,
            type=EventType.EARNINGS_ANNOUNCEMENT,
            date=datetime(2025, 2, 1, tzinfo=timezone.utc),
            last_updated=datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            source='AlphaVantage'
        )
    
    def test_build_ics_with_empty_events(self):
        '''Test building iCalendar with no events.'''
        ics = build_ics(stock_events=[])
        
        self.assertIn('BEGIN:VCALENDAR', ics)
        self.assertIn('END:VCALENDAR', ics)
        self.assertIn('VERSION:2.0', ics)
        self.assertNotIn('BEGIN:VEVENT', ics)
    
    def test_build_ics_with_single_event(self):
        '''Test building iCalendar with one event.'''
        ics = build_ics(stock_events=[self.event])
        
        self.assertIn('BEGIN:VCALENDAR', ics)
        self.assertIn('END:VCALENDAR', ics)
        self.assertIn('BEGIN:VEVENT', ics)
        self.assertIn('END:VEVENT', ics)
        self.assertIn('AAPL', ics)
    
    def test_build_ics_with_multiple_events(self):
        '''Test building iCalendar with multiple events.'''
        event2 = StockEvent(
            stock=Stock(name='Microsoft', symbol='MSFT', last_updated=datetime.now(timezone.utc)),
            type=EventType.DIVIDEND_PAYMENT,
            date=datetime(2025, 3, 1, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='Finnhub'
        )
        
        ics = build_ics(stock_events=[self.event, event2])
        
        # Should have 2 VEVENT blocks
        self.assertEqual(ics.count('BEGIN:VEVENT'), 2)
        self.assertEqual(ics.count('END:VEVENT'), 2)
        self.assertIn('AAPL', ics)
        self.assertIn('MSFT', ics)
    
    def test_build_ics_with_custom_watchlist_name(self):
        '''Test building iCalendar with custom watchlist name.'''
        ics = build_ics(stock_events=[self.event], watchlist_name='My Tech Stocks')
        
        self.assertIn('X-WR-CALNAME:My Tech Stocks', ics)
    
    def test_build_ics_with_reminder(self):
        '''Test building iCalendar with reminder.'''
        reminder = timedelta(days=1)
        ics = build_ics(stock_events=[self.event], reminder_before=reminder)
        
        self.assertIn('BEGIN:VALARM', ics)
        self.assertIn('END:VALARM', ics)
        self.assertIn('TRIGGER:-P1D', ics)
    
    def test_build_ics_uses_crlf(self):
        '''Test that iCalendar uses CRLF line endings.'''
        ics = build_ics(stock_events=[self.event])
        
        # RFC 5545 requires CRLF (\r\n)
        self.assertIn('\r\n', ics)
    
    def test_build_ics_has_required_headers(self):
        '''Test that iCalendar has all required headers.'''
        ics = build_ics(stock_events=[])
        
        required_headers = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            'END:VCALENDAR'
        ]
        
        for header in required_headers:
            self.assertIn(header, ics)


class TestCreateVevent(unittest.TestCase):
    '''Test VEVENT creation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.stock = Stock(
            name='Tesla Inc.',
            symbol='TSLA',
            last_updated=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        
        self.event = StockEvent(
            stock=self.stock,
            type=EventType.STOCK_SPLIT,
            date=datetime(2025, 6, 15, tzinfo=timezone.utc),
            last_updated=datetime(2025, 5, 1, tzinfo=timezone.utc),
            source='AlphaVantage'
        )
    
    def test_create_vevent_has_required_fields(self):
        '''Test that VEVENT has all required fields.'''
        vevent_lines = _create_vevent(self.event)
        vevent_str = '\n'.join(vevent_lines)
        
        required_fields = [
            'BEGIN:VEVENT',
            'END:VEVENT',
            'UID:',
            'DTSTAMP:',
            'DTSTART;VALUE=DATE:',
            'SUMMARY:',
            'DESCRIPTION:'
        ]
        
        for field in required_fields:
            self.assertIn(field, vevent_str)
    
    def test_create_vevent_date_format(self):
        '''Test that event date is formatted correctly.'''
        vevent_lines = _create_vevent(self.event)
        vevent_str = '\n'.join(vevent_lines)
        
        # Date should be in YYYYMMDD format
        self.assertIn('DTSTART;VALUE=DATE:20250615', vevent_str)
    
    def test_create_vevent_unique_uid(self):
        '''Test that UID is unique for different events.'''
        event2 = StockEvent(
            stock=self.stock,
            type=EventType.EARNINGS_ANNOUNCEMENT,
            date=datetime(2025, 7, 1, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='Finnhub'
        )
        
        vevent1 = _create_vevent(self.event)
        vevent2 = _create_vevent(event2)
        
        uid1 = [line for line in vevent1 if line.startswith('UID:')][0]
        uid2 = [line for line in vevent2 if line.startswith('UID:')][0]
        
        self.assertNotEqual(uid1, uid2)
    
    def test_create_vevent_includes_source(self):
        '''Test that source is included in VEVENT.'''
        vevent_lines = _create_vevent(self.event)
        vevent_str = '\n'.join(vevent_lines)
        
        self.assertIn('X-SOURCE:AlphaVantage', vevent_str)
    
    def test_create_vevent_with_reminder(self):
        '''Test creating VEVENT with reminder.'''
        reminder = timedelta(hours=12)
        vevent_lines = _create_vevent(self.event, reminder_before=reminder)
        vevent_str = '\n'.join(vevent_lines)
        
        self.assertIn('BEGIN:VALARM', vevent_str)
        self.assertIn('END:VALARM', vevent_str)


class TestGetEventDetails(unittest.TestCase):
    '''Test event detail generation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.stock = Stock(
            name='Amazon.com Inc.',
            symbol='AMZN',
            last_updated=datetime.now(timezone.utc)
        )
    
    def test_earnings_announcement_details(self):
        '''Test details for earnings announcement.'''
        event = StockEvent(
            stock=self.stock,
            type=EventType.EARNINGS_ANNOUNCEMENT,
            date=datetime(2025, 4, 15, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='AlphaVantage'
        )
        
        summary, description = _get_event_details(event)
        
        self.assertIn('AMZN', summary)
        self.assertIn('Earnings', summary)
        self.assertIn('Amazon.com Inc.', description)
        self.assertIn('earnings report', description.lower())
    
    def test_dividend_ex_details(self):
        '''Test details for dividend ex-date.'''
        event = StockEvent(
            stock=self.stock,
            type=EventType.DIVIDEND_EX,
            date=datetime(2025, 5, 1, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='Finnhub'
        )
        
        summary, description = _get_event_details(event)
        
        self.assertIn('Dividend Ex-Date', summary)
        self.assertIn('Ex-dividend', description)
    
    def test_stock_split_details(self):
        '''Test details for stock split.'''
        event = StockEvent(
            stock=self.stock,
            type=EventType.STOCK_SPLIT,
            date=datetime(2025, 6, 1, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='AlphaVantage'
        )
        
        summary, description = _get_event_details(event)
        
        self.assertIn('Stock Split', summary)
        self.assertIn('split', description.lower())
    
    def test_all_event_types_have_details(self):
        '''Test that all event types have proper details.'''
        for event_type in EventType:
            event = StockEvent(
                stock=self.stock,
                type=event_type,
                date=datetime(2025, 1, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Test'
            )
            
            summary, description = _get_event_details(event)
            
            self.assertIsInstance(summary, str)
            self.assertIsInstance(description, str)
            self.assertGreater(len(summary), 0)
            self.assertGreater(len(description), 0)


class TestCreateValarm(unittest.TestCase):
    '''Test VALARM creation.'''
    
    def test_create_valarm_one_day(self):
        '''Test creating alarm for 1 day before.'''
        reminder = timedelta(days=1)
        valarm_lines = _create_valarm(reminder)
        valarm_str = '\n'.join(valarm_lines)
        
        self.assertIn('BEGIN:VALARM', valarm_str)
        self.assertIn('END:VALARM', valarm_str)
        self.assertIn('TRIGGER:-P1D', valarm_str)
        self.assertIn('ACTION:DISPLAY', valarm_str)
    
    def test_create_valarm_hours(self):
        '''Test creating alarm for hours before.'''
        reminder = timedelta(hours=2)
        valarm_lines = _create_valarm(reminder)
        valarm_str = '\n'.join(valarm_lines)
        
        self.assertIn('TRIGGER:-PT2H', valarm_str)
    
    def test_create_valarm_mixed(self):
        '''Test creating alarm with days and hours.'''
        reminder = timedelta(days=2, hours=3)
        valarm_lines = _create_valarm(reminder)
        valarm_str = '\n'.join(valarm_lines)
        
        self.assertIn('TRIGGER:-P2DT3H', valarm_str)
    
    def test_create_valarm_minutes(self):
        '''Test creating alarm for minutes before.'''
        reminder = timedelta(minutes=30)
        valarm_lines = _create_valarm(reminder)
        valarm_str = '\n'.join(valarm_lines)
        
        self.assertIn('TRIGGER:-PT30M', valarm_str)
    
    def test_create_valarm_zero(self):
        '''Test creating alarm for zero time.'''
        reminder = timedelta(0)
        valarm_lines = _create_valarm(reminder)
        valarm_str = '\n'.join(valarm_lines)
        
        # Should default to P0D
        self.assertIn('TRIGGER:-P0D', valarm_str)


if __name__ == '__main__':
    unittest.main()
