# Disclaimer: Created by GitHub Copilot
'''
Unit tests for UserService.
'''

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta

from src.app.services.user_service import UserService
from src.models.user_model import User


class TestUserServiceInitialization(unittest.TestCase):
    '''Test UserService initialization.'''
    
    @patch('src.app.services.user_service.DatabaseAdapterFactory.get_instance')
    def test_init(self, mock_db_factory):
        '''Test service initializes with correct dependencies.'''
        mock_db = Mock()
        mock_db_factory.return_value = mock_db
        
        service = UserService()
        
        self.assertIsNotNone(service.db)
        mock_db_factory.assert_called_once()


class TestGetUser(unittest.TestCase):
    '''Test user retrieval.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.user_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            self.service = UserService()
        
        self.user_id = 12345
    
    def test_get_user_success_without_preferences(self):
        '''Test successful user retrieval without preferences.'''
        user_data = {
            'email': 'test@example.com',
            'created_at': datetime.now(timezone.utc),
        }
        
        self.mock_db.execute_query.return_value = [user_data]
        
        result = self.service.get_user(user_id=self.user_id)
        
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, 'test@example.com')
        self.assertIsNotNone(result.created_at)
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_user_not_found(self):
        '''Test user retrieval when user doesn't exist.'''
        self.mock_db.execute_query.return_value = []
        
        with self.assertRaises(Exception) as context:
            self.service.get_user(user_id=self.user_id)
        
        self.assertIn('Error fetching user', str(context.exception))
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_user_database_error(self):
        '''Test user retrieval when database error occurs.'''
        self.mock_db.execute_query.side_effect = Exception("Database connection error")
        
        with self.assertRaises(Exception) as context:
            self.service.get_user(user_id=self.user_id)
        
        self.assertIn('Error fetching user', str(context.exception))
        self.mock_db.execute_query.assert_called_once()


class TestUpdateUser(unittest.TestCase):
    '''Test user update operations.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.mock_db = Mock()
        
        with patch('src.app.services.user_service.DatabaseAdapterFactory.get_instance', return_value=self.mock_db):
            self.service = UserService()
        
        self.user_id = 12345
    
    def test_update_user_email_success(self):
        '''Test successful email update.'''
        self.mock_db.execute_update.return_value = 1
        
        result = self.service.update_user(
            user_id=self.user_id,
            email='newemail@example.com',
        )
        
        self.assertTrue(result)
        self.mock_db.execute_update.assert_called_once()
        
        # Verify the query contains the new email
        call_args = self.mock_db.execute_update.call_args
        self.assertEqual(call_args[1]['params']['email'], 'newemail@example.com')
        self.assertEqual(call_args[1]['params']['user_id'], self.user_id)
    
    def test_update_user_no_changes(self):
        '''Test update with no fields to change.'''
        result = self.service.update_user(user_id=self.user_id)
        
        self.assertFalse(result)
        self.mock_db.execute_update.assert_not_called()
    
    def test_update_user_invalid_user_id_type(self):
        '''Test update fails with invalid user_id type.'''
        with self.assertRaises(TypeError) as context:
            self.service.update_user(
                user_id='not-an-int',  # type: ignore
                email='test@example.com',
            )
        
        self.assertIn('must be an integer', str(context.exception))
        self.mock_db.execute_update.assert_not_called()
    
    def test_update_user_no_rows_affected(self):
        '''Test update when no rows are affected (user not found).'''
        self.mock_db.execute_update.return_value = 0
        
        result = self.service.update_user(
            user_id=self.user_id,
            email='newemail@example.com',
        )
        
        self.assertFalse(result)
        self.mock_db.execute_update.assert_called_once()
    
    def test_update_user_database_error(self):
        '''Test update when database error occurs.'''
        self.mock_db.execute_update.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception) as context:
            self.service.update_user(
                user_id=self.user_id,
                email='newemail@example.com',
            )
        
        self.assertIn('Error updating user', str(context.exception))
        self.mock_db.execute_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()
