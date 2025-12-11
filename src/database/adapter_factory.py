import logging
from enum import Enum
from typing import Optional

from src.database.adapter_base import DatabaseAdapterBaseDefinition
from src.database.local_adapter import LocalDatabaseAdapter
from src.database.gcp_adapter import GcpDatabaseAdapter


class DatabaseEnvironment(Enum):
    '''
    Enum for different deployment environments.
    '''
    DEVELOPMENT = "development"
    DEPLOYMENT = "deployment"


class DatabaseAdapterFactory:
    '''
    Factory class for creating the appropriate database adapter based on the deployment environment.
    
    Usage:
        The database instance can be used by calling the appropriate class method.
        On this object, all other performing methods are defined.
        ```
        from src.database.adapter_factory import DatabaseAdapterFactory
        db_adapter = DatabaseAdapterFactory.get_instance()
        ```
    '''
    
    _instance: Optional[DatabaseAdapterBaseDefinition] = None
    _environment: Optional[DatabaseEnvironment] = None
    
    @classmethod
    def initialize(cls, environment: DatabaseEnvironment) -> None:
        '''
        Initialize the factory with the specified environment.
        
        Args:
            environment: The deployment environment (DEVELOPMENT or DEPLOYMENT)
        '''
        cls._environment = environment
        cls._instance = None  # Reset instance to force recreation
        logging.info(f"DatabaseAdapterFactory initialized with environment: {environment.value}")
    
    @classmethod
    def get_instance(cls) -> DatabaseAdapterBaseDefinition:
        '''
        Get the singleton database adapter instance.
        
        Returns:
            DatabaseAdapterBaseDefinition: The appropriate database adapter
            
        Raises:
            RuntimeError: If the factory has not been initialized
        '''
        if cls._environment is None:
            raise RuntimeError(
                "DatabaseAdapterFactory not initialized. "
                "Call DatabaseAdapterFactory.initialize() first."
            )
        
        if cls._instance is None:
            cls._instance = cls._create_adapter(cls._environment)
        
        return cls._instance
    
    @classmethod
    def _create_adapter(cls, environment: DatabaseEnvironment) -> DatabaseAdapterBaseDefinition:
        '''
        Create the appropriate database adapter based on the environment.
        
        Args:
            environment: The deployment environment
            
        Returns:
            DatabaseAdapterBaseDefinition: The appropriate database adapter
        '''
        if environment == DatabaseEnvironment.DEVELOPMENT:
            logging.info("Creating LocalDatabaseAdapter for development environment")
            return cls._create_local_adapter()
        elif environment == DatabaseEnvironment.DEPLOYMENT:
            logging.info("Creating GcpDatabaseAdapter for deployment environment")
            return cls._create_gcp_adapter()
        else:
            raise ValueError(f"Unknown environment: {environment}")
    
    @classmethod
    def _create_local_adapter(cls) -> LocalDatabaseAdapter:
        '''
        Create a local database adapter.
        
        Returns:
            LocalDatabaseAdapter: Configured local database adapter
        '''
        return LocalDatabaseAdapter(
            host="127.0.0.1",
            port=5432,
            database="ticker_calendar_local_dev_db",
            user="ticker_dev",
            password="dev_password_123",
            pool_size=5,
            max_overflow=10,
            echo=False
        )
    
    @classmethod
    def _create_gcp_adapter(cls) -> GcpDatabaseAdapter:
        '''
        Create a GCP database adapter with configuration from environment variables.
        
        Returns:
            GcpDatabaseAdapter: Configured GCP database adapter
        '''
        return GcpDatabaseAdapter()
    
    @classmethod
    def reset(cls) -> None:
        '''
        Reset the factory (useful for testing).
        Closes any existing adapter and clears the instance.
        '''
        if cls._instance is not None:
            try:
                cls._instance.close()
            except Exception as e:
                logging.warning(f"Error closing database adapter during reset: {e}")
        cls._instance = None
        cls._environment = None


def parse_environment_from_args() -> DatabaseEnvironment:
    '''
    Parse the environment from command-line arguments.
    
    Returns:
        Environment: DEVELOPMENT if --development flag is present or no flag,
                    DEPLOYMENT if --deployment flag is present
    '''
    import sys
    
    if "--deployment" in sys.argv:
        return DatabaseEnvironment.DEPLOYMENT
    elif "--development" in sys.argv or len(sys.argv) == 1:
        # Default to DEVELOPMENT if no flags or explicit --development
        return DatabaseEnvironment.DEVELOPMENT
    else:
        # Default to DEVELOPMENT for any other case
        return DatabaseEnvironment.DEVELOPMENT
