# Disclaimer: Created by GitHub Copilot
'''
Unit tests for StocksService.
'''

import unittest
from unittest.mock import Mock, patch, call
from datetime import datetime, timezone

from src.app.services.stocks_service import StocksService
from src.models.stock_model import Stock
from src.models.stock_event_model import EventType, StockEvent


class TestStocksServiceInitialization(unittest.TestCase):
    '''Test StocksService initialization.'''
    
    @patch('src.app.services.stocks_service.DatabaseAdapterFactory.get_instance')
    @patch('src.app.services.stocks_service.ExternalApiFacade')
    def test_init(self, mock_external_api, mock_db_factory):
        '''Test service initializes with correct dependencies.'''
        mock_db = Mock()
        mock_db_factory.return_value = mock_db
        
        service = StocksService()
        
        self.assertIsNotNone(service.db)
        self.assertIsNotNone(service.external_api)
        mock_db_factory.assert_called_once()
        mock_external_api.assert_called_once()


class TestGetStockFromTicker(unittest.TestCase):
    '''Test get_stock_from_ticker method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        self.mock_external_api = Mock()
        
        with patch('src.app.services.stocks_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            with patch('src.app.services.stocks_service.ExternalApiFacade', return_value=self.mock_external_api):
                self.service = StocksService()
    
    def test_get_stock_invalid_ticker_type(self):
        '''Test get_stock fails with non-string ticker.'''
        with self.assertRaises(ValueError) as context:
            self.service.get_stock_from_ticker(ticker=123)  # type: ignore
        
        self.assertIn('ticker must be a non-empty string', str(context.exception))
    
    def test_get_stock_empty_ticker(self):
        '''Test get_stock fails with empty ticker.'''
        with self.assertRaises(ValueError) as context:
            self.service.get_stock_from_ticker(ticker='')
        
        self.assertIn('ticker must be a non-empty string', str(context.exception))
    
    def test_get_stock_whitespace_ticker(self):
        '''Test get_stock fails with whitespace-only ticker.'''
        with self.assertRaises(ValueError) as context:
            self.service.get_stock_from_ticker(ticker='   ')
        
        self.assertIn('ticker must be a non-empty string', str(context.exception))
    
    def test_get_stock_from_cache_success(self):
        '''Test successful retrieval from database cache.'''
        mock_result = {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'last_updated': datetime.now(timezone.utc),
        }
        self.mock_db.execute_query.return_value = [mock_result]
        
        stock = self.service.get_stock_from_ticker(ticker='aapl')
        
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.name, 'Apple Inc.')
        self.assertIsInstance(stock.last_updated, datetime)
        self.mock_db.execute_query.assert_called_once()
        # Should not call external API if found in cache
        self.mock_external_api.getStockInfoFromSymbol.assert_not_called()
    
    def test_get_stock_from_cache_with_string_timestamp(self):
        '''Test retrieval handles string timestamp from database.'''
        mock_result = {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'last_updated': '2025-11-06T10:30:00+00:00',
        }
        self.mock_db.execute_query.return_value = [mock_result]
        
        stock = self.service.get_stock_from_ticker(ticker='AAPL')
        
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertIsInstance(stock.last_updated, datetime)
    
    def test_get_stock_from_cache_with_invalid_timestamp(self):
        '''Test retrieval handles invalid timestamp gracefully.'''
        mock_result = {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'last_updated': 'invalid-date',
        }
        self.mock_db.execute_query.return_value = [mock_result]
        
        stock = self.service.get_stock_from_ticker(ticker='AAPL')
        
        self.assertEqual(stock.symbol, 'AAPL')
        # Should fallback to current timestamp
        self.assertIsInstance(stock.last_updated, datetime)
    
    def test_get_stock_from_cache_with_none_timestamp(self):
        '''Test retrieval handles None timestamp gracefully.'''
        mock_result = {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'last_updated': None,
        }
        self.mock_db.execute_query.return_value = [mock_result]
        
        stock = self.service.get_stock_from_ticker(ticker='AAPL')
        
        self.assertEqual(stock.symbol, 'AAPL')
        # Should fallback to current timestamp
        self.assertIsInstance(stock.last_updated, datetime)
    
    def test_get_stock_normalizes_ticker_case(self):
        '''Test ticker is normalized to uppercase.'''
        mock_result = {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'last_updated': datetime.now(timezone.utc),
        }
        self.mock_db.execute_query.return_value = [mock_result]
        
        stock = self.service.get_stock_from_ticker(ticker='  aapl  ')
        
        self.assertEqual(stock.symbol, 'AAPL')
        # Verify query was called with uppercase ticker
        call_args = self.mock_db.execute_query.call_args
        self.assertEqual(call_args[1]['params']['ticker'], 'AAPL')
    
    def test_get_stock_from_external_api_success(self):
        '''Test fetching from external API when not in cache.'''
        # Cache miss
        self.mock_db.execute_query.return_value = []
        
        # Mock external API response
        mock_external_stock = Stock(
            name='Microsoft Corporation',
            symbol='MSFT',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        
        # Mock stock events response
        mock_events = [
            StockEvent(
                stock=mock_external_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Alpha Vantage'
            ),
            StockEvent(
                stock=mock_external_stock,
                type=EventType.DIVIDEND_EX,
                date=datetime(2025, 11, 20, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Alpha Vantage'
            )
        ]
        self.mock_external_api.getStockEventDatesFromStock.return_value = mock_events
        self.mock_db.execute_update.return_value = 1
        
        stock = self.service.get_stock_from_ticker(ticker='msft')
        
        self.assertEqual(stock.symbol, 'MSFT')
        self.assertEqual(stock.name, 'Microsoft Corporation')
        # Should call external API
        self.mock_external_api.getStockInfoFromSymbol.assert_called_once_with(symbol='MSFT')
        # Should cache the stock result
        self.assertEqual(self.mock_db.execute_update.call_count, 3)  # 1 for stock + 2 for events
        
        # Verify stock events were fetched
        self.mock_external_api.getStockEventDatesFromStock.assert_called_once()
        call_args = self.mock_external_api.getStockEventDatesFromStock.call_args
        self.assertEqual(call_args[1]['stock'].symbol, 'MSFT')
        self.assertEqual(call_args[1]['event_types'], list(EventType))
    
    def test_get_stock_external_api_normalizes_symbol(self):
        '''Test external API response symbol is normalized to uppercase.'''
        self.mock_db.execute_query.return_value = []
        
        # Mock external API with lowercase symbol
        mock_external_stock = Stock(
            name='Tesla Inc.',
            symbol='tsla',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.return_value = []
        self.mock_db.execute_update.return_value = 1
        
        stock = self.service.get_stock_from_ticker(ticker='TSLA')
        
        # Should be normalized to uppercase
        self.assertEqual(stock.symbol, 'TSLA')
    
    def test_get_stock_external_api_handles_missing_timestamp(self):
        '''Test external API response without timestamp gets current time.'''
        self.mock_db.execute_query.return_value = []
        
        # Mock external API with None timestamp
        mock_external_stock = Mock()
        mock_external_stock.name = 'Amazon.com Inc.'
        mock_external_stock.symbol = 'AMZN'
        mock_external_stock.last_updated = None
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.return_value = []
        self.mock_db.execute_update.return_value = 1
        
        stock = self.service.get_stock_from_ticker(ticker='AMZN')
        
        self.assertEqual(stock.symbol, 'AMZN')
        # Should have timestamp set to current time
        self.assertIsInstance(stock.last_updated, datetime)
    
    def test_get_stock_cache_query_error(self):
        '''Test handles database query errors.'''
        self.mock_db.execute_query.side_effect = Exception('Database error')
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker='AAPL')
        
        self.assertIn('Failed to query local stock cache', str(context.exception))
    
    def test_get_stock_external_api_error(self):
        '''Test handles external API errors.'''
        self.mock_db.execute_query.return_value = []
        self.mock_external_api.getStockInfoFromSymbol.side_effect = Exception('API error')
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker='INVALID')
        
        self.assertIn('Failed to fetch stock from external providers', str(context.exception))
    
    def test_get_stock_cache_update_error(self):
        '''Test handles cache update errors but still returns stock.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Netflix Inc.',
            symbol='NFLX',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_db.execute_update.side_effect = Exception('Cache update failed')
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker='NFLX')
        
        self.assertIn('Failed to persist stock data', str(context.exception))
    
    def test_get_stock_uses_upsert_pattern(self):
        '''Test that cache update uses UPSERT pattern.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Google LLC',
            symbol='GOOGL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.return_value = []
        self.mock_db.execute_update.return_value = 1
        
        self.service.get_stock_from_ticker(ticker='GOOGL')
        
        # Verify UPSERT query was used
        call_args = self.mock_db.execute_update.call_args_list[0]
        query = call_args[1]['query']
        self.assertIn('ON CONFLICT', query)
        self.assertIn('DO UPDATE', query)
    
    def test_get_stock_fetches_all_event_types(self):
        '''Test that all event types are requested from external API.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.return_value = []
        self.mock_db.execute_update.return_value = 1
        
        self.service.get_stock_from_ticker(ticker='AAPL')
        
        # Verify all event types were requested
        call_args = self.mock_external_api.getStockEventDatesFromStock.call_args
        requested_event_types = call_args[1]['event_types']
        self.assertEqual(requested_event_types, list(EventType))
        self.assertEqual(len(requested_event_types), 6)  # All 6 event types
    
    def test_get_stock_stores_stock_events(self):
        '''Test that stock events are stored in database.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Netflix Inc.',
            symbol='NFLX',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        
        # Mock multiple stock events
        mock_events = [
            StockEvent(
                stock=mock_external_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Alpha Vantage'
            ),
            StockEvent(
                stock=mock_external_stock,
                type=EventType.DIVIDEND_EX,
                date=datetime(2025, 11, 20, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Alpha Vantage'
            ),
            StockEvent(
                stock=mock_external_stock,
                type=EventType.STOCK_SPLIT,
                date=datetime(2025, 12, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='Alpha Vantage'
            )
        ]
        self.mock_external_api.getStockEventDatesFromStock.return_value = mock_events
        self.mock_db.execute_update.return_value = 1
        
        self.service.get_stock_from_ticker(ticker='NFLX')
        
        # Verify execute_update was called for stock + each event
        # 1 call for stock, 3 calls for events = 4 total
        self.assertEqual(self.mock_db.execute_update.call_count, 4)
        
        # Verify event queries use UPSERT pattern
        event_calls = self.mock_db.execute_update.call_args_list[1:]  # Skip first (stock) call
        for event_call in event_calls:
            query = event_call[1]['query']
            self.assertIn('stock_events', query)
            self.assertIn('ON CONFLICT', query)
    
    def test_get_stock_event_parameters_correct(self):
        '''Test that stock events are stored with correct parameters.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Meta Platforms Inc.',
            symbol='META',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        
        event_date = datetime(2025, 11, 25, tzinfo=timezone.utc)
        mock_event = StockEvent(
            stock=mock_external_stock,
            type=EventType.DIVIDEND_PAYMENT,
            date=event_date,
            last_updated=datetime.now(timezone.utc),
            source='Alpha Vantage'
        )
        self.mock_external_api.getStockEventDatesFromStock.return_value = [mock_event]
        self.mock_db.execute_update.return_value = 1
        
        self.service.get_stock_from_ticker(ticker='META')
        
        # Get the event insert call (second call)
        event_call = self.mock_db.execute_update.call_args_list[1]
        params = event_call[1]['params']
        
        # Verify all parameters are correct
        self.assertEqual(params['stock_ticker'], 'META')
        self.assertEqual(params['type'], EventType.DIVIDEND_PAYMENT.value)
        self.assertEqual(params['event_date'], event_date)
        self.assertEqual(params['source'], 'Alpha Vantage')
        self.assertIsInstance(params['last_updated'], datetime)
    
    def test_get_stock_event_last_updated_is_current_time(self):
        '''Test that stock events use current time for last_updated, not event's last_updated.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Adobe Inc.',
            symbol='ADBE',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        
        # Event with old last_updated timestamp
        old_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_event = StockEvent(
            stock=mock_external_stock,
            type=EventType.EARNINGS_ANNOUNCEMENT,
            date=datetime(2025, 11, 30, tzinfo=timezone.utc),
            last_updated=old_timestamp,
            source='Alpha Vantage'
        )
        self.mock_external_api.getStockEventDatesFromStock.return_value = [mock_event]
        self.mock_db.execute_update.return_value = 1
        
        before_call = datetime.now(timezone.utc)
        self.service.get_stock_from_ticker(ticker='ADBE')
        after_call = datetime.now(timezone.utc)
        
        # Get the event insert call
        event_call = self.mock_db.execute_update.call_args_list[1]
        params = event_call[1]['params']
        
        # Verify last_updated is current time, not the event's old timestamp
        self.assertGreaterEqual(params['last_updated'], before_call)
        self.assertLessEqual(params['last_updated'], after_call)
        self.assertNotEqual(params['last_updated'], old_timestamp)
    
    def test_get_stock_events_fetch_error(self):
        '''Test handling of errors when fetching stock events.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Oracle Corporation',
            symbol='ORCL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.side_effect = Exception('API error')
        self.mock_db.execute_update.return_value = 1
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker='ORCL')
        
        self.assertIn('Failed to fetch or store stock events', str(context.exception))
    
    def test_get_stock_events_store_error(self):
        '''Test handling of errors when storing stock events.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='Salesforce Inc.',
            symbol='CRM',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        
        mock_event = StockEvent(
            stock=mock_external_stock,
            type=EventType.EARNINGS_ANNOUNCEMENT,
            date=datetime(2025, 12, 1, tzinfo=timezone.utc),
            last_updated=datetime.now(timezone.utc),
            source='Alpha Vantage'
        )
        self.mock_external_api.getStockEventDatesFromStock.return_value = [mock_event]
        
        # First call succeeds (stock insert), second call fails (event insert)
        self.mock_db.execute_update.side_effect = [1, Exception('Database error')]
        
        with self.assertRaises(Exception) as context:
            self.service.get_stock_from_ticker(ticker='CRM')
        
        self.assertIn('Failed to fetch or store stock events', str(context.exception))
    
    def test_get_stock_with_no_events(self):
        '''Test handling when stock has no events.'''
        self.mock_db.execute_query.return_value = []
        
        mock_external_stock = Stock(
            name='New Company Inc.',
            symbol='NEWCO',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_external_api.getStockInfoFromSymbol.return_value = mock_external_stock
        self.mock_external_api.getStockEventDatesFromStock.return_value = []
        self.mock_db.execute_update.return_value = 1
        
        stock = self.service.get_stock_from_ticker(ticker='NEWCO')
        
        # Should still succeed and return the stock
        self.assertEqual(stock.symbol, 'NEWCO')
        # Only one execute_update call for the stock itself
        self.assertEqual(self.mock_db.execute_update.call_count, 1)


if __name__ == '__main__':
    unittest.main()
