# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from external.external_api_facade import ExternalApiFacade
from models.stock_model import Stock
from models.stock_event_model import StockEvent, EventType


class TestExternalApiFacadeInit(unittest.TestCase):
    '''Test ExternalApiFacade initialization.'''
    
    @patch('external.external_api_facade.AlphaVantage')
    @patch('external.external_api_facade.Finnhub')
    def test_init_success(self, mock_finnhub_class, mock_alpha_vantage_class):
        '''Test successful initialization of facade.'''
        mock_finnhub = Mock()
        mock_alpha_vantage = Mock()
        mock_finnhub_class.return_value = mock_finnhub
        mock_alpha_vantage_class.return_value = mock_alpha_vantage
        
        facade = ExternalApiFacade()
        
        self.assertEqual(facade.finnhub, mock_finnhub)
        self.assertEqual(facade.alpha_vantage, mock_alpha_vantage)
        mock_finnhub_class.assert_called_once()
        mock_alpha_vantage_class.assert_called_once()
    
    @patch('external.external_api_facade.AlphaVantage')
    @patch('external.external_api_facade.Finnhub')
    def test_init_raises_error_no_api_key(self, mock_finnhub_class, mock_alpha_vantage_class):
        '''Test initialization fails when API key is missing.'''
        mock_finnhub_class.side_effect = ValueError("API key not found")
        
        with self.assertRaises(ValueError):
            ExternalApiFacade()


class TestGetStockInfoFromName(unittest.TestCase):
    '''Test getStockInfoFromName method with fallback logic.'''
    
    def setUp(self):
        '''Set up test fixtures with mocked API clients.'''
        self.patcher_av = patch('external.external_api_facade.AlphaVantage')
        self.patcher_fh = patch('external.external_api_facade.Finnhub')
        
        self.mock_av_class = self.patcher_av.start()
        self.mock_fh_class = self.patcher_fh.start()
        
        self.mock_av = Mock()
        self.mock_fh = Mock()
        
        self.mock_av_class.return_value = self.mock_av
        self.mock_fh_class.return_value = self.mock_fh
        
        self.facade = ExternalApiFacade()
    
    def tearDown(self):
        '''Clean up patches after each test.'''
        self.patcher_av.stop()
        self.patcher_fh.stop()
    
    def test_get_stock_info_from_name_finnhub_success(self):
        '''Test successful lookup using Finnhub (primary).'''
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromName.return_value = mock_stock
        
        result = self.facade.getStockInfoFromName(name='Apple')
        
        self.assertEqual(result, mock_stock)
        self.mock_fh.getStockInfoFromName.assert_called_once_with(name='Apple')
        self.mock_av.getStockInfoFromName.assert_not_called()
    
    def test_get_stock_info_from_name_fallback_to_alpha_vantage(self):
        '''Test fallback to Alpha Vantage when Finnhub fails.'''
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromName.side_effect = ValueError("Finnhub error")
        self.mock_av.getStockInfoFromName.return_value = mock_stock
        
        result = self.facade.getStockInfoFromName(name='Apple')
        
        self.assertEqual(result, mock_stock)
        self.mock_fh.getStockInfoFromName.assert_called_once_with(name='Apple')
        self.mock_av.getStockInfoFromName.assert_called_once_with(name='Apple')
    
    def test_get_stock_info_from_name_both_fail(self):
        '''Test when both APIs fail to find stock.'''
        self.mock_fh.getStockInfoFromName.side_effect = ValueError("Finnhub error")
        self.mock_av.getStockInfoFromName.side_effect = ValueError("Alpha Vantage error")
        
        with self.assertRaises(ValueError) as context:
            self.facade.getStockInfoFromName(name='InvalidCompany')
        
        self.assertIn("Failed to fetch stock data for name 'InvalidCompany' from all sources", str(context.exception))
        self.mock_fh.getStockInfoFromName.assert_called_once()
        self.mock_av.getStockInfoFromName.assert_called_once()
    
    def test_get_stock_info_from_name_type_error(self):
        '''Test type error when name is not a string.'''
        with self.assertRaises(TypeError) as context:
            self.facade.getStockInfoFromName(name=123) # pyright: ignore[reportArgumentType]
        
        self.assertIn("Name must be a string", str(context.exception))
        self.mock_fh.getStockInfoFromName.assert_not_called()
        self.mock_av.getStockInfoFromName.assert_not_called()
    
    def test_get_stock_info_from_name_empty_string(self):
        '''Test with empty name string.'''
        self.mock_fh.getStockInfoFromName.side_effect = ValueError("Invalid name provided")
        self.mock_av.getStockInfoFromName.side_effect = ValueError("Invalid name provided")
        
        with self.assertRaises(ValueError):
            self.facade.getStockInfoFromName(name='')
    
    def test_get_stock_info_from_name_whitespace_only(self):
        '''Test with whitespace-only name string.'''
        self.mock_fh.getStockInfoFromName.side_effect = ValueError("Invalid name provided")
        self.mock_av.getStockInfoFromName.side_effect = ValueError("Invalid name provided")
        
        with self.assertRaises(ValueError):
            self.facade.getStockInfoFromName(name='   ')


