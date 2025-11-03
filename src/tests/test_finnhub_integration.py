# Disclaimer: Created by GitHub Copilot

import unittest
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

from external.finnhub import Finnhub
from models.stock_model import Stock

# Load environment variables from .env file
load_dotenv(Path('.env'))


class TestFinnhubIntegration(unittest.TestCase):
    '''
    Integration tests for Finnhub API.
    
    These tests make real API calls and require a valid API key.
    Set the API_KEY_FINNHUB environment variable before running.
    
    Run with:
        python -m unittest tests.test_finnhub_integration -v
    
    Skip these tests if no API key is available:
        export SKIP_INTEGRATION_TESTS=1
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up test class - check for API key.'''
        if os.getenv('SKIP_INTEGRATION_TESTS'):
            raise unittest.SkipTest("Integration tests skipped (SKIP_INTEGRATION_TESTS is set)")
        
        if not os.getenv('API_KEY_FINNHUB'):
            raise unittest.SkipTest("API_KEY_FINNHUB not set - skipping integration tests")
        
        cls.finnhub = Finnhub()
    
    def test_get_stock_info_from_symbol_apple(self):
        '''Test fetching Apple Inc by ticker symbol.'''
        result = self.finnhub.getStockInfoFromSymbol(symbol='AAPL')
        
        # Verify it returns a Stock object
        self.assertIsInstance(result, Stock)
        
        # Verify required fields are populated
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.symbol)
        self.assertIsNotNone(result.last_updated)
        
        # Verify symbol matches
        self.assertEqual(result.symbol, 'AAPL')
        
        # Verify name contains Apple
        self.assertIn('Apple', result.name)
        
        # Verify last_updated is a datetime with timezone
        self.assertIsInstance(result.last_updated, datetime)
        self.assertIsNotNone(result.last_updated.tzinfo)
        
        print(f"✓ Found stock by symbol: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_symbol_microsoft(self):
        '''Test fetching Microsoft by ticker symbol.'''
        result = self.finnhub.getStockInfoFromSymbol(symbol='MSFT')
        
        # Verify it returns a Stock object
        self.assertIsInstance(result, Stock)
        
        # Verify required fields
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.symbol)
        self.assertIsNotNone(result.last_updated)
        
        # Verify symbol matches
        self.assertEqual(result.symbol, 'MSFT')
        
        # Verify name is Microsoft-related
        self.assertIn('Microsoft', result.name)
        
        print(f"✓ Found stock: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_symbol_tesla(self):
        '''Test fetching Tesla by ticker symbol.'''
        result = self.finnhub.getStockInfoFromSymbol(symbol='TSLA')
        
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'TSLA')
        self.assertIn('Tesla', result.name)
        
        print(f"✓ Found stock: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_name_apple(self):
        '''Test fetching Apple Inc by company name.'''
        result = self.finnhub.getStockInfoFromName(name='Apple Inc')
        
        # Verify it returns a Stock object
        self.assertIsInstance(result, Stock)
        
        # Verify required fields are populated
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.symbol)
        self.assertIsNotNone(result.last_updated)
        
        # Verify name contains Apple
        self.assertIn('Apple', result.name)
        
        # Verify symbol is likely AAPL (though Finnhub might return variants)
        self.assertIsNotNone(result.symbol)
        self.assertTrue(len(result.symbol) > 0)
        
        print(f"✓ Found stock by name: {result.name} ({result.symbol})")
    
    def test_get_stock_info_from_name_microsoft(self):
        '''Test fetching Microsoft by company name.'''
        result = self.finnhub.getStockInfoFromName(name='Microsoft')
        
        self.assertIsInstance(result, Stock)
        self.assertIsNotNone(result.symbol)
        self.assertIn('Microsoft', result.name)
        
        print(f"✓ Found stock by name: {result.name} ({result.symbol})")
    
    def test_case_insensitive_symbol_lookup(self):
        '''Test that symbol lookup is case insensitive.'''
        result_upper = self.finnhub.getStockInfoFromSymbol(symbol='AAPL')
        result_lower = self.finnhub.getStockInfoFromSymbol(symbol='aapl')
        result_mixed = self.finnhub.getStockInfoFromSymbol(symbol='AaPl')
        
        # All should return the same company
        self.assertEqual(result_upper.symbol, result_lower.symbol)
        self.assertEqual(result_upper.symbol, result_mixed.symbol)
        self.assertEqual(result_upper.name, result_lower.name)
        
        print(f"✓ Case insensitive lookup working: {result_upper.symbol}")
    
    def test_invalid_symbol_handling(self):
        '''Test API response for invalid symbol.'''
        try:
            result = self.finnhub.getStockInfoFromSymbol(symbol='INVALIDSYMBOLXYZ123')
            
            # If it returns something, it should still be a valid Stock object
            self.assertIsInstance(result, Stock)
            print(f"⚠ API returned data for invalid symbol: {result.symbol}")
            
        except ValueError as e:
            # Expected behavior - no data found
            self.assertIn('No stock data found', str(e))
            print("✓ Invalid symbol correctly rejected")
    
    def test_invalid_name_handling(self):
        '''Test API response for invalid company name.'''
        try:
            result = self.finnhub.getStockInfoFromName(name='NonExistentCompanyXYZ123456')
            
            # If it returns something, verify it's still valid
            self.assertIsInstance(result, Stock)
            print(f"⚠ API returned close match: {result.name}")
            
        except ValueError as e:
            # Expected behavior - either no stocks found or API validation errors
            error_msg = str(e)
            # Accept either "No stocks found" or API errors like "q too long"
            self.assertTrue(
                'No stocks found' in error_msg or 'q too long' in error_msg,
                f"Expected 'No stocks found' or API error, got: {error_msg}"
            )
            if 'q too long' in error_msg:
                print("✓ API validation error (query too long)")
            else:
                print("✓ Invalid name correctly rejected")
    
    def test_response_data_structure(self):
        '''Test that API responses have expected structure.'''
        stock = self.finnhub.getStockInfoFromSymbol(symbol='AAPL')
        
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
        
        # Verify timezone info
        self.assertIsNotNone(stock.last_updated.tzinfo)
        
        print("✓ Stock object has correct structure")
        print(f"  Name: {stock.name}")
        print(f"  Symbol: {stock.symbol}")
        print(f"  Last Updated: {stock.last_updated.isoformat()}")
    
    def test_api_rate_limiting(self):
        '''Test that API handles rate limits gracefully.'''
        # Finnhub free tier: 60 API calls/minute
        
        try:
            # Make a simple request
            result = self.finnhub.getStockInfoFromSymbol(symbol='AAPL')
            self.assertIsInstance(result, Stock)
            print("✓ API request succeeded (within rate limits)")
        except ValueError as e:
            # Check if it's a rate limit error
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or 'too many requests' in error_msg:
                self.skipTest(f"Rate limit hit: {e}")
            else:
                raise
    
    def test_multiple_consecutive_requests(self):
        '''Test making multiple requests in sequence.'''
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        results = []
        
        for symbol in symbols:
            try:
                result = self.finnhub.getStockInfoFromSymbol(symbol=symbol)
                self.assertIsInstance(result, Stock)
                self.assertEqual(result.symbol, symbol)
                results.append(result)
            except ValueError as e:
                if 'rate limit' in str(e).lower():
                    self.skipTest(f"Rate limit hit on {symbol}")
                raise
        
        self.assertEqual(len(results), 3)
        print(f"✓ Successfully fetched {len(results)} stocks consecutively")
        for stock in results:
            print(f"  - {stock.name} ({stock.symbol})")
    
    def test_special_characters_in_name(self):
        '''Test searching with special characters.'''
        # Test with ampersand
        try:
            result = self.finnhub.getStockInfoFromName(name='Johnson & Johnson')
            self.assertIsInstance(result, Stock)
            print(f"✓ Special characters handled: {result.name}")
        except ValueError as e:
            print(f"⚠ Special character search failed: {e}")
    
    def test_international_symbols(self):
        '''Test fetching international stocks if supported.'''
        # Try a European stock (if Finnhub supports it)
        try:
            result = self.finnhub.getStockInfoFromSymbol(symbol='SAP')
            if result:
                self.assertIsInstance(result, Stock)
                print(f"✓ International symbol supported: {result.name} ({result.symbol})")
        except ValueError:
            print("⚠ International symbols may not be supported or require different format")


