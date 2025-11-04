# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.database import (  # type: ignore
    DatabaseAdapter, # type: ignore
    DatabaseAdapterFactory, # type: ignore
    DatabaseEnvironment, # type: ignore
    get_database_adapter # type: ignore
)
from src.database.local_adapter import LocalDatabaseAdapter


class TestDatabaseAdapterInterface(unittest.TestCase):
    """Test that adapters implement the DatabaseAdapter interface correctly."""
    
    def test_local_adapter_implements_interface(self):
        """LocalDatabaseAdapter should implement all abstract methods."""
        adapter = LocalDatabaseAdapter(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        
        # Check that adapter is an instance of DatabaseAdapter
        self.assertIsInstance(adapter, DatabaseAdapter)
        
        # Check that all required methods exist
        self.assertTrue(hasattr(adapter, 'get_engine'))
        self.assertTrue(hasattr(adapter, 'get_session'))
        self.assertTrue(hasattr(adapter, 'execute_query'))
        self.assertTrue(hasattr(adapter, 'execute_update'))
        self.assertTrue(hasattr(adapter, 'health_check'))
        self.assertTrue(hasattr(adapter, 'close'))
        
        adapter.close()


class TestDatabaseAdapterFactory(unittest.TestCase):
    """Test the DatabaseAdapterFactory."""
    
    @patch.dict('os.environ', {
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_create_local_adapter(self):
        """Factory should create LocalDatabaseAdapter for local environment."""
        adapter = DatabaseAdapterFactory.create(DatabaseEnvironment.LOCAL)
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        self.assertEqual(adapter.host, 'localhost')
        self.assertEqual(adapter.database, 'test_db')
        
        adapter.close()
    
    @patch.dict('os.environ', {
        'DB_ENVIRONMENT': 'local',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_create_from_env_local(self):
        """Factory should create adapter from environment variables."""
        adapter = DatabaseAdapterFactory.create_from_env()
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        
        adapter.close()
    
    def test_create_test_adapter(self):
        """Factory should create test adapter."""
        adapter = DatabaseAdapterFactory.create(
            DatabaseEnvironment.TEST,
            database="test_database"
        )
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        self.assertEqual(adapter.database, 'test_database')
        
        adapter.close()


class TestLocalDatabaseAdapter(unittest.TestCase):
    """Test LocalDatabaseAdapter functionality."""
    
    def setUp(self):
        """Set up test adapter with mock database."""
        self.adapter = LocalDatabaseAdapter(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.adapter.close()
    
    def test_connection_string(self):
        """Adapter should create correct connection string."""
        expected = "postgresql://test_user:test_pass@localhost:5432/test_db"
        self.assertEqual(self.adapter.connection_string, expected)
    
    def test_get_engine(self):
        """Adapter should return SQLAlchemy engine."""
        engine = self.adapter.get_engine()
        self.assertIsNotNone(engine)
    
    @patch.dict('os.environ', {
        'DB_HOST': 'custom_host',
        'DB_PORT': '3306',
        'DB_NAME': 'custom_db',
        'DB_USER': 'custom_user',
        'DB_PASSWORD': 'custom_pass',
        'DB_POOL_SIZE': '10',
        'DB_MAX_OVERFLOW': '20'
    })
    def test_from_env(self):
        """Adapter should be created from environment variables."""
        adapter = LocalDatabaseAdapter.from_env()  # type: ignore
        
        self.assertEqual(adapter.host, 'custom_host')
        self.assertEqual(adapter.port, 3306)
        self.assertEqual(adapter.database, 'custom_db')
        self.assertEqual(adapter.user, 'custom_user')
        self.assertEqual(adapter.password, 'custom_pass')
        
        adapter.close()


class TestDatabaseAdapterUsage(unittest.TestCase):
    """Test common usage patterns."""
    
    @patch.dict('os.environ', {
        'DB_ENVIRONMENT': 'local',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_singleton_pattern(self):
        """get_database_adapter should return singleton instance."""
        adapter1 = get_database_adapter()
        adapter2 = get_database_adapter()
        
        # Should be the same instance
        self.assertIs(adapter1, adapter2)
    
    def test_context_manager(self):
        """Adapter should work as context manager."""
        with LocalDatabaseAdapter(  # type: ignore
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        ) as adapter:
            self.assertIsInstance(adapter, DatabaseAdapter)
        
        # After exiting context, adapter should be closed
        # (engine will be disposed)


if __name__ == '__main__':
    unittest.main()