class TestGetStockInfoFromSymbol(unittest.TestCase):
    '''Test getStockInfoFromSymbol method with fallback logic.'''
    
    def setUp(self):
        '''Set up test fixtures with mocked API clients.'''
        self.patcher_av = patch('external.external_api_facade.AlphaVantage')
        self.patcher_fh = patch('external.external_api_facade.Finnhub')
        
        self.mock_av_class = self.patcher_av.start()
        self.mock_fh_class = self.patcher_fh.start()
        
        self.mock_av = Mock()
        self.mock_fh = Mock()
        
        self.mock_av_class.return_value = self.mock_av
        self.mock_fh_class.return_value = self.mock_fh
        
        self.facade = ExternalApiFacade()
    
    def tearDown(self):
        '''Clean up patches after each test.'''
        self.patcher_av.stop()
        self.patcher_fh.stop()
    
    def test_get_stock_info_from_symbol_finnhub_success(self):
        '''Test successful lookup using Finnhub (primary).'''
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromSymbol.return_value = mock_stock
        
        result = self.facade.getStockInfoFromSymbol(symbol='AAPL')
        
        self.assertEqual(result, mock_stock)
        self.mock_fh.getStockInfoFromSymbol.assert_called_once_with(symbol='AAPL')
        self.mock_av.getStockInfoFromSymbol.assert_not_called()
    
    def test_get_stock_info_from_symbol_fallback_to_alpha_vantage(self):
        '''Test fallback to Alpha Vantage when Finnhub fails.'''
        mock_stock = Stock(
            name='Tesla Inc.',
            symbol='TSLA',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromSymbol.side_effect = ValueError("Finnhub error")
        self.mock_av.getStockInfoFromSymbol.return_value = mock_stock
        
        result = self.facade.getStockInfoFromSymbol(symbol='TSLA')
        
        self.assertEqual(result, mock_stock)
        self.mock_fh.getStockInfoFromSymbol.assert_called_once_with(symbol='TSLA')
        self.mock_av.getStockInfoFromSymbol.assert_called_once_with(symbol='TSLA')
    
    def test_get_stock_info_from_symbol_both_fail(self):
        '''Test when both APIs fail to find stock.'''
        self.mock_fh.getStockInfoFromSymbol.side_effect = ValueError("Finnhub error")
        self.mock_av.getStockInfoFromSymbol.side_effect = ValueError("Alpha Vantage error")
        
        with self.assertRaises(ValueError) as context:
            self.facade.getStockInfoFromSymbol(symbol='INVALID')
        
        self.assertIn("Failed to fetch stock data for symbol 'INVALID' from all sources", str(context.exception))
        self.mock_fh.getStockInfoFromSymbol.assert_called_once()
        self.mock_av.getStockInfoFromSymbol.assert_called_once()
    
    def test_get_stock_info_from_symbol_type_error(self):
        '''Test type error when symbol is not a string.'''
        with self.assertRaises(TypeError) as context:
            self.facade.getStockInfoFromSymbol(symbol=123) # pyright: ignore[reportArgumentType]
        
        self.assertIn("Symbol must be a string", str(context.exception))
        self.mock_fh.getStockInfoFromSymbol.assert_not_called()
        self.mock_av.getStockInfoFromSymbol.assert_not_called()
    
    def test_get_stock_info_from_symbol_empty_string(self):
        '''Test with empty symbol string.'''
        self.mock_fh.getStockInfoFromSymbol.side_effect = ValueError("Invalid symbol provided")
        self.mock_av.getStockInfoFromSymbol.side_effect = ValueError("Invalid symbol provided")
        
        with self.assertRaises(ValueError):
            self.facade.getStockInfoFromSymbol(symbol='')
    
    def test_get_stock_info_from_symbol_case_handling(self):
        '''Test that symbol lookup works regardless of case.'''
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromSymbol.return_value = mock_stock
        
        result = self.facade.getStockInfoFromSymbol(symbol='aapl')
        
        self.assertEqual(result, mock_stock)
        self.mock_fh.getStockInfoFromSymbol.assert_called_once_with(symbol='aapl')


class TestGetStockEventDatesFromStock(unittest.TestCase):
    '''Test getStockEventDatesFromStock method.'''
    
    def setUp(self):
        '''Set up test fixtures with mocked API clients.'''
        self.patcher_av = patch('external.external_api_facade.AlphaVantage')
        self.patcher_fh = patch('external.external_api_facade.Finnhub')
        
        self.mock_av_class = self.patcher_av.start()
        self.mock_fh_class = self.patcher_fh.start()
        
        self.mock_av = Mock()
        self.mock_fh = Mock()
        
        self.mock_av_class.return_value = self.mock_av
        self.mock_fh_class.return_value = self.mock_fh
        
        self.facade = ExternalApiFacade()
        
        self.test_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
    
    def tearDown(self):
        '''Clean up patches after each test.'''
        self.patcher_av.stop()
        self.patcher_fh.stop()
    
    def test_get_stock_event_dates_success_earnings(self):
        '''Test successful retrieval of earnings events.'''
        mock_events = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        self.mock_av.getStockEventDatesFromStock.return_value = mock_events
        
        result = self.facade.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        
        self.assertEqual(result, mock_events)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, EventType.EARNINGS_ANNOUNCEMENT)
        self.mock_av.getStockEventDatesFromStock.assert_called_once_with(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
    
    def test_get_stock_event_dates_success_multiple_types(self):
        '''Test successful retrieval of multiple event types.'''
        mock_events = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_EX,
                date=datetime(2025, 12, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        self.mock_av.getStockEventDatesFromStock.return_value = mock_events
        
        result = self.facade.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT, EventType.DIVIDEND_EX]
        )
        
        self.assertEqual(result, mock_events)
        self.assertEqual(len(result), 2)
    
    def test_get_stock_event_dates_success_all_dividend_types(self):
        '''Test successful retrieval of all dividend event types.'''
        mock_events = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_EX,
                date=datetime(2025, 12, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_DECLARATION,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_RECORD,
                date=datetime(2025, 12, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_PAYMENT,
                date=datetime(2025, 12, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        self.mock_av.getStockEventDatesFromStock.return_value = mock_events
        
        result = self.facade.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[
                EventType.DIVIDEND_EX,
                EventType.DIVIDEND_DECLARATION,
                EventType.DIVIDEND_RECORD,
                EventType.DIVIDEND_PAYMENT
            ]
        )
        
        self.assertEqual(len(result), 4)
    
    def test_get_stock_event_dates_success_stock_split(self):
        '''Test successful retrieval of stock split events.'''
        mock_events = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.STOCK_SPLIT,
                date=datetime(2025, 6, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        self.mock_av.getStockEventDatesFromStock.return_value = mock_events
        
        result = self.facade.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.STOCK_SPLIT]
        )
        
        self.assertEqual(result, mock_events)
        self.assertEqual(result[0].type, EventType.STOCK_SPLIT)
    
    def test_get_stock_event_dates_empty_result(self):
        '''Test when no events are found.'''
        self.mock_av.getStockEventDatesFromStock.return_value = []
        
        result = self.facade.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
    
    def test_get_stock_event_dates_type_error_stock(self):
        '''Test type error when stock is not a Stock object.'''
        with self.assertRaises(TypeError) as context:
            self.facade.getStockEventDatesFromStock(
                stock="not a stock", # pyright: ignore[reportArgumentType]
                event_types=[EventType.EARNINGS_ANNOUNCEMENT]
            )
        
        self.assertIn("Stock must be a Stock object", str(context.exception))
        self.mock_av.getStockEventDatesFromStock.assert_not_called()
    
    def test_get_stock_event_dates_type_error_event_types(self):
        '''Test type error when event_types is not a list.'''
        with self.assertRaises(TypeError) as context:
            self.facade.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types=EventType.EARNINGS_ANNOUNCEMENT # pyright: ignore[reportArgumentType]
            )
        
        self.assertIn("event_types must be a list", str(context.exception))
        self.mock_av.getStockEventDatesFromStock.assert_not_called()
    
    def test_get_stock_event_dates_empty_list_error(self):
        '''Test error when event_types list is empty.'''
        with self.assertRaises(ValueError) as context:
            self.facade.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types=[]
            )
        
        self.assertIn("event_types cannot be empty", str(context.exception))
        self.mock_av.getStockEventDatesFromStock.assert_not_called()
    
    def test_get_stock_event_dates_api_error(self):
        '''Test when Alpha Vantage API returns an error.'''
        self.mock_av.getStockEventDatesFromStock.side_effect = ValueError("API error")
        
        with self.assertRaises(ValueError):
            self.facade.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types=[EventType.EARNINGS_ANNOUNCEMENT]
            )


