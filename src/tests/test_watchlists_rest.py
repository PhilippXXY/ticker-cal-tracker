# Disclaimer: Created by GitHub Copilot
'''
Unit tests for Watchlist REST API endpoints.
'''

import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from http import HTTPStatus

from flask import Flask
from flask_smorest import Api, abort

from src.api.routes.watchlists_rest import (
    watchlists_bp,
    get_watchlist_service,
    _extract_watchlist_settings,
)
from src.models.stock_event_model import EventType


class TestExtractWatchlistSettings(unittest.TestCase):
    '''Test _extract_watchlist_settings helper function.'''
    
    def test_extract_all_settings_with_defaults(self):
        '''Test extraction with all settings present and defaults enabled.'''
        payload = {
            'include_earnings_announcement': True,
            'include_dividend_ex': False,
            'include_dividend_declaration': True,
            'include_dividend_record': False,
            'include_dividend_payment': True,
            'include_stock_split': False,
        }
        
        result = _extract_watchlist_settings(payload, include_defaults=True)
        
        self.assertEqual(len(result), 6)
        self.assertTrue(result[EventType.EARNINGS_ANNOUNCEMENT])
        self.assertFalse(result[EventType.DIVIDEND_EX])
        self.assertTrue(result[EventType.DIVIDEND_DECLARATION])
        self.assertFalse(result[EventType.DIVIDEND_RECORD])
        self.assertTrue(result[EventType.DIVIDEND_PAYMENT])
        self.assertFalse(result[EventType.STOCK_SPLIT])
    
    def test_extract_partial_settings_with_defaults(self):
        '''Test extraction with partial settings and defaults enabled.'''
        payload = {
            'include_earnings_announcement': False,
            'include_dividend_ex': True,
        }
        
        result = _extract_watchlist_settings(payload, include_defaults=True)
        
        # Should have all 6 event types
        self.assertEqual(len(result), 6)
        self.assertFalse(result[EventType.EARNINGS_ANNOUNCEMENT])
        self.assertTrue(result[EventType.DIVIDEND_EX])
        # Others should default to True
        self.assertTrue(result[EventType.DIVIDEND_DECLARATION])
        self.assertTrue(result[EventType.DIVIDEND_RECORD])
        self.assertTrue(result[EventType.DIVIDEND_PAYMENT])
        self.assertTrue(result[EventType.STOCK_SPLIT])
    
    def test_extract_partial_settings_without_defaults(self):
        '''Test extraction with partial settings and defaults disabled.'''
        payload = {
            'include_earnings_announcement': False,
            'include_dividend_ex': True,
        }
        
        result = _extract_watchlist_settings(payload, include_defaults=False)
        
        # Should only have the provided settings
        self.assertEqual(len(result), 2)
        self.assertFalse(result[EventType.EARNINGS_ANNOUNCEMENT])
        self.assertTrue(result[EventType.DIVIDEND_EX])
    
    def test_extract_empty_payload_with_defaults(self):
        '''Test extraction with empty payload and defaults enabled.'''
        result = _extract_watchlist_settings({}, include_defaults=True)
        
        # Should have all event types defaulting to True
        self.assertEqual(len(result), 6)
        for event_type in EventType:
            self.assertTrue(result[event_type])
    
    def test_extract_empty_payload_without_defaults(self):
        '''Test extraction with empty payload and defaults disabled.'''
        result = _extract_watchlist_settings({}, include_defaults=False)
        
        # Should be empty
        self.assertEqual(len(result), 0)


