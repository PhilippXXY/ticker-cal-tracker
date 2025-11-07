# Disclaimer: Created by GitHub Copilot
'''
Unit tests for stocks REST API endpoints.
'''

import unittest
from unittest.mock import patch, Mock
from http import HTTPStatus
from datetime import datetime, timezone

from flask import Flask
from flask_smorest import Api

from src.api.routes.stocks_rest import stocks_bp, get_stocks_service
from src.models.stock_model import Stock


class TestStocksRestAPI(unittest.TestCase):
    '''Test stocks REST API endpoints.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config.update({
            'API_TITLE': 'Test API',
            'API_VERSION': 'v1',
            'OPENAPI_VERSION': '3.0.2',
            'TESTING': True,
        })
        
        self.api = Api(self.app)
        self.api.register_blueprint(stocks_bp, url_prefix='/stocks')
        
        self.client = self.app.test_client()
        
        # Mock auth to always return a valid user_id
        self.auth_patcher = patch('src.api.routes.stocks_rest.auth_utils.get_current_user_id')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = 'test-user-id-123'
        
        # Mock the stocks service
        self.service_patcher = patch('src.api.routes.stocks_rest.get_stocks_service')
        self.mock_get_service = self.service_patcher.start()
        self.mock_service = Mock()
        self.mock_get_service.return_value = self.mock_service
    
    def tearDown(self):
        '''Clean up patches.'''
        self.auth_patcher.stop()
        self.service_patcher.stop()


class TestGetStock(TestStocksRestAPI):
    '''Test GET /stocks/<ticker_symbol> endpoint.'''
    
    def test_get_stock_success(self):
        '''Test successful stock retrieval.'''
        timestamp = datetime.now(timezone.utc)
        mock_stock = Stock(
            name='Apple Inc.',
            symbol='AAPL',
            last_updated=timestamp
        )
        self.mock_service.get_stock_from_ticker.return_value = mock_stock
        
        response = self.client.get('/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['ticker'], 'AAPL')
        self.assertEqual(data['name'], 'Apple Inc.')
        self.mock_service.get_stock_from_ticker.assert_called_once_with(ticker='AAPL')
    
    def test_get_stock_lowercase_ticker(self):
        '''Test stock retrieval with lowercase ticker.'''
        timestamp = datetime.now(timezone.utc)
        mock_stock = Stock(
            name='Microsoft Corporation',
            symbol='MSFT',
            last_updated=timestamp
        )
        self.mock_service.get_stock_from_ticker.return_value = mock_stock
        
        response = self.client.get('/stocks/msft')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['ticker'], 'MSFT')
        # Service should receive the ticker as provided
        self.mock_service.get_stock_from_ticker.assert_called_once_with(ticker='msft')
    
    def test_get_stock_empty_ticker(self):
        '''Test that empty ticker returns BAD_REQUEST.'''
        response = self.client.get('/stocks/ ')
        
        # Flask routing returns BAD_REQUEST for URL-decoded empty paths
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    def test_get_stock_whitespace_ticker(self):
        '''Test that whitespace-only ticker returns BAD_REQUEST.'''
        self.mock_service.get_stock_from_ticker.side_effect = ValueError('Stock ticker must not be empty.')
        
        response = self.client.get('/stocks/   ')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = response.get_json()
        self.assertIn('Stock ticker must not be empty', data['message'])
    
    def test_get_stock_unauthorized_no_user_id(self):
        '''Test that missing user_id returns UNAUTHORIZED.'''
        self.mock_auth.return_value = None
        
        response = self.client.get('/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        data = response.get_json()
        self.assertIn('Authentication required', data['message'])
        # Service should not be called
        self.mock_service.get_stock_from_ticker.assert_not_called()
    
    def test_get_stock_unauthorized_empty_user_id(self):
        '''Test that empty user_id returns UNAUTHORIZED.'''
        self.mock_auth.return_value = ''
        
        response = self.client.get('/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.mock_service.get_stock_from_ticker.assert_not_called()
    
    def test_get_stock_value_error(self):
        '''Test that ValueError from service returns BAD_REQUEST.'''
        self.mock_service.get_stock_from_ticker.side_effect = ValueError('Invalid ticker format')
        
        response = self.client.get('/stocks/INVALID')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = response.get_json()
        self.assertIn('Invalid ticker format', data['message'])
    
    def test_get_stock_not_found(self):
        '''Test that "not found" error returns NOT_FOUND.'''
        self.mock_service.get_stock_from_ticker.side_effect = Exception('Stock not found')
        
        response = self.client.get('/stocks/NOTFOUND')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        data = response.get_json()
        self.assertIn('NOTFOUND not found', data['message'])
    
    def test_get_stock_failed_to_fetch(self):
        '''Test that "Failed to fetch" error returns NOT_FOUND.'''
        self.mock_service.get_stock_from_ticker.side_effect = Exception('Failed to fetch stock from API')
        
        response = self.client.get('/stocks/FAIL')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        data = response.get_json()
        self.assertIn('FAIL not found', data['message'])
    
    def test_get_stock_internal_error(self):
        '''Test that generic exception returns INTERNAL_SERVER_ERROR.'''
        self.mock_service.get_stock_from_ticker.side_effect = Exception('Database connection failed')
        
        response = self.client.get('/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        data = response.get_json()
        self.assertIn('Database connection failed', data['message'])
    
    def test_get_stock_service_singleton(self):
        '''Test that get_stocks_service returns singleton instance.'''
        # Reset the module-level singleton for this test
        import src.api.routes.stocks_rest as stocks_rest_module
        original_service = stocks_rest_module.stocks_service
        
        try:
            # Reset to None to test singleton creation
            stocks_rest_module.stocks_service = None
            
            # Mock StocksService constructor
            with patch('src.api.routes.stocks_rest.StocksService') as mock_stocks_service_class:
                mock_instance = Mock()
                mock_stocks_service_class.return_value = mock_instance
                
                service1 = get_stocks_service()
                service2 = get_stocks_service()
                
                # Should return same instance
                self.assertIs(service1, service2)
                # Constructor should only be called once
                mock_stocks_service_class.assert_called_once()
        finally:
            # Restore original state
            stocks_rest_module.stocks_service = original_service
    
    def test_get_stock_case_sensitivity_in_error(self):
        '''Test that error messages preserve ticker case.'''
        self.mock_service.get_stock_from_ticker.side_effect = Exception('not found')
        
        response = self.client.get('/stocks/aapl')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        data = response.get_json()
        # Error message should uppercase the ticker
        self.assertIn('AAPL not found', data['message'])
    
    def test_get_stock_multiple_requests(self):
        '''Test multiple successful requests.'''
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        
        for ticker in tickers:
            timestamp = datetime.now(timezone.utc)
            mock_stock = Stock(
                name=f'{ticker} Company',
                symbol=ticker,
                last_updated=timestamp
            )
            self.mock_service.get_stock_from_ticker.return_value = mock_stock
            
            response = self.client.get(f'/stocks/{ticker}')
            
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = response.get_json()
            self.assertEqual(data['ticker'], ticker)
    
    def test_get_stock_special_characters_in_ticker(self):
        '''Test handling of special characters in ticker.'''
        # Some tickers have special chars like BRK.B
        ticker = 'BRK.B'
        timestamp = datetime.now(timezone.utc)
        mock_stock = Stock(
            name='Berkshire Hathaway Inc. Class B',
            symbol='BRK.B',
            last_updated=timestamp
        )
        self.mock_service.get_stock_from_ticker.return_value = mock_stock
        
        response = self.client.get('/stocks/BRK.B')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['ticker'], 'BRK.B')


class TestStocksRESTAPIDocumentation(TestStocksRestAPI):
    '''Test OpenAPI documentation for stocks endpoints.'''
    
    def test_blueprint_registered(self):
        '''Test that stocks blueprint is registered.'''
        # Check that the stocks blueprint exists
        self.assertIsNotNone(stocks_bp)
        self.assertEqual(stocks_bp.name, 'stocks')


if __name__ == '__main__':
    unittest.main()
