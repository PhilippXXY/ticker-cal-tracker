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


if __name__ == '__main__':
    unittest.main()
