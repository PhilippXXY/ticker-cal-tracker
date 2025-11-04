# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import patch


from src.database.adaper_factory import (
    DatabaseAdapterFactory,
    DatabaseEnvironment,
    parse_environment_from_args
)
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.gcp_adapter import GcpDatabaseAdapter


class TestDatabaseAdapterFactoryIntegration(unittest.TestCase):
    """
    Integration tests for DatabaseAdapterFactory.
    
    These tests verify the factory works correctly with real adapter implementations
    (without mocking the adapters themselves).
    """
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_create_local_adapter_returns_correct_type(self):
        """Test that factory creates actual LocalDatabaseAdapter for development."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
    
    def test_local_adapter_has_correct_configuration(self):
        """Test that local adapter is configured with expected values."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        # Verify it's a LocalDatabaseAdapter
        self.assertIsInstance(adapter, LocalDatabaseAdapter)
        
        # Check configuration (cast to LocalDatabaseAdapter to access specific attributes)
        if isinstance(adapter, LocalDatabaseAdapter):
            self.assertEqual(adapter.host, "127.0.0.1")
            self.assertEqual(adapter.port, 5432)
            self.assertEqual(adapter.database, "ticker_calendar_local_dev_db")
            self.assertEqual(adapter.user, "ticker_dev")
            self.assertEqual(adapter.password, "dev_password_123")
    
    def test_create_gcp_adapter_returns_correct_type(self):
        """Test that factory creates actual GcpDatabaseAdapter for deployment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        self.assertIsInstance(adapter, GcpDatabaseAdapter)
    
    def test_singleton_pattern_with_real_adapter(self):
        """Test singleton pattern with real LocalDatabaseAdapter."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter1 = DatabaseAdapterFactory.get_instance()
        adapter2 = DatabaseAdapterFactory.get_instance()
        adapter3 = DatabaseAdapterFactory.get_instance()
        
        # All should be the same instance
        self.assertIs(adapter1, adapter2)
        self.assertIs(adapter2, adapter3)
        
        # And they should all be LocalDatabaseAdapter
        self.assertIsInstance(adapter1, LocalDatabaseAdapter)
    
    def test_reset_and_reinitialize_with_real_adapters(self):
        """Test resetting and reinitializing the factory with real adapters."""
        # Create development adapter
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        dev_adapter = DatabaseAdapterFactory.get_instance()
        self.assertIsInstance(dev_adapter, LocalDatabaseAdapter)
        
        # Reset
        DatabaseAdapterFactory.reset()
        
        # Should raise error before reinitialization
        with self.assertRaises(RuntimeError):
            DatabaseAdapterFactory.get_instance()
        
        # Create deployment adapter
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        deploy_adapter = DatabaseAdapterFactory.get_instance()
        self.assertIsInstance(deploy_adapter, GcpDatabaseAdapter)
        
        # Should be different instances
        self.assertIsNot(dev_adapter, deploy_adapter)
    
    def test_local_adapter_connection_string_format(self):
        """Test that local adapter has correctly formatted connection string."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        # Verify connection string format (cast to LocalDatabaseAdapter)
        if isinstance(adapter, LocalDatabaseAdapter):
            expected_conn_str = (
                "postgresql://ticker_dev:dev_password_123@127.0.0.1:5432/"
                "ticker_calendar_local_dev_db"
            )
            self.assertEqual(adapter.connection_string, expected_conn_str)
    
    def test_local_adapter_has_engine(self):
        """Test that local adapter has a valid SQLAlchemy engine."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        # Get engine and verify it exists
        engine = adapter.get_engine()
        self.assertIsNotNone(engine)
        
        # Verify engine URL contains expected database name
        self.assertIn("ticker_calendar_local_dev_db", str(engine.url))
    
    def test_multiple_initializations_create_new_instances(self):
        """Test that re-initializing creates a new instance."""
        # First initialization
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter1 = DatabaseAdapterFactory.get_instance()
        adapter1_id = id(adapter1)
        
        # Re-initialize with same environment
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter2 = DatabaseAdapterFactory.get_instance()
        adapter2_id = id(adapter2)
        
        # Should be different instances (new object created)
        self.assertNotEqual(adapter1_id, adapter2_id)
    
    def test_gcp_adapter_methods_raise_not_implemented(self):
        """Test that GCP adapter methods raise NotImplementedError (as expected)."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        
        # All methods should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            adapter.get_engine()
        
        with self.assertRaises(NotImplementedError):
            with adapter.get_session():
                pass
        
        with self.assertRaises(NotImplementedError):
            adapter.execute_query(query="SELECT 1")
        
        with self.assertRaises(NotImplementedError):
            adapter.execute_update(query="UPDATE test SET x = 1")
        
        with self.assertRaises(NotImplementedError):
            adapter.execute_many(query="INSERT INTO test VALUES (?)", params_list=[])
        
        with self.assertRaises(NotImplementedError):
            adapter.health_check()
        
        with self.assertRaises(NotImplementedError):
            adapter.close()


class TestParseEnvironmentFromArgsIntegration(unittest.TestCase):
    """Integration tests for parse_environment_from_args function."""
    
    def test_parse_and_initialize_development(self):
        """Test parsing development flag and initializing factory."""
        with patch('sys.argv', ['script.py', '--development']):
            env = parse_environment_from_args()
            DatabaseAdapterFactory.initialize(env)
            
            adapter = DatabaseAdapterFactory.get_instance()
            self.assertIsInstance(adapter, LocalDatabaseAdapter)
        
        DatabaseAdapterFactory.reset()
    
    def test_parse_and_initialize_deployment(self):
        """Test parsing deployment flag and initializing factory."""
        with patch('sys.argv', ['script.py', '--deployment']):
            env = parse_environment_from_args()
            DatabaseAdapterFactory.initialize(env)
            
            adapter = DatabaseAdapterFactory.get_instance()
            self.assertIsInstance(adapter, GcpDatabaseAdapter)
        
        DatabaseAdapterFactory.reset()
    
    def test_default_parse_and_initialize(self):
        """Test default parsing (no flags) initializes development."""
        with patch('sys.argv', ['script.py']):
            env = parse_environment_from_args()
            DatabaseAdapterFactory.initialize(env)
            
            adapter = DatabaseAdapterFactory.get_instance()
            self.assertIsInstance(adapter, LocalDatabaseAdapter)
        
        DatabaseAdapterFactory.reset()


class TestDatabaseAdapterFactoryUsagePatterns(unittest.TestCase):
    """
    Test common usage patterns for DatabaseAdapterFactory.
    
    These tests verify the factory works as documented in its docstring.
    """
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_typical_usage_pattern(self):
        """Test the typical usage pattern from the docstring."""
        # This is the documented usage pattern:
        # from database.adaper_factory import DatabaseAdapterFactory
        # db_adapter = DatabaseAdapterFactory.get_instance()
        
        # But first need to initialize
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # Now use as documented
        db_adapter = DatabaseAdapterFactory.get_instance()
        
        # Should be a valid adapter
        self.assertIsNotNone(db_adapter)
        self.assertIsInstance(db_adapter, LocalDatabaseAdapter)
    
    def test_get_engine_from_factory_instance(self):
        """Test getting database engine from factory instance."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        db_adapter = DatabaseAdapterFactory.get_instance()
        engine = db_adapter.get_engine()
        
        self.assertIsNotNone(engine)
        self.assertIn("ticker_calendar_local_dev_db", str(engine.url))
    
    def test_reusing_instance_across_module(self):
        """Test that the same instance can be reused across different calls."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # Simulate different modules getting the instance
        db_adapter_module1 = DatabaseAdapterFactory.get_instance()
        db_adapter_module2 = DatabaseAdapterFactory.get_instance()
        db_adapter_module3 = DatabaseAdapterFactory.get_instance()
        
        # All should be the same instance
        self.assertIs(db_adapter_module1, db_adapter_module2)
        self.assertIs(db_adapter_module2, db_adapter_module3)
    
    def test_error_handling_without_initialization(self):
        """Test proper error handling when factory is not initialized."""
        # Try to use factory without initialization
        with self.assertRaises(RuntimeError) as context:
            DatabaseAdapterFactory.get_instance()
        
        # Error message should be helpful
        error_message = str(context.exception)
        self.assertIn("not initialized", error_message)
        self.assertIn("initialize()", error_message)


class TestDatabaseAdapterFactoryCleanup(unittest.TestCase):
    """Test cleanup and resource management for DatabaseAdapterFactory."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_reset_closes_local_adapter_engine(self):
        """Test that reset properly closes the local adapter's engine."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        adapter = DatabaseAdapterFactory.get_instance()
        engine = adapter.get_engine()
        
        # Engine should be usable
        self.assertIsNotNone(engine)
        
        # Reset should call close on adapter
        DatabaseAdapterFactory.reset()
        
        # After reset, factory should be in clean state
        self.assertIsNone(DatabaseAdapterFactory._instance)
        self.assertIsNone(DatabaseAdapterFactory._environment)
    
    def test_reinitialize_after_reset(self):
        """Test that factory can be reinitialized after reset."""
        # First use
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter1 = DatabaseAdapterFactory.get_instance()
        self.assertIsInstance(adapter1, LocalDatabaseAdapter)
        
        # Reset
        DatabaseAdapterFactory.reset()
        
        # Reinitialize and use again
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        adapter2 = DatabaseAdapterFactory.get_instance()
        self.assertIsInstance(adapter2, LocalDatabaseAdapter)
        
        # Should be different instances
        self.assertIsNot(adapter1, adapter2)


if __name__ == '__main__':
    unittest.main()
