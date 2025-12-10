
from abc import ABC, abstractmethod
from contextlib import contextmanager
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from typing import Any, Dict, Generator, Iterable, List, Mapping, Optional
from src.models.user_model import User

class DatabaseAdapterBaseDefinition(ABC):
    '''
    Abstract base class for database operations.
    
    All concrete database adapters (Local, GCP, etc.) must implement
    these methods to ensure consistent behavior across environments.
    '''
    
    @abstractmethod
    def get_engine(self) -> Engine:
        '''
        Get the SQLAlchemy engine instance.
        
        Returns:
            Engine: SQLAlchemy engine for the database
        '''
        pass
    
    @abstractmethod
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        '''
        Context manager for database sessions.

        Provides automatic session management with commit/rollback.

        Usage:
            ```
            with db_adapter.get_session() as session:
                session.execute(...)
            ```

        Yields:
            Session: SQLAlchemy session object
        '''
        pass
    
    @abstractmethod
    def execute_query(self, *, query: str, params: Optional[Dict[str, Any]] = None) -> Iterable[Mapping[str, Any]]:
        '''
        Execute a raw SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional query parameters for safe parameter binding
            
        Returns:
            Iterable: An iterable of dict-like rows where each key
            is a column name and each value is the corresponding cell.
            
        Example:
            ```
            results = adapter.execute_query(
                "SELECT * FROM users WHERE email = :email",
                {"email": "user@example.com"}
            )
            ```
        '''
        pass

    @abstractmethod
    def execute_update(self, *, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        '''
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Optional query parameters for safe parameter binding
            
        Returns:
            Number of rows affected
            
        Example:
            ```
            rows = adapter.execute_update(
                "UPDATE users SET password = :pwd WHERE id = :id",
                {"pwd": "hashed_password", "id": user_id}
            )
            ```
        '''
        pass
    
    @abstractmethod
    def execute_many(self, *, query: str, params_list: List[Dict[str, Any]]) -> int:
        '''
        Execute the same query multiple times with different parameters.
        
         Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            Total number of rows affected
        '''
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        '''
        Check if the database connection is healthy.
        
        Returns:
            bool: True if database is reachable and healthy, False otherwise
        '''
        pass
    
    @abstractmethod
    def close(self):
        '''
        Close database connections and clean up resources.
        
        Should be called when shutting down the application.
        '''
        pass

    @abstractmethod
    def save_user(self, user: User) -> None:
        '''
        Save a user to the database.
        
        Args:
            user: User object to save
        '''
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        '''
        Retrieve a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        '''
        pass
