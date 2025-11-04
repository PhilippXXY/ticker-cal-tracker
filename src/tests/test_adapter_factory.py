# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.adaper_factory import (
    DatabaseAdapterFactory,
    DatabaseEnvironment,
    parse_environment_from_args
)
from database.adapter_base import DatabaseAdapterBaseDefinition
from database.local_adapter import LocalDatabaseAdapter
from database.gcp_adapter import GcpDatabaseAdapter


class TestDatabaseEnvironmentEnum(unittest.TestCase):
    """Test DatabaseEnvironment enum."""
    
    def test_development_environment_value(self):
        """Test DEVELOPMENT enum value."""
        self.assertEqual(DatabaseEnvironment.DEVELOPMENT.value, "development")
    
    def test_deployment_environment_value(self):
        """Test DEPLOYMENT enum value."""
        self.assertEqual(DatabaseEnvironment.DEPLOYMENT.value, "deployment")
    
    def test_enum_membership(self):
        """Test enum membership."""
        self.assertIn(DatabaseEnvironment.DEVELOPMENT, DatabaseEnvironment)
        self.assertIn(DatabaseEnvironment.DEPLOYMENT, DatabaseEnvironment)


class TestDatabaseAdapterFactoryInitialization(unittest.TestCase):
    """Test DatabaseAdapterFactory initialization."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_initialize_development_environment(self):
        """Test initialization with development environment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        self.assertEqual(
            DatabaseAdapterFactory._environment,
            DatabaseEnvironment.DEVELOPMENT
        )
        self.assertIsNone(DatabaseAdapterFactory._instance)
    
    def test_initialize_deployment_environment(self):
        """Test initialization with deployment environment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        
        self.assertEqual(
            DatabaseAdapterFactory._environment,
            DatabaseEnvironment.DEPLOYMENT
        )
        self.assertIsNone(DatabaseAdapterFactory._instance)
    
    def test_initialize_resets_existing_instance(self):
        """Test that initialization resets existing instance."""
        # First initialization
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # Get an instance
        with patch.object(DatabaseAdapterFactory, '_create_adapter') as mock_create:
            mock_adapter = Mock(spec=DatabaseAdapterBaseDefinition)
            mock_create.return_value = mock_adapter
            instance1 = DatabaseAdapterFactory.get_instance()
        
        self.assertIsNotNone(DatabaseAdapterFactory._instance)
        
        # Re-initialize with different environment
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        
        # Instance should be reset
        self.assertIsNone(DatabaseAdapterFactory._instance)
        self.assertEqual(
            DatabaseAdapterFactory._environment,
            DatabaseEnvironment.DEPLOYMENT
        )


class TestDatabaseAdapterFactoryGetInstance(unittest.TestCase):
    """Test DatabaseAdapterFactory.get_instance() method."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_get_instance_without_initialization_raises_error(self):
        """Test that get_instance raises RuntimeError if not initialized."""
        with self.assertRaises(RuntimeError) as context:
            DatabaseAdapterFactory.get_instance()
        
        self.assertIn("not initialized", str(context.exception))
        self.assertIn("initialize()", str(context.exception))
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_get_instance_creates_adapter_first_time(self, mock_local_adapter):
        """Test that get_instance creates adapter on first call."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_local_adapter.return_value = mock_adapter
        
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # First call should create adapter
        instance = DatabaseAdapterFactory.get_instance()
        
        self.assertIsNotNone(instance)
        self.assertEqual(DatabaseAdapterFactory._instance, mock_adapter)
        mock_local_adapter.assert_called_once()
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_get_instance_returns_singleton(self, mock_local_adapter):
        """Test that get_instance returns the same instance (singleton pattern)."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_local_adapter.return_value = mock_adapter
        
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # Get instance multiple times
        instance1 = DatabaseAdapterFactory.get_instance()
        instance2 = DatabaseAdapterFactory.get_instance()
        instance3 = DatabaseAdapterFactory.get_instance()
        
        # Should be the same instance
        self.assertIs(instance1, instance2)
        self.assertIs(instance2, instance3)
        
        # Adapter should only be created once
        mock_local_adapter.assert_called_once()


