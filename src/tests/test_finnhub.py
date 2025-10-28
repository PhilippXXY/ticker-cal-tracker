# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys
from datetime import datetime, timezone

# Add parent directory to sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from external.finnhub import Finnhub
from models.stock_model import Stock


class TestFinnhub(unittest.TestCase):
    """
    Comprehensive unit tests for the Finnhub API client.
    
    Tests all public methods and error conditions with mocked API responses.
    """
    
    def setUp(self):
        """
        Set up test fixtures with mocked environment and Finnhub client.
        """
        # Mock environment variable for API key
        self.api_key_patch = patch.dict(os.environ, {'API_KEY_FINNHUB': 'test_api_key'})
        self.api_key_patch.start()
        
        # Mock the Finnhub client
        self.finnhub_client_patch = patch('external.finnhub.finnhub.Client')
        self.mock_client_class = self.finnhub_client_patch.start()
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        
        # Initialize Finnhub instance
        self.finnhub_api = Finnhub()
    
    def tearDown(self):
        """Clean up patches after each test."""
        self.finnhub_client_patch.stop()
        self.api_key_patch.stop()
    
    # ===== Tests for getStockInfoFromSymbol =====
    
    def test_getStockInfoFromSymbol_success(self):
        """Test successful symbol lookup with complete data."""
        # Mock API response
        mock_response = {
            'name': 'Apple Inc.',
            'ticker': 'AAPL'
        }
        self.mock_client.company_profile2.return_value = mock_response
        
        # Execute test
        result = self.finnhub_api.getStockInfoFromSymbol(symbol='AAPL')
        
        # Assertions
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'AAPL')
        self.assertEqual(result.name, 'Apple Inc.')
        self.assertIsInstance(result.last_updated, datetime)
        
        # Verify API call
        self.mock_client.company_profile2.assert_called_once_with(symbol='AAPL')
    
    def test_getStockInfoFromSymbol_success_minimal_data(self):
        """Test successful symbol lookup with minimal data."""
        # Mock API response with minimal data
        mock_response = {
            'name': 'Test Company Inc.',
            'ticker': 'TEST'
        }
        self.mock_client.company_profile2.return_value = mock_response
        
        # Execute test
        result = self.finnhub_api.getStockInfoFromSymbol(symbol='TEST')
        
        # Assertions
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'TEST')
        self.assertEqual(result.name, 'Test Company Inc.')
        self.assertIsInstance(result.last_updated, datetime)
    
    def test_getStockInfoFromSymbol_no_data_found(self):
        """Test symbol lookup when no data is returned."""
        # Mock empty API response
        self.mock_client.company_profile2.return_value = {}
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromSymbol(symbol='INVALID')
        
        self.assertIn("No stock data found for symbol: INVALID", str(context.exception))
    
    def test_getStockInfoFromSymbol_api_exception(self):
        """Test symbol lookup when API throws an exception."""
        # Mock API exception
        self.mock_client.company_profile2.side_effect = Exception("API Error")
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromSymbol(symbol='AAPL')
        
        self.assertIn("Error fetching stock data for symbol AAPL", str(context.exception))
        self.assertIn("API Error", str(context.exception))
    
    def test_getStockInfoFromSymbol_empty_symbol(self):
        """Test symbol lookup with empty symbol."""
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromSymbol(symbol='')
        
        self.assertIn("Invalid symbol provided:", str(context.exception))
    
    def test_getStockInfoFromSymbol_none_symbol(self):
        """Test symbol lookup with None symbol."""
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromSymbol(symbol=None)  # type: ignore
        
        self.assertIn("Invalid symbol provided:", str(context.exception))
    
    # ===== Tests for getStockInfoFromName =====
    
    def test_getStockInfoFromName_success(self):
        """Test successful name lookup with complete flow."""
        # Mock search response
        mock_search_response = {
            'result': [
                {
                    'symbol': 'MSFT',
                    'description': 'Microsoft Corporation'
                }
            ]
        }
        self.mock_client.symbol_lookup.return_value = mock_search_response
        
        # Mock profile response
        mock_profile_response = {
            'name': 'Microsoft Corporation',
            'ticker': 'MSFT'
        }
        self.mock_client.company_profile2.return_value = mock_profile_response
        
        # Execute test
        result = self.finnhub_api.getStockInfoFromName(name='Microsoft')
        
        # Assertions
        self.assertIsInstance(result, Stock)
        self.assertEqual(result.symbol, 'MSFT')
        self.assertEqual(result.name, 'Microsoft Corporation')
        self.assertIsInstance(result.last_updated, datetime)
        
        # Verify API calls
        self.mock_client.symbol_lookup.assert_called_once_with('Microsoft')
        self.mock_client.company_profile2.assert_called_once_with(symbol='MSFT')
    
    def test_getStockInfoFromName_no_search_results(self):
        """Test name lookup when no search results are found."""
        # Mock empty search response
        mock_search_response = {'result': []}
        self.mock_client.symbol_lookup.return_value = mock_search_response
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='NonexistentCompany')
        
        self.assertIn("No stocks found for name: NonexistentCompany", str(context.exception))
    
    def test_getStockInfoFromName_no_symbol_in_search_result(self):
        """Test name lookup when search result has no symbol."""
        # Mock search response without symbol
        mock_search_response = {
            'result': [
                {
                    'description': 'Some Company'
                    # Missing 'symbol' key
                }
            ]
        }
        self.mock_client.symbol_lookup.return_value = mock_search_response
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='SomeCompany')
        
        self.assertIn("No valid symbol found in search results", str(context.exception))
    
    def test_getStockInfoFromName_profile_lookup_fails(self):
        """Test name lookup when profile lookup fails."""
        # Mock successful search response
        mock_search_response = {
            'result': [{'symbol': 'TEST'}]
        }
        self.mock_client.symbol_lookup.return_value = mock_search_response
        
        # Mock empty profile response
        self.mock_client.company_profile2.return_value = {}
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='TestCompany')
        
        self.assertIn("No detailed data found for symbol: TEST", str(context.exception))
    
    def test_getStockInfoFromName_search_exception(self):
        """Test name lookup when search API throws exception."""
        # Mock search exception
        self.mock_client.symbol_lookup.side_effect = Exception("Search API Error")
        
        # Execute test and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='TestCompany')
        
        self.assertIn("Error fetching stock data for name 'TestCompany'", str(context.exception))
        self.assertIn("Search API Error", str(context.exception))
    
    def test_getStockInfoFromName_empty_name(self):
        """Test name lookup with empty name."""
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='')
        
        self.assertIn("Invalid name provided:", str(context.exception))
    
    def test_getStockInfoFromName_whitespace_only_name(self):
        """Test name lookup with whitespace-only name."""
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name='   ')
        
        self.assertIn("Invalid name provided:", str(context.exception))
    
    def test_getStockInfoFromName_none_name(self):
        """Test name lookup with None name."""
        with self.assertRaises(ValueError) as context:
            self.finnhub_api.getStockInfoFromName(name=None)  # type: ignore
        
        self.assertIn("Invalid name provided:", str(context.exception))
    
    # ===== Tests for Initialization =====
    
    @patch('external.finnhub.finnhub.Client')
    def test_initialization_success(self, mock_client_class):
        """Test successful initialization with valid API key."""
        with patch.dict(os.environ, {'API_KEY_FINNHUB': 'valid_api_key'}):
            finnhub_instance = Finnhub()
            
            # Verify client was initialized with correct API key
            mock_client_class.assert_called_once_with(api_key='valid_api_key')
    
    @patch('external.finnhub.finnhub.Client')
    def test_initialization_missing_api_key(self, mock_client_class):
        """Test initialization failure when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                Finnhub()
            
            self.assertIn("API key 'API_KEY_FINNHUB' not found in environment variables", str(context.exception))
    
    # ===== Integration-style Tests =====
    
    def test_datetime_timezone_consistency(self):
        """Test that all methods return datetime objects with UTC timezone."""
        # Mock response for symbol lookup
        mock_response = {
            'name': 'Test Company',
            'ticker': 'TEST'
        }
        self.mock_client.company_profile2.return_value = mock_response
        
        # Test symbol lookup
        result_symbol = self.finnhub_api.getStockInfoFromSymbol(symbol='TEST')
        self.assertEqual(result_symbol.last_updated.tzinfo, timezone.utc)
        
        # Test name lookup (requires additional mock setup)
        mock_search_response = {'result': [{'symbol': 'TEST'}]}
        self.mock_client.symbol_lookup.return_value = mock_search_response
        
        result_name = self.finnhub_api.getStockInfoFromName(name='Test Company')
        self.assertEqual(result_name.last_updated.tzinfo, timezone.utc)


if __name__ == '__main__':
    unittest.main()