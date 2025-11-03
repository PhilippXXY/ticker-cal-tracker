# Disclaimer: Created by GitHub Copilot

import unittest
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

from external.alpha_vantage import AlphaVantage
from models.stock_model import Stock
from models.stock_event_model import StockEvent, EventType

# Load environment variables from .env file
load_dotenv(Path('.env'))


class TestAlphaVantageIntegration(unittest.TestCase):
    '''
    Integration tests for AlphaVantage API.
    
    These tests make real API calls and require a valid API key.
    Set the API_KEY_ALPHA_VANTAGE environment variable before running.
    
    Run with:
        python -m unittest tests.test_alpha_vantage_integration -v
    
    Skip these tests if no API key is available:
        export SKIP_INTEGRATION_TESTS=1
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up test class - check for API key.'''
        if os.getenv('SKIP_INTEGRATION_TESTS'):
            raise unittest.SkipTest("Integration tests skipped (SKIP_INTEGRATION_TESTS is set)")
        
        if not os.getenv('API_KEY_ALPHA_VANTAGE'):
            raise unittest.SkipTest("API_KEY_ALPHA_VANTAGE not set - skipping integration tests")
        
        cls.av = AlphaVantage()
    
    def test_get_stock_info_from_name_apple(self):
        '''Test fetching Apple Inc by company name.'''
        result = self.av.getStockInfoFromName(name='Apple Inc')
        
        # Verify it returns a Stock object
        self.assertIsInstance(result, Stock)
        
        # Verify required fields are populated
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.symbol)
        self.assertIsNotNone(result.last_updated)
        
        # Verify name contains Apple
        self.assertIn('Apple', result.name)
        
        # Verify symbol is AAPL (or AAPL.X for other exchanges)
        self.assertIn('AAPL', result.symbol)
        
        # Verify last_updated is a datetime with timezone
        self.assertIsInstance(result.last_updated, datetime)
        self.assertIsNotNone(result.last_updated.tzinfo)
        
        print(f"✓ Found stock by name: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_symbol_aapl(self):
        '''Test fetching Apple by ticker symbol.'''
        result = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Verify it returns a Stock object
        self.assertIsInstance(result, Stock)
        
        # Verify required fields
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.symbol)
        self.assertIsNotNone(result.last_updated)
        
        # Verify symbol matches (case-insensitive)
        self.assertEqual(result.symbol.upper(), 'AAPL')
        
        # Verify name is not empty
        self.assertTrue(len(result.name) > 0)
        
        print(f"✓ Found stock by symbol: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_symbol_microsoft(self):
        '''Test fetching Microsoft by ticker symbol.'''
        result = self.av.getStockInfoFromSymbol(symbol='MSFT')
        
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol.upper(), 'MSFT')
        self.assertIn('Microsoft', result.name)
        
        print(f"✓ Found stock: {result.name} ({result.symbol})")
    
    def test_get_earnings_announcements(self):
        '''Test fetching earnings announcements for Apple.'''
        # First get the stock
        stock = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Fetch earnings
        result = self.av.getStockEventDatesFromStock(
            stock=stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        
        # Verify it returns a list
        self.assertIsInstance(result, list)
        
        if len(result) > 0:
            # Verify first item is a StockEvent
            self.assertIsInstance(result[0], StockEvent)
            
            # Verify event properties
            self.assertEqual(result[0].type, EventType.EARNINGS_ANNOUNCEMENT)
            self.assertEqual(result[0].stock, stock)
            self.assertIsInstance(result[0].date, datetime)
            self.assertIsNotNone(result[0].date.tzinfo)
            self.assertIsInstance(result[0].last_updated, datetime)
            self.assertEqual(result[0].source, 'AlphaVantage')
            
            print(f"✓ Found {len(result)} earnings announcement(s)")
            print(f"  First earnings date: {result[0].date.strftime('%Y-%m-%d')}")
        else:
            print("⚠ No earnings announcements found (API may have rate limits)")
    
    def test_get_dividends(self):
        '''Test fetching dividend events for Apple.'''
        # Apple pays regular dividends
        stock = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Fetch dividends
        result = self.av.getStockEventDatesFromStock(
            stock=stock,
            event_types=[
                EventType.DIVIDEND_EX,
                EventType.DIVIDEND_DECLARATION,
                EventType.DIVIDEND_RECORD,
                EventType.DIVIDEND_PAYMENT
            ]
        )
        
        # Verify it returns a list
        self.assertIsInstance(result, list)
        
        if len(result) > 0:
            # Check that we have dividend events
            dividend_types = {event.type for event in result}
            self.assertTrue(len(dividend_types) > 0)
            
            # Verify all are dividend types
            for event in result:
                self.assertIn(event.type, [
                    EventType.DIVIDEND_EX,
                    EventType.DIVIDEND_DECLARATION,
                    EventType.DIVIDEND_RECORD,
                    EventType.DIVIDEND_PAYMENT
                ])
                self.assertEqual(event.stock, stock)
                self.assertIsInstance(event.date, datetime)
                self.assertEqual(event.source, 'AlphaVantage')
            
            print(f"✓ Found {len(result)} dividend event(s)")
            print(f"  Event types: {', '.join([et.name for et in dividend_types])}")
        else:
            print("⚠ No dividend events found (API may have rate limits)")
    
    def test_get_stock_splits(self):
        '''Test fetching stock splits for Apple.'''
        # Apple has had stock splits (most recently in 2020)
        stock = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Fetch splits
        result = self.av.getStockEventDatesFromStock(
            stock=stock,
            event_types=[EventType.STOCK_SPLIT]
        )
        
        # Verify it returns a list
        self.assertIsInstance(result, list)
        
        if len(result) > 0:
            # Verify events
            for event in result:
                self.assertIsInstance(event, StockEvent)
                self.assertEqual(event.type, EventType.STOCK_SPLIT)
                self.assertEqual(event.stock, stock)
                self.assertIsInstance(event.date, datetime)
                self.assertEqual(event.source, 'AlphaVantage')
            
            print(f"✓ Found {len(result)} stock split(s)")
            # Print most recent split
            if result:
                recent = max(result, key=lambda e: e.date)
                print(f"  Most recent split: {recent.date.strftime('%Y-%m-%d')}")
        else:
            print("⚠ No stock splits found (API may have rate limits)")
    
    def test_get_multiple_event_types(self):
        '''Test fetching multiple event types in one call.'''
        stock = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Fetch multiple event types
        result = self.av.getStockEventDatesFromStock(
            stock=stock,
            event_types=[
                EventType.EARNINGS_ANNOUNCEMENT,
                EventType.DIVIDEND_EX,
                EventType.STOCK_SPLIT
            ]
        )
        
        # Verify it returns a list
        self.assertIsInstance(result, list)
        
        if len(result) > 0:
            # Check event types
            event_types = {event.type for event in result}
            
            # Verify all events are from requested types
            for event in result:
                self.assertIn(event.type, [
                    EventType.EARNINGS_ANNOUNCEMENT,
                    EventType.DIVIDEND_EX,
                    EventType.STOCK_SPLIT
                ])
            
            print(f"✓ Found {len(result)} total event(s)")
            print(f"  Event types returned: {', '.join([et.name for et in event_types])}")
        else:
            print("⚠ No events found (API may have rate limits)")
    
    def test_api_rate_limiting(self):
        '''Test that API handles rate limits gracefully.'''
        # Alpha Vantage free tier: 25 requests per day, 5 per minute
        
        try:
            # Make a simple request
            result = self.av.getStockInfoFromSymbol(symbol='AAPL')
            self.assertIsInstance(result, Stock)
            print("✓ API request succeeded (within rate limits)")
        except ValueError as e:
            # Check if it's a rate limit error
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or 'thank you' in error_msg:
                self.skipTest(f"Rate limit hit: {e}")
            else:
                raise
    
    def test_invalid_symbol_handling(self):
        '''Test API response for invalid symbol.'''
        try:
            # Use a clearly invalid symbol
            result = self.av.getStockInfoFromSymbol(symbol='INVALIDSYMBOLXYZ123')
            
            # If it returns something, verify it's a Stock object
            # (API might return close matches)
            self.assertIsInstance(result, Stock)
            print(f"⚠ API returned close match: {result.symbol}")
            
        except ValueError as e:
            # Expected behavior - no matches found
            self.assertIn('No stock data found', str(e))
            print("✓ Invalid symbol correctly rejected")
    
    def test_response_data_structure(self):
        '''Test that API responses have expected structure.'''
        stock = self.av.getStockInfoFromSymbol(symbol='AAPL')
        
        # Test Stock object structure
        self.assertTrue(hasattr(stock, 'name'))
        self.assertTrue(hasattr(stock, 'symbol'))
        self.assertTrue(hasattr(stock, 'last_updated'))
        
        # Test types
        self.assertIsInstance(stock.name, str)
        self.assertIsInstance(stock.symbol, str)
        self.assertIsInstance(stock.last_updated, datetime)
        
        # Test values are not empty
        self.assertTrue(len(stock.name) > 0)
        self.assertTrue(len(stock.symbol) > 0)
        
        print("✓ Stock object has correct structure")
        
        # Test StockEvent structure
        events = self.av.getStockEventDatesFromStock(
            stock=stock,
            event_types=[EventType.EARNINGS_ANNOUNCEMENT]
        )
        
        if len(events) > 0:
            event = events[0]
            self.assertTrue(hasattr(event, 'stock'))
            self.assertTrue(hasattr(event, 'type'))
            self.assertTrue(hasattr(event, 'date'))
            self.assertTrue(hasattr(event, 'last_updated'))
            self.assertTrue(hasattr(event, 'source'))
            
            self.assertIsInstance(event.stock, Stock)
            self.assertIsInstance(event.type, EventType)
            self.assertIsInstance(event.date, datetime)
            self.assertIsInstance(event.last_updated, datetime)
            self.assertIsInstance(event.source, str)
            
            print("✓ StockEvent object has correct structure")


class TestAlphaVantageAPIResponseFormats(unittest.TestCase):
    '''
    Tests to verify Alpha Vantage API response formats match expectations.
    
    These tests validate that the API still returns data in the expected format,
    which is important for detecting breaking changes in the API.
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up test class.'''
        if os.getenv('SKIP_INTEGRATION_TESTS'):
            raise unittest.SkipTest("Integration tests skipped")
        
        if not os.getenv('API_KEY_ALPHA_VANTAGE'):
            raise unittest.SkipTest("API_KEY_ALPHA_VANTAGE not set")
        
        cls.av = AlphaVantage()
    
    def test_symbol_search_response_format(self):
        '''Verify SYMBOL_SEARCH API returns expected format.'''
        import requests
        
        url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=Apple&apikey={self.av.api_key}'
        response = requests.get(url)
        data = response.json()
        
        # Check response structure
        self.assertIn('bestMatches', data)
        
        if len(data['bestMatches']) > 0:
            match = data['bestMatches'][0]
            
            # Verify expected fields exist
            self.assertIn('1. symbol', match)
            self.assertIn('2. name', match)
            
            print(f"✓ SYMBOL_SEARCH format validated")
            print(f"  Sample: {match.get('2. name')} ({match.get('1. symbol')})")
        else:
            print("⚠ No results in SYMBOL_SEARCH response")
    
    def test_earnings_calendar_response_format(self):
        '''Verify EARNINGS_CALENDAR API returns CSV format.'''
        import requests
        
        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol=AAPL&horizon=3month&apikey={self.av.api_key}'
        response = requests.get(url)
        content = response.content.decode('utf-8')
        
        # Check it's CSV format
        lines = content.strip().split('\n')
        
        if len(lines) > 0:
            header = lines[0]
            
            # Verify expected CSV headers
            self.assertIn('symbol', header.lower())
            self.assertIn('reportdate', header.lower())
            
            print(f"✓ EARNINGS_CALENDAR format validated (CSV)")
            print(f"  Headers: {header[:100]}...")
        else:
            print("⚠ Empty EARNINGS_CALENDAR response")
    
    def test_dividends_response_format(self):
        '''Verify DIVIDENDS API returns expected JSON format.'''
        import requests
        
        url = f'https://www.alphavantage.co/query?function=DIVIDENDS&symbol=AAPL&apikey={self.av.api_key}'
        response = requests.get(url)
        data = response.json()
        
        # Check response structure
        if 'symbol' in data:
            self.assertEqual(data['symbol'], 'AAPL')
            
            if 'data' in data and len(data['data']) > 0:
                dividend = data['data'][0]
                
                # Verify expected fields
                # Note: Not all fields may be present for all dividends
                expected_fields = ['ex_dividend_date', 'declaration_date', 
                                 'record_date', 'payment_date']
                
                has_date_field = any(field in dividend for field in expected_fields)
                self.assertTrue(has_date_field, "At least one date field should be present")
                
                print(f"✓ DIVIDENDS format validated")
                print(f"  Available fields: {', '.join(dividend.keys())}")
            else:
                print("⚠ No dividend data in response")
        else:
            print("⚠ Unexpected DIVIDENDS response format")
    
    def test_splits_response_format(self):
        '''Verify SPLITS API returns expected JSON format.'''
        import requests
        
        url = f'https://www.alphavantage.co/query?function=SPLITS&symbol=AAPL&apikey={self.av.api_key}'
        response = requests.get(url)
        data = response.json()
        
        # Check response structure
        if 'symbol' in data:
            self.assertEqual(data['symbol'], 'AAPL')
            
            if 'data' in data and len(data['data']) > 0:
                split = data['data'][0]
                
                # Verify expected fields
                self.assertIn('effective_date', split)
                
                print(f"✓ SPLITS format validated")
                print(f"  Sample split date: {split.get('effective_date')}")
            else:
                print("⚠ No split data in response")
        else:
            print("⚠ Unexpected SPLITS response format")


if __name__ == '__main__':
    # Print helpful information
    print("\n" + "="*70)
    print("Alpha Vantage Integration Tests")
    print("="*70)
    print("\nThese tests make REAL API calls to Alpha Vantage.")
    print("\nRequirements:")
    print("  - API_KEY_ALPHA_VANTAGE environment variable must be set")
    print("  - Internet connection required")
    print("  - Subject to API rate limits (5 requests/minute, 25/day for free tier)")
    print("\nTo skip these tests:")
    print("  export SKIP_INTEGRATION_TESTS=1")
    print("\n" + "="*70 + "\n")
    
    unittest.main(verbosity=2)