class TestDatabaseAdapterFactoryCreateAdapter(unittest.TestCase):
    """Test DatabaseAdapterFactory._create_adapter() method."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_create_adapter_development_environment(self, mock_local_adapter):
        """Test creating adapter for development environment."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_local_adapter.return_value = mock_adapter
        
        adapter = DatabaseAdapterFactory._create_adapter(
            DatabaseEnvironment.DEVELOPMENT
        )
        
        self.assertEqual(adapter, mock_adapter)
        mock_local_adapter.assert_called_once()
    
    @patch('database.adaper_factory.GcpDatabaseAdapter')
    def test_create_adapter_deployment_environment(self, mock_gcp_adapter):
        """Test creating adapter for deployment environment."""
        mock_adapter = Mock(spec=GcpDatabaseAdapter)
        mock_gcp_adapter.return_value = mock_adapter
        
        adapter = DatabaseAdapterFactory._create_adapter(
            DatabaseEnvironment.DEPLOYMENT
        )
        
        self.assertEqual(adapter, mock_adapter)
        mock_gcp_adapter.assert_called_once()
    
    def test_create_adapter_unknown_environment_raises_error(self):
        """Test that unknown environment raises ValueError."""
        # Create a mock enum value that's not DEVELOPMENT or DEPLOYMENT
        unknown_env = Mock()
        unknown_env.value = "unknown"
        
        with self.assertRaises(ValueError) as context:
            DatabaseAdapterFactory._create_adapter(unknown_env)
        
        self.assertIn("Unknown environment", str(context.exception))


class TestDatabaseAdapterFactoryCreateLocalAdapter(unittest.TestCase):
    """Test DatabaseAdapterFactory._create_local_adapter() method."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_create_local_adapter_with_correct_parameters(self, mock_local_adapter):
        """Test that local adapter is created with correct parameters."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_local_adapter.return_value = mock_adapter
        
        adapter = DatabaseAdapterFactory._create_local_adapter()
        
        # Verify LocalDatabaseAdapter was called with correct parameters
        mock_local_adapter.assert_called_once_with(
            host="127.0.0.1",
            port=5432,
            database="ticker_calendar_local_dev_db",
            user="ticker_dev",
            password="dev_password_123",
            pool_size=5,
            max_overflow=10,
            echo=False
        )
        self.assertEqual(adapter, mock_adapter)


class TestDatabaseAdapterFactoryCreateGcpAdapter(unittest.TestCase):
    """Test DatabaseAdapterFactory._create_gcp_adapter() method."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    @patch('database.adaper_factory.GcpDatabaseAdapter')
    def test_create_gcp_adapter(self, mock_gcp_adapter):
        """Test that GCP adapter is created."""
        mock_adapter = Mock(spec=GcpDatabaseAdapter)
        mock_gcp_adapter.return_value = mock_adapter
        
        adapter = DatabaseAdapterFactory._create_gcp_adapter()
        
        # Verify GcpDatabaseAdapter was called
        mock_gcp_adapter.assert_called_once_with()
        self.assertEqual(adapter, mock_adapter)


class TestDatabaseAdapterFactoryReset(unittest.TestCase):
    """Test DatabaseAdapterFactory.reset() method."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    def test_reset_clears_instance_and_environment(self):
        """Test that reset clears instance and environment."""
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        DatabaseAdapterFactory._environment = DatabaseEnvironment.DEVELOPMENT
        DatabaseAdapterFactory._instance = Mock(spec=DatabaseAdapterBaseDefinition)
        
        DatabaseAdapterFactory.reset()
        
        self.assertIsNone(DatabaseAdapterFactory._instance)
        self.assertIsNone(DatabaseAdapterFactory._environment)
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_reset_closes_existing_adapter(self, mock_local_adapter):
        """Test that reset calls close() on existing adapter."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_adapter.close = Mock()
        mock_local_adapter.return_value = mock_adapter
        
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        DatabaseAdapterFactory.get_instance()
        
        # Reset should close the adapter
        DatabaseAdapterFactory.reset()
        
        mock_adapter.close.assert_called_once()
        self.assertIsNone(DatabaseAdapterFactory._instance)
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_reset_handles_close_exception_gracefully(self, mock_local_adapter):
        """Test that reset handles exceptions from close() gracefully."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_adapter.close = Mock(side_effect=Exception("Close failed"))
        mock_local_adapter.return_value = mock_adapter
        
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        DatabaseAdapterFactory.get_instance()
        
        # Reset should handle exception and still clear instance
        DatabaseAdapterFactory.reset()
        
        self.assertIsNone(DatabaseAdapterFactory._instance)
        self.assertIsNone(DatabaseAdapterFactory._environment)


