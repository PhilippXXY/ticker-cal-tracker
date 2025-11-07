# Disclaimer: Created by GitHub Copilot
'''
Unit tests for calendar REST endpoints.
'''

import unittest
from unittest.mock import Mock, patch, MagicMock
from http import HTTPStatus
from flask import Flask

from src.api.routes.calendar_rest import calendar_bp, get_calendar_service


class TestCalendarRest(unittest.TestCase):
    '''Test calendar REST endpoints.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Create a Flask app for testing
        self.app = Flask(__name__)
        self.app.register_blueprint(calendar_bp, url_prefix='/calendar')
        self.client = self.app.test_client()
        self.test_token = 'test_secure_token_abc123'
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_success(self, mock_get_service):
        '''Test successful calendar retrieval.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        ics_content = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n'
        mock_service.get_calendar.return_value = ics_content
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Verify service was called
        mock_service.get_calendar.assert_called_once_with(token=self.test_token)
        
        # Verify response
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.mimetype, 'text/calendar')
        self.assertEqual(response.get_data(as_text=True), ics_content)
        
        # Verify headers
        self.assertIn('Content-Disposition', response.headers)
        self.assertIn(self.test_token, response.headers['Content-Disposition'])
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_empty_token(self, mock_get_service):
        '''Test retrieval with empty token (URL would be invalid anyway).'''
        # Flask won't match the route with empty token, so this tests the route pattern
        response = self.client.get('/calendar/.ics')
        
        # Should return 404 as route won't match
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_value_error(self, mock_get_service):
        '''Test handling of ValueError from service.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.side_effect = ValueError('Invalid token format')
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Should return BAD_REQUEST
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_lookup_error(self, mock_get_service):
        '''Test handling of LookupError from service.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.side_effect = LookupError('Watchlist not found')
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Should return NOT_FOUND
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_generic_error(self, mock_get_service):
        '''Test handling of generic exceptions from service.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.side_effect = Exception('Database error')
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Should return INTERNAL_SERVER_ERROR
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_empty_content(self, mock_get_service):
        '''Test handling of empty calendar content.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.return_value = ''
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Should return NOT_FOUND for empty content
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_trims_token(self, mock_get_service):
        '''Test that token is trimmed before processing.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.return_value = 'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'
        
        # Token with spaces in URL (URL encoded)
        response = self.client.get('/calendar/%20%20token_with_spaces%20%20.ics')
        
        # Verify service was called with trimmed token
        mock_service.get_calendar.assert_called_once_with(token='token_with_spaces')
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_response_headers(self, mock_get_service):
        '''Test that response has correct headers for calendar subscription.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.return_value = 'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'
        
        response = self.client.get(f'/calendar/{self.test_token}.ics')
        
        # Verify cache control headers
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')
        self.assertEqual(response.headers['Pragma'], 'no-cache')
        self.assertEqual(response.headers['Expires'], '0')
        
        # Verify content disposition
        self.assertIn('attachment', response.headers['Content-Disposition'])
        self.assertIn('.ics', response.headers['Content-Disposition'])
    
    @patch('src.api.routes.calendar_rest.CalendarService')
    def test_get_calendar_service_singleton(self, mock_calendar_service_class):
        '''Test that calendar service is a singleton.'''
        # Reset the global service
        import src.api.routes.calendar_rest as calendar_rest_module
        calendar_rest_module.calendar_service = None
        
        mock_service_instance = Mock()
        mock_calendar_service_class.return_value = mock_service_instance
        
        # Call get_calendar_service multiple times
        service1 = get_calendar_service()
        service2 = get_calendar_service()
        
        # Should return the same instance
        self.assertIs(service1, service2)
        
        # Should only instantiate once
        mock_calendar_service_class.assert_called_once()
    
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_calendar_whitespace_only_token(self, mock_get_service):
        '''Test retrieval with whitespace-only token.'''
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar.return_value = 'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'
        
        # URL with spaces (will be trimmed)
        response = self.client.get('/calendar/%20%20%20.ics')
        
        # Should be rejected as empty after trimming
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestCalendarWatchlistRotateToken(unittest.TestCase):
    '''Test calendar token rotation endpoint.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Create a Flask app for testing
        self.app = Flask(__name__)
        self.app.register_blueprint(calendar_bp, url_prefix='/calendar')
        self.client = self.app.test_client()
        self.test_watchlist_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
        self.test_user_id = '1234abcd-5678-1234-9012-abcdef123456'
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_rotate_token_success(self, mock_get_service, mock_get_user_id):
        '''Test successful token rotation.'''
        from uuid import UUID
        
        mock_user_id = UUID(self.test_user_id)
        mock_get_user_id.return_value = mock_user_id
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        new_token = 'new_secure_token_xyz789'
        mock_service.rotate_calendar_token.return_value = new_token
        
        with self.app.test_request_context():
            response = self.client.post(f'/calendar/{self.test_watchlist_id}')
        
        # Verify service was called correctly
        mock_service.rotate_calendar_token.assert_called_once()
        call_kwargs = mock_service.rotate_calendar_token.call_args.kwargs
        self.assertEqual(call_kwargs['user_id'], mock_user_id)
        self.assertEqual(str(call_kwargs['watchlist_id']), self.test_watchlist_id)
        
        # Verify response
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertIn('calendar_url', data)
        self.assertIn('token', data)
        self.assertEqual(data['token'], new_token)
        self.assertIn(new_token, data['calendar_url'])
        self.assertIn('.ics', data['calendar_url'])
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_rotate_token_constructs_url(self, mock_get_service, mock_get_user_id):
        '''Test that full calendar URL is constructed correctly.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        new_token = 'test_token_123'
        mock_service.rotate_calendar_token.return_value = new_token
        
        with self.app.test_request_context():
            response = self.client.post(f'/calendar/{self.test_watchlist_id}')
        
        data = response.get_json()
        self.assertIn('/api/cal/', data['calendar_url'])
        self.assertTrue(data['calendar_url'].endswith(f'{new_token}.ics'))
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_rotate_token_value_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of ValueError from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.rotate_calendar_token.side_effect = ValueError('Invalid watchlist ID')
        
        response = self.client.post(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_rotate_token_lookup_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of LookupError from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.rotate_calendar_token.side_effect = LookupError('Watchlist not found')
        
        response = self.client.post(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_rotate_token_generic_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of generic exceptions from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.rotate_calendar_token.side_effect = Exception('Database error')
        
        response = self.client.post(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def test_rotate_token_invalid_uuid(self):
        '''Test with invalid UUID format.'''
        response = self.client.post('/calendar/not-a-valid-uuid')
        
        # Should return 404 as route won't match
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestCalendarWatchlistGetToken(unittest.TestCase):
    '''Test calendar token retrieval endpoint.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Create a Flask app for testing
        self.app = Flask(__name__)
        self.app.register_blueprint(calendar_bp, url_prefix='/calendar')
        self.client = self.app.test_client()
        self.test_watchlist_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
        self.test_user_id = '1234abcd-5678-1234-9012-abcdef123456'
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_success(self, mock_get_service, mock_get_user_id):
        '''Test successful token retrieval.'''
        from uuid import UUID
        
        mock_user_id = UUID(self.test_user_id)
        mock_get_user_id.return_value = mock_user_id
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        existing_token = 'existing_token_abc123'
        mock_service.get_calendar_token.return_value = existing_token
        
        with self.app.test_request_context():
            response = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        # Verify service was called correctly
        mock_service.get_calendar_token.assert_called_once()
        call_kwargs = mock_service.get_calendar_token.call_args.kwargs
        self.assertEqual(call_kwargs['user_id'], mock_user_id)
        self.assertEqual(str(call_kwargs['watchlist_id']), self.test_watchlist_id)
        
        # Verify response
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.get_json()
        self.assertIn('calendar_url', data)
        self.assertIn('token', data)
        self.assertEqual(data['token'], existing_token)
        self.assertIn(existing_token, data['calendar_url'])
        self.assertIn('.ics', data['calendar_url'])
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_constructs_url(self, mock_get_service, mock_get_user_id):
        '''Test that full calendar URL is constructed correctly.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        token = 'my_calendar_token'
        mock_service.get_calendar_token.return_value = token
        
        with self.app.test_request_context():
            response = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        data = response.get_json()
        self.assertIn('/api/cal/', data['calendar_url'])
        self.assertTrue(data['calendar_url'].endswith(f'{token}.ics'))
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_value_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of ValueError from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar_token.side_effect = ValueError('Invalid watchlist ID')
        
        response = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_lookup_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of LookupError from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar_token.side_effect = LookupError('Watchlist not found')
        
        response = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_generic_error(self, mock_get_service, mock_get_user_id):
        '''Test handling of generic exceptions from service.'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.get_calendar_token.side_effect = Exception('Database error')
        
        response = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def test_get_token_invalid_uuid(self):
        '''Test with invalid UUID format.'''
        response = self.client.get('/calendar/not-a-valid-uuid')
        
        # Should return 404 as route won't match
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    @patch('src.api.routes.calendar_rest.auth_utils.get_current_user_id')
    @patch('src.api.routes.calendar_rest.get_calendar_service')
    def test_get_token_returns_same_token_on_multiple_calls(self, mock_get_service, mock_get_user_id):
        '''Test that GET returns the same token on multiple calls (idempotent).'''
        from uuid import UUID
        
        mock_get_user_id.return_value = UUID(self.test_user_id)
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        token = 'stable_token_xyz'
        mock_service.get_calendar_token.return_value = token
        
        with self.app.test_request_context():
            response1 = self.client.get(f'/calendar/{self.test_watchlist_id}')
            response2 = self.client.get(f'/calendar/{self.test_watchlist_id}')
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        self.assertEqual(data1['token'], data2['token'])
        self.assertEqual(data1['calendar_url'], data2['calendar_url'])


if __name__ == '__main__':
    unittest.main()