class TestWatchlistCollectionGet(unittest.TestCase):
    '''Test GET /watchlists/ endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlists_success(self, mock_get_user_id, mock_get_service):
        '''Test successful retrieval of watchlists.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_all_watchlists_for_user.return_value = [
            {
                'id': str(uuid4()),
                'name': 'Tech Stocks',
                'calendar_token': 'token1',
                'created_at': datetime.now(timezone.utc),
                'include_earnings_announcement': True,
            },
        ]
        mock_get_service.return_value = mock_service
        
        response = self.client.get('/watchlists/')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Tech Stocks')
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlists_empty(self, mock_get_user_id, mock_get_service):
        '''Test retrieval returns empty list when no watchlists.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_all_watchlists_for_user.return_value = []
        mock_get_service.return_value = mock_service
        
        response = self.client.get('/watchlists/')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)


class TestWatchlistCollectionPost(unittest.TestCase):
    '''Test POST /watchlists/ endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_create_watchlist_success(self, mock_get_user_id, mock_get_service):
        '''Test successful watchlist creation.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.create_watchlist.return_value = {
            'id': str(self.watchlist_id),
            'name': 'Tech Stocks',
            'calendar_token': 'token123',
            'created_at': datetime.now(timezone.utc),
            'include_earnings_announcement': True,
        }
        mock_get_service.return_value = mock_service
        
        payload = {
            'name': 'Tech Stocks',
            'include_earnings_announcement': True,
            'include_dividend_ex': False,
        }
        
        response = self.client.post('/watchlists/', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        data = response.get_json()
        self.assertEqual(data['name'], 'Tech Stocks')
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_create_watchlist_empty_name(self, mock_get_user_id, mock_get_service):
        '''Test creation fails with empty name.'''
        mock_get_user_id.return_value = self.user_id
        mock_get_service.return_value = Mock()
        
        payload = {
            'name': '   ',
            'include_earnings_announcement': True,
        }
        
        response = self.client.post('/watchlists/', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestWatchlistDetailGet(unittest.TestCase):
    '''Test GET /watchlists/<id> endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlist_success(self, mock_get_user_id, mock_get_service):
        '''Test successful retrieval of watchlist by ID.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_watchlist_by_id.return_value = {
            'id': str(self.watchlist_id),
            'name': 'Tech Stocks',
            'calendar_token': 'token123',
            'created_at': datetime.now(timezone.utc),
        }
        mock_get_service.return_value = mock_service
        
        response = self.client.get(f'/watchlists/{self.watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['name'], 'Tech Stocks')
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlist_not_found(self, mock_get_user_id, mock_get_service):
        '''Test retrieval fails when watchlist not found.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_watchlist_by_id.return_value = None
        mock_get_service.return_value = mock_service
        
        response = self.client.get(f'/watchlists/{self.watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestWatchlistDetailPut(unittest.TestCase):
    '''Test PUT /watchlists/<id> endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_update_watchlist_name_success(self, mock_get_user_id, mock_get_service):
        '''Test successful update of watchlist name.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.update_watchlist.return_value = True
        mock_service.get_watchlist_by_id.return_value = {
            'id': str(self.watchlist_id),
            'name': 'Updated Name',
            'calendar_token': 'token123',
            'created_at': datetime.now(timezone.utc),
        }
        mock_get_service.return_value = mock_service
        
        payload = {'name': 'Updated Name'}
        response = self.client.put(f'/watchlists/{self.watchlist_id}', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['name'], 'Updated Name')
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_update_watchlist_settings_success(self, mock_get_user_id, mock_get_service):
        '''Test successful update of watchlist settings.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.update_watchlist.return_value = True
        mock_service.get_watchlist_by_id.return_value = {
            'id': str(self.watchlist_id),
            'name': 'Tech Stocks',
            'calendar_token': 'token123',
            'created_at': datetime.now(timezone.utc),
            'include_earnings_announcement': False,
        }
        mock_get_service.return_value = mock_service
        
        payload = {'include_earnings_announcement': False}
        response = self.client.put(f'/watchlists/{self.watchlist_id}', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_update_watchlist_empty_name(self, mock_get_user_id, mock_get_service):
        '''Test update fails with empty name.'''
        mock_get_user_id.return_value = self.user_id
        mock_get_service.return_value = Mock()
        
        payload = {'name': '   '}
        response = self.client.put(f'/watchlists/{self.watchlist_id}', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_update_watchlist_no_fields(self, mock_get_user_id, mock_get_service):
        '''Test update fails when no fields provided.'''
        mock_get_user_id.return_value = self.user_id
        mock_get_service.return_value = Mock()
        
        payload = {}
        response = self.client.put(f'/watchlists/{self.watchlist_id}', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_update_watchlist_not_found(self, mock_get_user_id, mock_get_service):
        '''Test update fails when watchlist not found.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.update_watchlist.return_value = False
        mock_get_service.return_value = mock_service
        
        payload = {'name': 'Updated Name'}
        response = self.client.put(f'/watchlists/{self.watchlist_id}', json=payload)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestWatchlistDetailDelete(unittest.TestCase):
    '''Test DELETE /watchlists/<id> endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_delete_watchlist_success(self, mock_get_user_id, mock_get_service):
        '''Test successful watchlist deletion.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.delete_watchlist.return_value = True
        mock_get_service.return_value = mock_service
        
        response = self.client.delete(f'/watchlists/{self.watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_delete_watchlist_not_found(self, mock_get_user_id, mock_get_service):
        '''Test delete fails when watchlist not found.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.delete_watchlist.return_value = False
        mock_get_service.return_value = mock_service
        
        response = self.client.delete(f'/watchlists/{self.watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestWatchlistStocksCollectionGet(unittest.TestCase):
    '''Test GET /watchlists/<id>/stocks endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlist_stocks_success(self, mock_get_user_id, mock_get_service):
        '''Test successful retrieval of watchlist stocks.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_watchlist_stocks.return_value = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'followed_at': datetime.now(timezone.utc).isoformat(),
            },
        ]
        mock_get_service.return_value = mock_service
        
        response = self.client.get(f'/watchlists/{self.watchlist_id}/stocks')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['ticker'], 'AAPL')
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_get_watchlist_stocks_not_found(self, mock_get_user_id, mock_get_service):
        '''Test retrieval fails when watchlist not found.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.get_watchlist_stocks.side_effect = ValueError('Watchlist not found')
        mock_get_service.return_value = mock_service
        
        response = self.client.get(f'/watchlists/{self.watchlist_id}/stocks')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestWatchlistStockPost(unittest.TestCase):
    '''Test POST /watchlists/<id>/stocks/<ticker> endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_follow_stock_success(self, mock_get_user_id, mock_get_service):
        '''Test successfully following a stock.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.add_stock_to_watchlist.return_value = True
        mock_get_service.return_value = mock_service
        
        response = self.client.post(f'/watchlists/{self.watchlist_id}/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['stock_ticker'], 'AAPL')
        self.assertIn('message', data)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_follow_stock_empty_ticker(self, mock_get_user_id, mock_get_service):
        '''Test follow fails with empty ticker.'''
        mock_get_user_id.return_value = self.user_id
        mock_get_service.return_value = Mock()
        
        response = self.client.post(f'/watchlists/{self.watchlist_id}/stocks/   ')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_follow_stock_not_found(self, mock_get_user_id, mock_get_service):
        '''Test follow fails when stock not found.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.add_stock_to_watchlist.side_effect = LookupError('Stock not found')
        mock_get_service.return_value = mock_service
        
        response = self.client.post(f'/watchlists/{self.watchlist_id}/stocks/INVALID')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestWatchlistStockDelete(unittest.TestCase):
    '''Test DELETE /watchlists/<id>/stocks/<ticker> endpoint.'''
    
    def setUp(self):
        '''Set up test Flask app and client.'''
        self.app = Flask(__name__)
        self.app.config['API_TITLE'] = 'Test API'
        self.app.config['API_VERSION'] = 'v1'
        self.app.config['OPENAPI_VERSION'] = '3.0.2'
        self.app.config['TESTING'] = True
        
        self.api = Api(self.app)
        self.api.register_blueprint(watchlists_bp, url_prefix='/watchlists')
        
        self.client = self.app.test_client()
        self.user_id = uuid4()
        self.watchlist_id = uuid4()
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_unfollow_stock_success(self, mock_get_user_id, mock_get_service):
        '''Test successfully unfollowing a stock.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.remove_stock_to_watchlist.return_value = True
        mock_get_service.return_value = mock_service
        
        response = self.client.delete(f'/watchlists/{self.watchlist_id}/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertEqual(data['stock_ticker'], 'AAPL')
        self.assertIn('message', data)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_unfollow_stock_empty_ticker(self, mock_get_user_id, mock_get_service):
        '''Test unfollow fails with empty ticker.'''
        mock_get_user_id.return_value = self.user_id
        mock_get_service.return_value = Mock()
        
        response = self.client.delete(f'/watchlists/{self.watchlist_id}/stocks/   ')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.watchlists_rest.get_watchlist_service')
    @patch('src.api.routes.watchlists_rest.auth_utils.get_current_user_id')
    def test_unfollow_stock_not_found(self, mock_get_user_id, mock_get_service):
        '''Test unfollow fails when stock not in watchlist.'''
        mock_get_user_id.return_value = self.user_id
        
        mock_service = Mock()
        mock_service.remove_stock_to_watchlist.return_value = False
        mock_get_service.return_value = mock_service
        
        response = self.client.delete(f'/watchlists/{self.watchlist_id}/stocks/AAPL')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestGetWatchlistService(unittest.TestCase):
    '''Test get_watchlist_service singleton.'''
    
    @patch('src.api.routes.watchlists_rest.WatchlistService')
    def test_get_watchlist_service_creates_singleton(self, mock_service_class):
        '''Test service is created as singleton.'''
        # Reset the global variable
        import src.api.routes.watchlists_rest as rest_module
        rest_module.watchlist_service = None
        
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        service1 = get_watchlist_service()
        service2 = get_watchlist_service()
        
        # Should create only once
        mock_service_class.assert_called_once()
        self.assertIs(service1, service2)
        
        # Cleanup
        rest_module.watchlist_service = None


if __name__ == '__main__':
    unittest.main()
