# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.database.adapter_base import DatabaseAdapterBaseDefinition as DatabaseAdapter
from src.database.adapter_factory import (
    DatabaseAdapterFactory,
    DatabaseEnvironment
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
    
    def tearDown(self):
        """Reset factory after each test."""
        DatabaseAdapterFactory.reset()
    
    @patch.dict('os.environ', {
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_create_local_adapter(self):
        """Factory should create LocalDatabaseAdapter for local environment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter = DatabaseAdapterFactory.get_instance()
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        self.assertEqual(adapter.host, '127.0.0.1')
        self.assertEqual(adapter.database, 'ticker_calendar_local_dev_db')
        
        adapter.close()
    
    @patch.dict('os.environ', {
        'DB_ENVIRONMENT': 'local',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_initialize_development(self):
        """Factory should initialize for development environment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter = DatabaseAdapterFactory.get_instance()
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        
        adapter.close()
    
    def test_get_instance_without_initialize(self):
        """get_instance should raise RuntimeError if not initialized."""
        # Ensure factory is reset
        DatabaseAdapterFactory.reset()
        
        with self.assertRaises(RuntimeError):
            DatabaseAdapterFactory.get_instance()


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
        """get_instance should return singleton instance."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter1 = DatabaseAdapterFactory.get_instance()
        adapter2 = DatabaseAdapterFactory.get_instance()
        
        # Should be the same instance
        self.assertIs(adapter1, adapter2)
    



if __name__ == '__main__':
    unittest.main()