class TestFacadeIntegration(unittest.TestCase):
    '''Integration-style tests for the facade with realistic scenarios.'''
    
    def setUp(self):
        '''Set up test fixtures with mocked API clients.'''
        self.patcher_av = patch('external.external_api_facade.AlphaVantage')
        self.patcher_fh = patch('external.external_api_facade.Finnhub')
        
        self.mock_av_class = self.patcher_av.start()
        self.mock_fh_class = self.patcher_fh.start()
        
        self.mock_av = Mock()
        self.mock_fh = Mock()
        
        self.mock_av_class.return_value = self.mock_av
        self.mock_fh_class.return_value = self.mock_fh
        
        self.facade = ExternalApiFacade()
    
    def tearDown(self):
        '''Clean up patches after each test.'''
        self.patcher_av.stop()
        self.patcher_fh.stop()
    
    def test_full_workflow_stock_lookup_and_events(self):
        '''Test complete workflow: lookup stock and fetch events.'''
        # Mock stock lookup
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_fh.getStockInfoFromSymbol.return_value = mock_stock
        
        # Mock event retrieval
        mock_events = [
            StockEvent(
                stock=mock_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        self.mock_av.getStockEventDatesFromStock.return_value = mock_events
        
        # Step 1: Lookup stock
        stock = self.facade.getStockInfoFromSymbol(symbol='AAPL')
        self.assertEqual(stock.symbol, 'AAPL')
        
        # Step 2: Get events for the stock
        events = self.facade.getStockEventDatesFromStock(
            stock=stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].type, EventType.EARNINGS_ANNOUNCEMENT)
    
    def test_finnhub_rate_limit_fallback_scenario(self):
        '''Test realistic scenario where Finnhub hits rate limit.'''
        # Simulate rate limit on first call, success on second
        self.mock_fh.getStockInfoFromSymbol.side_effect = ValueError("Rate limit exceeded")
        
        mock_stock = Stock(
            name='Tesla Inc.',
            symbol='TSLA',
            last_updated=datetime.now(timezone.utc)
        )
        self.mock_av.getStockInfoFromSymbol.return_value = mock_stock
        
        result = self.facade.getStockInfoFromSymbol(symbol='TSLA')
        
        self.assertEqual(result, mock_stock)
        # Verify both APIs were called
        self.mock_fh.getStockInfoFromSymbol.assert_called_once()
        self.mock_av.getStockInfoFromSymbol.assert_called_once()


if __name__ == '__main__':
    unittest.main()
