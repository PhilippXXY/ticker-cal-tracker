from contextlib import contextmanager
from typing import Any, Dict, Generator, Iterable, List, Mapping, Optional, cast
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Engine, create_engine, text, CursorResult
from sqlalchemy.exc import SQLAlchemyError

from database.adapter_base import DatabaseAdapterBaseDefinition

class LocalDatabaseAdapter(DatabaseAdapterBaseDefinition):
    '''
    Database adapter for local PostgreSQL database
    '''
    
    def __init__(
        self, *,
        host: str = "127.0.0.1",
        port: int = 5432,
        database: str = "ticker_calendar_local_dev_db",
        user: str = "ticker_dev",
        password: str = "dev_password_123",
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False
    ):
        '''
        Initialize the local database adapter.
        
        Args:
            host: Database host (default: localhost)
            port: Database port (default: 5432)
            database: Database name
            user: Database user
            password: Database password
            pool_size: Size of the connection pool (default: 5)
            max_overflow: Max overflow connections (default: 10)
            echo: Whether to echo SQL queries (default: False, useful for debugging)
        '''
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        
        # Create connection string
        self.connection_string = (f"postgresql://{user}:{password}@{host}:{port}/{database}")
 
        # Create database engine with connection pooling
        self.engine = create_engine(
            self.connection_string,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
            pool_pre_ping=True
            )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
            
    def get_engine(self) -> Engine:
        '''
        Get the SQLAlchemy engine instance.
        
        Returns:
            Engine: SQLAlchemy engine for the database
        '''
        return self.engine
    
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
        session = self.session_factory()
        
        try:
            # .begin() handles commit and rollback automatically
            with session.begin():
                yield session
        finally:
            session.close()

    def execute_query(self, *, query: str, params: Dict[str, Any] | None = None) -> Iterable[Mapping[str, Any]]:
        '''
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters
            
        Returns:
            Iterable of row mappings (dict-like objects)
        '''
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            # Convert rows to dictionaries and collect them
            rows = [dict(row._mapping) for row in result]
        return rows

    def execute_update(self, *, query: str, params: Dict[str, Any] | None = None) -> int:
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
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            # Cast to CursorResult to access rowcount
            cursor_result = cast(CursorResult[Any], result)
            return cursor_result.rowcount
        
    def execute_many(self, *, query: str, params_list: List[Dict[str, Any]]) -> int:
        '''
        Execute the same query multiple times with different parameters.
        
         Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            Total number of rows affected
        '''
        if not params_list:
            return 0
        
        with self.get_session() as session:
            total_affected = 0
            for params in params_list:
                result = session.execute(text(query), params)
                # Cast to CursorResult to access rowcount
                cursor_result = cast(CursorResult[Any], result)
                total_affected += cursor_result.rowcount
            return total_affected
        
    
    def health_check(self) -> bool:
        '''
        Check if the database connection is healthy.
        
        Returns:
            bool: True if database is reachable and healthy, False otherwise
        '''
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
        
    
    def close(self):
        '''
        Close database connections and clean up resources.
        
        Should be called when shutting down the application.
        '''
        if self.engine:
            self.engine.dispose()