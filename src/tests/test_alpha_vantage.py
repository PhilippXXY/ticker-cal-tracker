# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timezone
import requests

from external.alpha_vantage import AlphaVantage
from models.stock_model import Stock
from models.stock_event_model import StockEvent, EventType


class TestAlphaVantageInit(unittest.TestCase):
    '''Test AlphaVantage initialization.'''
    
    @patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__')
    def test_init_success(self, mock_super_init):
        '''Test successful initialization.'''
        mock_super_init.return_value = None
        
        av = AlphaVantage()
        
        mock_super_init.assert_called_once_with(api_key_name='API_KEY_ALPHA_VANTAGE')
        self.assertEqual(av.source, 'AlphaVantage')
    
    @patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__')
    def test_init_raises_error_no_api_key(self, mock_super_init):
        '''Test initialization fails when API key is missing.'''
        mock_super_init.side_effect = ValueError("API key not found")
        
        with self.assertRaises(ValueError):
            AlphaVantage()


class TestGetStockInfoFromName(unittest.TestCase):
    '''Test getStockInfoFromName method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_name_success(self, mock_get):
        '''Test successful stock lookup by name.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'bestMatches': [
                {
                    '1. symbol': 'AAPL',
                    '2. name': 'Apple Inc',
                    '3. type': 'Equity',
                    '4. region': 'United States'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.av.getStockInfoFromName(name='Apple')
        
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'AAPL')
        self.assertEqual(result.name, 'Apple Inc')
        self.assertIsNotNone(result.last_updated)
        mock_get.assert_called_once()
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_name_no_matches(self, mock_get):
        '''Test when no matches are found.'''
        mock_response = Mock()
        mock_response.json.return_value = {'bestMatches': []}
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromName(name='NonexistentCompany')
        
        self.assertIn('No stocks found', str(context.exception))
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_name_invalid_data(self, mock_get):
        '''Test when API returns invalid data.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'bestMatches': [
                {
                    '1. symbol': '',
                    '2. name': ''
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromName(name='Test')
        
        self.assertIn('Invalid data', str(context.exception))
    
    def test_get_stock_info_from_name_empty_string(self):
        '''Test with empty name string.'''
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromName(name='')
        
        self.assertIn('Invalid name provided', str(context.exception))
    
    def test_get_stock_info_from_name_whitespace_only(self):
        '''Test with whitespace-only name.'''
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromName(name='   ')
        
        self.assertIn('Invalid name provided', str(context.exception))
    
    def test_get_stock_info_from_name_wrong_type(self):
        '''Test with non-string type.'''
        with self.assertRaises(TypeError) as context:
            self.av.getStockInfoFromName(name=123) # pyright: ignore[reportArgumentType]
        
        self.assertIn('Name must be a string', str(context.exception))
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_name_api_error(self, mock_get):
        '''Test when API request fails.'''
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromName(name='Apple')
        
        self.assertIn('Error fetching stock data', str(context.exception))


class TestGetStockInfoFromSymbol(unittest.TestCase):
    '''Test getStockInfoFromSymbol method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_symbol_exact_match(self, mock_get):
        '''Test successful lookup with exact symbol match.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'bestMatches': [
                {
                    '1. symbol': 'AAPL',
                    '2. name': 'Apple Inc',
                    '3. type': 'Equity'
                },
                {
                    '1. symbol': 'AAPL.US',
                    '2. name': 'Apple Inc - US',
                    '3. type': 'Equity'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'AAPL')
        self.assertEqual(result.name, 'Apple Inc')
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_symbol_no_exact_match(self, mock_get):
        '''Test when no exact match but results exist.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'bestMatches': [
                {
                    '1. symbol': 'AAPL.LON',
                    '2. name': 'Apple Inc London',
                    '3. type': 'Equity'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Should return first result when no exact match
        self.assertEqual(result.symbol, 'AAPL.LON')
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_symbol_case_insensitive(self, mock_get):
        '''Test symbol matching is case insensitive.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'bestMatches': [
                {
                    '1. symbol': 'AAPL',
                    '2. name': 'Apple Inc',
                    '3. type': 'Equity'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.av.getStockInfoFromSymbol(symbol='aapl')
        
        self.assertEqual(result.symbol, 'AAPL')
    
    def test_get_stock_info_from_symbol_empty_string(self):
        '''Test with empty symbol.'''
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromSymbol(symbol='')
        
        self.assertIn('Invalid symbol provided', str(context.exception))
    
    def test_get_stock_info_from_symbol_wrong_type(self):
        '''Test with non-string type.'''
        with self.assertRaises(TypeError) as context:
            self.av.getStockInfoFromSymbol(symbol=None) # pyright: ignore[reportArgumentType]
        
        self.assertIn('Symbol must be a string', str(context.exception))
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_stock_info_from_symbol_no_results(self, mock_get):
        '''Test when no results found.'''
        mock_response = Mock()
        mock_response.json.return_value = {'bestMatches': []}
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.av.getStockInfoFromSymbol(symbol='INVALID')
        
        self.assertIn('No stock data found', str(context.exception))


class TestGetStockEventDatesFromStock(unittest.TestCase):
    '''Test getStockEventDatesFromStock method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
            self.av.source = 'AlphaVantage'
        
        self.test_stock = Stock(
            name='Apple Inc',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
    
    @patch.object(AlphaVantage, '_getEarningsAnnouncementsFromStock')
    def test_get_earnings_only(self, mock_earnings):
        '''Test fetching only earnings events.'''
        mock_earnings.return_value = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        
        result = self.av.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, EventType.EARNINGS_ANNOUNCEMENT)
        mock_earnings.assert_called_once_with(stock=self.test_stock)
    
    @patch.object(AlphaVantage, '_getSplitsFromStock')
    def test_get_splits_only(self, mock_splits):
        '''Test fetching only stock split events.'''
        mock_splits.return_value = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.STOCK_SPLIT,
                date=datetime(2025, 11, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        
        result = self.av.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.STOCK_SPLIT]
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, EventType.STOCK_SPLIT)
    
    @patch.object(AlphaVantage, '_getDividendsFromStock')
    def test_get_dividends_filtered(self, mock_dividends):
        '''Test fetching dividends with filtering.'''
        # API returns all dividend types
        mock_dividends.return_value = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_EX,
                date=datetime(2025, 11, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_PAYMENT,
                date=datetime(2025, 11, 10, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            ),
            StockEvent(
                stock=self.test_stock,
                type=EventType.DIVIDEND_DECLARATION,
                date=datetime(2025, 11, 1, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        
        # Request only DIVIDEND_EX
        result = self.av.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.DIVIDEND_EX]
        )
        
        # Should only return DIVIDEND_EX
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, EventType.DIVIDEND_EX)
    
    @patch.object(AlphaVantage, '_getEarningsAnnouncementsFromStock')
    @patch.object(AlphaVantage, '_getSplitsFromStock')
    def test_get_multiple_event_types(self, mock_splits, mock_earnings):
        '''Test fetching multiple event types.'''
        mock_earnings.return_value = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.EARNINGS_ANNOUNCEMENT,
                date=datetime(2025, 11, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        mock_splits.return_value = [
            StockEvent(
                stock=self.test_stock,
                type=EventType.STOCK_SPLIT,
                date=datetime(2025, 11, 10, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc),
                source='AlphaVantage'
            )
        ]
        
        result = self.av.getStockEventDatesFromStock(
            stock=self.test_stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT, EventType.STOCK_SPLIT]
        )
        
        self.assertEqual(len(result), 2)
    
    def test_invalid_stock_type(self):
        '''Test with invalid stock type.'''
        with self.assertRaises(TypeError) as context:
            self.av.getStockEventDatesFromStock(
                stock="not a stock", # pyright: ignore[reportArgumentType]
                event_types=[EventType.EARNINGS_ANNOUNCEMENT]
            )
        
        self.assertIn('Stock must be a Stock object', str(context.exception))
    
    def test_invalid_event_types_type(self):
        '''Test with invalid event_types type.'''
        with self.assertRaises(TypeError) as context:
            self.av.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types="not a list" # pyright: ignore[reportArgumentType]
            )
        
        self.assertIn('event_types must be a list', str(context.exception))
    
    def test_empty_event_types(self):
        '''Test with empty event_types list.'''
        with self.assertRaises(ValueError) as context:
            self.av.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types=[]
            )
        
        self.assertIn('event_types cannot be empty', str(context.exception))
    
    def test_invalid_event_type_in_list(self):
        '''Test with invalid EventType in list.'''
        with self.assertRaises(TypeError) as context:
            self.av.getStockEventDatesFromStock(
                stock=self.test_stock,
                event_types=[EventType.EARNINGS_ANNOUNCEMENT, "invalid"] # pyright: ignore[reportArgumentType]
            )
        
        self.assertIn('All event_types must be EventType enums', str(context.exception))