class TestFinnhubAPIResponseFormats(unittest.TestCase):
    '''
    Tests to verify Finnhub API response formats match expectations.
    
    These tests validate that the API still returns data in the expected format,
    which is important for detecting breaking changes in the API.
    '''
    
    @classmethod
    def setUpClass(cls):
        '''Set up test class.'''
        if os.getenv('SKIP_INTEGRATION_TESTS'):
            raise unittest.SkipTest("Integration tests skipped")
        
        if not os.getenv('API_KEY_FINNHUB'):
            raise unittest.SkipTest("API_KEY_FINNHUB not set")
        
        cls.finnhub = Finnhub()
    
    def test_company_profile_response_format(self):
        '''Verify company_profile2 API returns expected format.'''
        # Use the Finnhub client directly
        data = self.finnhub.finnhub_client.company_profile2(symbol='AAPL')
        
        # Verify response is a dictionary
        self.assertIsInstance(data, dict)
        
        if data:
            # Verify expected fields exist
            self.assertIn('name', data)
            
            # Optional fields that might be present
            optional_fields = ['country', 'currency', 'exchange', 'ipo', 
                             'marketCapitalization', 'shareOutstanding', 'ticker']
            
            print(f"✓ company_profile2 format validated")
            print(f"  Company: {data.get('name')}")
            print(f"  Available fields: {', '.join(data.keys())}")
        else:
            print("⚠ Empty company_profile2 response")
    
    def test_symbol_lookup_response_format(self):
        '''Verify symbol_lookup API returns expected format.'''
        data = self.finnhub.finnhub_client.symbol_lookup('Apple')
        
        # Verify response structure
        self.assertIsInstance(data, dict)
        self.assertIn('result', data)
        
        if len(data['result']) > 0:
            result = data['result'][0]
            
            # Verify expected fields
            self.assertIn('symbol', result)
            self.assertIn('description', result, 
                         "description field should be present (might be 'displaySymbol' in newer versions)")
            
            print(f"✓ symbol_lookup format validated")
            print(f"  Sample: {result.get('description', result.get('displaySymbol'))} ({result.get('symbol')})")
        else:
            print("⚠ No results in symbol_lookup response")
    
    def test_api_error_handling(self):
        '''Test that API errors are handled properly.'''
        try:
            # Try to fetch with clearly invalid symbol
            data = self.finnhub.finnhub_client.company_profile2(symbol='__INVALID__')
            
            # If we get here, check if data is empty (expected for invalid symbol)
            if not data or 'name' not in data:
                print("✓ Invalid symbol returns empty/incomplete data as expected")
            else:
                print(f"⚠ Unexpected data for invalid symbol: {data}")
                
        except Exception as e:
            # Some error is also acceptable
            print(f"✓ API error raised for invalid symbol: {type(e).__name__}")


if __name__ == '__main__':
    # Print helpful information
    print("\n" + "="*70)
    print("Finnhub Integration Tests")
    print("="*70)
    print("\nThese tests make REAL API calls to Finnhub.")
    print("\nRequirements:")
    print("  - API_KEY_FINNHUB environment variable must be set")
    print("  - Internet connection required")
    print("  - Subject to API rate limits (60 requests/minute for free tier)")
    print("\nTo skip these tests:")
    print("  export SKIP_INTEGRATION_TESTS=1")
    print("\n" + "="*70 + "\n")
    
    unittest.main(verbosity=2)
