# Disclaimer: Created by GitHub Copilot
'''
Integration tests for UserService with real database.
IMPORTANT: These tests will modify data in the database.
'''

import unittest
import os
from uuid import uuid4
from datetime import datetime, timezone

from src.app.services.user_service import UserService
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.adapter_factory import DatabaseAdapterFactory, DatabaseEnvironment


# Skip integration tests if flag is set
SKIP_DB_INTEGRATION = os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1'


@unittest.skipIf(SKIP_DB_INTEGRATION, "Skipping database integration tests")
class TestUserServiceIntegration(unittest.TestCase):
    '''Integration tests for UserService with real database.'''
    
    @classmethod
    def setUpClass(cls):
        '''Set up database connection for all tests.'''
        cls.adapter = LocalDatabaseAdapter(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'ticker_calendar_local_dev_db'),
            user=os.getenv('DB_USER', 'ticker_dev'),
            password=os.getenv('DB_PASSWORD', 'dev_password_123')
        )
        
        # Verify database is accessible
        if not cls.adapter.health_check():
            raise unittest.SkipTest(
                "Database is not accessible. Run 'python database/local/manage_db.py setup' first."
            )
        
        # Initialize the DatabaseAdapterFactory for integration tests
        DatabaseAdapterFactory.initialize(environment=DatabaseEnvironment.DEVELOPMENT)
        
        cls.service = UserService()
    
    @classmethod
    def tearDownClass(cls):
        '''Clean up database connection.'''
        cls.adapter.close()
    
    def setUp(self):
        '''Set up test data before each test.'''
        self.test_user_id = uuid4()
        self.test_users = []
        
        # Create a test user in the database
        self._create_test_user()
    
    def tearDown(self):
        '''Clean up test data after each test.'''
        # Clean up all test users
        for user_id in [self.test_user_id] + self.test_users:
            try:
                query = "DELETE FROM users WHERE id = :user_id"
                self.adapter.execute_update(query=query, params={'user_id': user_id})
            except Exception:
                pass
    
    def _create_test_user(self, user_id=None, email=None):
        '''Helper to create a test user in the database.'''
        if user_id is None:
            user_id = self.test_user_id
        if email is None:
            email = f'test_{user_id.hex[:8]}@example.com'
        
        query = """
            INSERT INTO users (id, email, password)
            VALUES (:user_id, :email, :password)
            ON CONFLICT (id) DO NOTHING
        """
        self.adapter.execute_update(
            query=query,
            params={
                'user_id': user_id,
                'email': email,
                'password': 'test_hash_not_real'
            }
        )
        return user_id
    
    def test_get_user_success(self):
        '''Test retrieving an existing user.'''
        user = self.service.get_user(user_id=self.test_user_id)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, f'test_{self.test_user_id.hex[:8]}@example.com')
        self.assertIsNotNone(user.created_at)
    
    def test_get_user_not_found(self):
        '''Test retrieving a non-existent user.'''
        non_existent_id = uuid4()
        
        with self.assertRaises(Exception) as context:
            self.service.get_user(user_id=non_existent_id)
        
        self.assertIn('Error fetching user', str(context.exception))
    
    def test_update_user_email_success(self):
        '''Test successfully updating user email.'''
        new_email = f'updated_{self.test_user_id.hex[:8]}@example.com'
        
        result = self.service.update_user(
            user_id=self.test_user_id,
            email=new_email,
        )
        
        self.assertTrue(result)
        
        # Verify the update
        user = self.service.get_user(user_id=self.test_user_id)
        self.assertEqual(user.email, new_email)
    
    def test_update_user_no_fields(self):
        '''Test update with no fields returns False.'''
        result = self.service.update_user(user_id=self.test_user_id)
        
        self.assertFalse(result)
    
    def test_update_user_not_found(self):
        '''Test updating a non-existent user.'''
        non_existent_id = uuid4()
        
        result = self.service.update_user(
            user_id=non_existent_id,
            email='nonexistent@example.com',
        )
        
        self.assertFalse(result)
    
    def test_update_user_invalid_user_id_type(self):
        '''Test update with invalid user_id type.'''
        with self.assertRaises(TypeError) as context:
            self.service.update_user(
                user_id='not-a-uuid',  # type: ignore
                email='test@example.com',
            )
        
        self.assertIn('must be a UUID', str(context.exception))
    
    def test_get_and_update_user_workflow(self):
        '''Test complete workflow of getting and updating a user.'''
        # Get initial user
        user = self.service.get_user(user_id=self.test_user_id)
        original_email = user.email
        
        # Update email
        new_email = f'workflow_{self.test_user_id.hex[:8]}@example.com'
        update_result = self.service.update_user(
            user_id=self.test_user_id,
            email=new_email,
        )
        self.assertTrue(update_result)
        
        # Get updated user
        updated_user = self.service.get_user(user_id=self.test_user_id)
        self.assertEqual(updated_user.email, new_email)
        self.assertNotEqual(updated_user.email, original_email)
        
        # Verify created_at hasn't changed
        self.assertEqual(user.created_at, updated_user.created_at)


if __name__ == '__main__':
    unittest.main()