class TestGetEarningsAnnouncementsFromStock(unittest.TestCase):
    '''Test _getEarningsAnnouncementsFromStock method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
            self.av.source = 'AlphaVantage'
        
        self.test_stock = Stock(
            name='Apple Inc',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
    
    @patch('external.alpha_vantage.requests.Session')
    def test_get_earnings_success(self, mock_session):
        '''Test successful earnings fetch.'''
        csv_data = "symbol,reportDate,fiscalDateEnding\nAAPL,2025-11-05,2025-09-30\nAAPL,2026-02-05,2025-12-31"
        
        mock_response = Mock()
        mock_response.content = csv_data.encode('utf-8')
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.__enter__ = Mock(return_value=mock_session_instance)
        mock_session_instance.__exit__ = Mock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        result = self.av._getEarningsAnnouncementsFromStock(stock=self.test_stock)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].type, EventType.EARNINGS_ANNOUNCEMENT)
        self.assertEqual(result[0].stock, self.test_stock)
    
    @patch('external.alpha_vantage.requests.Session')
    def test_get_earnings_wrong_symbol(self, mock_session):
        '''Test when CSV contains different symbol.'''
        csv_data = "symbol,reportDate,fiscalDateEnding\nTSLA,2025-11-05,2025-09-30"
        
        mock_response = Mock()
        mock_response.content = csv_data.encode('utf-8')
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.__enter__ = Mock(return_value=mock_session_instance)
        mock_session_instance.__exit__ = Mock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        result = self.av._getEarningsAnnouncementsFromStock(stock=self.test_stock)
        
        # Should return empty list when symbol doesn't match
        self.assertEqual(len(result), 0)
    
    @patch('external.alpha_vantage.requests.Session')
    def test_get_earnings_invalid_date_format(self, mock_session):
        '''Test handling of invalid date format.'''
        csv_data = "symbol,reportDate,fiscalDateEnding\nAAPL,invalid-date,2025-09-30"
        
        mock_response = Mock()
        mock_response.content = csv_data.encode('utf-8')
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.__enter__ = Mock(return_value=mock_session_instance)
        mock_session_instance.__exit__ = Mock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        # Should skip invalid dates and return empty list
        result = self.av._getEarningsAnnouncementsFromStock(stock=self.test_stock)
        self.assertEqual(len(result), 0)
    
    def test_get_earnings_invalid_stock_type(self):
        '''Test with invalid stock type.'''
        with self.assertRaises(TypeError):
            self.av._getEarningsAnnouncementsFromStock(stock="not a stock") # pyright: ignore[reportArgumentType]
    
    @patch('external.alpha_vantage.requests.Session')
    def test_get_earnings_request_exception(self, mock_session):
        '''Test handling of request exception.'''
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.__enter__ = Mock(return_value=mock_session_instance)
        mock_session_instance.__exit__ = Mock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        with self.assertRaises(ValueError) as context:
            self.av._getEarningsAnnouncementsFromStock(stock=self.test_stock)
        
        self.assertIn('Error fetching earnings data', str(context.exception))


class TestGetDividendsFromStock(unittest.TestCase):
    '''Test _getDividendsFromStock method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
            self.av.source = 'AlphaVantage'
        
        self.test_stock = Stock(
            name='Apple Inc',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_dividends_success(self, mock_get):
        '''Test successful dividend fetch with all date types.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': [
                {
                    'ex_dividend_date': '2025-11-05',
                    'declaration_date': '2025-11-01',
                    'record_date': '2025-11-06',
                    'payment_date': '2025-11-15',
                    'amount': 0.25
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getDividendsFromStock(stock=self.test_stock)
        
        # Should create 4 events (one for each date type)
        self.assertEqual(len(result), 4)
        event_types = {event.type for event in result}
        self.assertEqual(event_types, {
            EventType.DIVIDEND_EX,
            EventType.DIVIDEND_DECLARATION,
            EventType.DIVIDEND_RECORD,
            EventType.DIVIDEND_PAYMENT
        })
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_dividends_partial_dates(self, mock_get):
        '''Test when only some dividend dates are present.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': [
                {
                    'ex_dividend_date': '2025-11-05',
                    'payment_date': '2025-11-15'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getDividendsFromStock(stock=self.test_stock)
        
        # Should only create 2 events
        self.assertEqual(len(result), 2)
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_dividends_wrong_symbol(self, mock_get):
        '''Test when API returns different symbol.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'TSLA',
            'data': []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getDividendsFromStock(stock=self.test_stock)
        
        self.assertEqual(len(result), 0)
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_dividends_invalid_date(self, mock_get):
        '''Test handling of invalid date format.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': [
                {
                    'ex_dividend_date': 'invalid-date'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Should skip invalid dates
        result = self.av._getDividendsFromStock(stock=self.test_stock)
        self.assertEqual(len(result), 0)
    
    def test_get_dividends_invalid_stock_type(self):
        '''Test with invalid stock type.'''
        with self.assertRaises(TypeError):
            self.av._getDividendsFromStock(stock=None) # pyright: ignore[reportArgumentType]
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_dividends_request_exception(self, mock_get):
        '''Test handling of request exception.'''
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with self.assertRaises(ValueError) as context:
            self.av._getDividendsFromStock(stock=self.test_stock)
        
        self.assertIn('Error fetching dividend data', str(context.exception))


class TestGetSplitsFromStock(unittest.TestCase):
    '''Test _getSplitsFromStock method.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        with patch('external.alpha_vantage.ExternalApiBaseDefinition.__init__', return_value=None):
            self.av = AlphaVantage()
            self.av.api_key = 'test_api_key'
            self.av.source = 'AlphaVantage'
        
        self.test_stock = Stock(
            name='Apple Inc',
            symbol='AAPL',
            last_updated=datetime.now(timezone.utc)
        )
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_splits_success(self, mock_get):
        '''Test successful stock split fetch.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': [
                {
                    'effective_date': '2020-08-31',
                    'split_factor': '4:1'
                },
                {
                    'effective_date': '2014-06-09',
                    'split_factor': '7:1'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getSplitsFromStock(stock=self.test_stock)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].type, EventType.STOCK_SPLIT)
        self.assertEqual(result[0].stock, self.test_stock)
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_splits_empty_data(self, mock_get):
        '''Test when no splits exist.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getSplitsFromStock(stock=self.test_stock)
        
        self.assertEqual(len(result), 0)
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_splits_wrong_symbol(self, mock_get):
        '''Test when API returns different symbol.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'TSLA',
            'data': [
                {
                    'effective_date': '2022-08-25',
                    'split_factor': '3:1'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.av._getSplitsFromStock(stock=self.test_stock)
        
        self.assertEqual(len(result), 0)
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_splits_invalid_date(self, mock_get):
        '''Test handling of invalid date format.'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'data': [
                {
                    'effective_date': 'not-a-date',
                    'split_factor': '2:1'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Should skip invalid dates
        result = self.av._getSplitsFromStock(stock=self.test_stock)
        self.assertEqual(len(result), 0)
    
    def test_get_splits_invalid_stock_type(self):
        '''Test with invalid stock type.'''
        with self.assertRaises(TypeError):
            self.av._getSplitsFromStock(stock=123) # pyright: ignore[reportArgumentType]
    
    @patch('external.alpha_vantage.requests.get')
    def test_get_splits_request_exception(self, mock_get):
        '''Test handling of request exception.'''
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.av._getSplitsFromStock(stock=self.test_stock)
        
        self.assertIn('Error fetching split data', str(context.exception))


if __name__ == '__main__':
    unittest.main()