class TestParseEnvironmentFromArgs(unittest.TestCase):
    """Test parse_environment_from_args() function."""
    
    def test_parse_deployment_flag(self):
        """Test parsing --deployment flag."""
        with patch('sys.argv', ['script.py', '--deployment']):
            env = parse_environment_from_args()
            self.assertEqual(env, DatabaseEnvironment.DEPLOYMENT)
    
    def test_parse_development_flag(self):
        """Test parsing --development flag."""
        with patch('sys.argv', ['script.py', '--development']):
            env = parse_environment_from_args()
            self.assertEqual(env, DatabaseEnvironment.DEVELOPMENT)
    
    def test_parse_no_flags_defaults_to_development(self):
        """Test that no flags defaults to development."""
        with patch('sys.argv', ['script.py']):
            env = parse_environment_from_args()
            self.assertEqual(env, DatabaseEnvironment.DEVELOPMENT)
    
    def test_parse_unknown_flag_defaults_to_development(self):
        """Test that unknown flags default to development."""
        with patch('sys.argv', ['script.py', '--unknown']):
            env = parse_environment_from_args()
            self.assertEqual(env, DatabaseEnvironment.DEVELOPMENT)
    
    def test_parse_multiple_flags_deployment_takes_precedence(self):
        """Test that --deployment takes precedence over --development."""
        with patch('sys.argv', ['script.py', '--development', '--deployment']):
            env = parse_environment_from_args()
            self.assertEqual(env, DatabaseEnvironment.DEPLOYMENT)


class TestDatabaseAdapterFactoryEndToEnd(unittest.TestCase):
    """End-to-end integration tests for DatabaseAdapterFactory."""
    
    def setUp(self):
        """Reset factory before each test."""
        DatabaseAdapterFactory.reset()
    
    def tearDown(self):
        """Clean up after each test."""
        DatabaseAdapterFactory.reset()
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    def test_full_workflow_development(self, mock_local_adapter):
        """Test complete workflow for development environment."""
        mock_adapter = Mock(spec=LocalDatabaseAdapter)
        mock_local_adapter.return_value = mock_adapter
        
        # Initialize factory
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        
        # Get instance multiple times
        instance1 = DatabaseAdapterFactory.get_instance()
        instance2 = DatabaseAdapterFactory.get_instance()
        
        # Should be same instance
        self.assertIs(instance1, instance2)
        
        # Reset and verify cleanup
        DatabaseAdapterFactory.reset()
        self.assertIsNone(DatabaseAdapterFactory._instance)
        
        # Should raise error after reset
        with self.assertRaises(RuntimeError):
            DatabaseAdapterFactory.get_instance()
    
    @patch('database.adaper_factory.GcpDatabaseAdapter')
    def test_full_workflow_deployment(self, mock_gcp_adapter):
        """Test complete workflow for deployment environment."""
        mock_adapter = Mock(spec=GcpDatabaseAdapter)
        mock_gcp_adapter.return_value = mock_adapter
        
        # Initialize factory
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        
        # Get instance
        instance = DatabaseAdapterFactory.get_instance()
        
        self.assertIsNotNone(instance)
        self.assertEqual(instance, mock_adapter)
        
        # Reset
        DatabaseAdapterFactory.reset()
        mock_adapter.close.assert_called_once()
    
    @patch('database.adaper_factory.LocalDatabaseAdapter')
    @patch('database.adaper_factory.GcpDatabaseAdapter')
    def test_switching_environments(self, mock_gcp_adapter, mock_local_adapter):
        """Test switching between environments."""
        mock_local = Mock(spec=LocalDatabaseAdapter)
        mock_gcp = Mock(spec=GcpDatabaseAdapter)
        mock_local_adapter.return_value = mock_local
        mock_gcp_adapter.return_value = mock_gcp
        
        # Start with development
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEVELOPMENT)
        instance1 = DatabaseAdapterFactory.get_instance()
        self.assertEqual(instance1, mock_local)
        
        # Switch to deployment
        DatabaseAdapterFactory.initialize(DatabaseEnvironment.DEPLOYMENT)
        instance2 = DatabaseAdapterFactory.get_instance()
        self.assertEqual(instance2, mock_gcp)
        
        # Instances should be different
        self.assertIsNot(instance1, instance2)


if __name__ == '__main__':
    unittest.main()
