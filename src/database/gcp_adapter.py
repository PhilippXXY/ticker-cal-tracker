from contextlib import contextmanager
import os
from typing import Any, Dict, Generator, Iterable, List, Mapping, Optional, cast
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import CursorResult, Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.database.adapter_base import DatabaseAdapterBaseDefinition
from src.models.user_model import User

class GcpDatabaseAdapter(DatabaseAdapterBaseDefinition):
    '''
    Database adapter for Google Cloud SQL (PostgreSQL).

    Supports two modes:

    1) Cloud Run / Cloud SQL connector via Unix socket:
       - USE_CLOUDSQL_SOCKET=true
       - INSTANCE_CONNECTION_NAME set (e.g. "project:region:instance")
       - DB_USER, DB_PASSWORD, DB_NAME set

    2) Direct TCP (local machine to Cloud SQL public IP):
       - USE_CLOUDSQL_SOCKET=false (or unset)
       - DB_HOST, DB_PORT set (plus DB_USER, DB_PASSWORD, DB_NAME)
    '''
     
    def __init__(self) -> None:
        '''
        Initialize the GCP database adapter with connection pooling.
        
        Configures database connection based on deployment environment:
        - Cloud SQL with Unix socket when USE_CLOUDSQL_SOCKET is "true"
        - Local/standard TCP connection otherwise
        
        Environment Variables:
            - DB_USER (str): Database user name
            - DB_PASSWORD (str): Database password
            - DB_NAME (str): Database name
            - USE_CLOUDSQL_SOCKET (str, optional): Set to "true" for Cloud SQL socket mode. Defaults to "false"
            - DB_INSTANCE_CONNECTION_NAME (str, required if USE_CLOUDSQL_SOCKET="true"): Cloud SQL instance connection name (format: project:region:instance)
            - DB_HOST (str, required if USE_CLOUDSQL_SOCKET="false"): Database host address
            - DB_PORT (str, optional): Database port. Defaults to "5432"
            - DB_POOL_SIZE (str, optional): SQLAlchemy connection pool size. Defaults to "5"
            - DB_MAX_OVERFLOW (str, optional): Maximum overflow connections. Defaults to "10"
            - DB_ECHO (str, optional): Enable SQLAlchemy SQL logging. Defaults to "false"
            
        Attributes:
            connection_string (str): PostgreSQL connection URI
            engine (Engine): SQLAlchemy database engine with connection pooling
            session_factory (sessionmaker): Factory for creating new database sessions
            
        Raises:
            KeyError: If required environment variables are missing
            ValueError: If environment variables contain invalid values
        '''
        # Common settings for 1) and 2)
        db_user = os.environ["DB_USER"]
        db_password = os.environ["DB_PASSWORD"]
        db_name = os.environ["DB_NAME"]
        
        use_socket = os.getenv("USE_CLOUDSQL_SOCKET", "false").lower() == "true"
        
        if use_socket:
            # Cloud Run / Cloud SQL connector via Unix socket
            instance_connection_name = os.environ["DB_INSTANCE_CONNECTION_NAME"]

            # SQLAlchemy/psycopg2 pattern for Unix sockets
            self.connection_string = (
                f"postgresql://{db_user}:{db_password}@/{db_name}"
                f"?host=/cloudsql/{instance_connection_name}"
            )
        else:
            # Local machine
            db_host = os.environ["DB_HOST"]
            db_port = os.getenv("DB_PORT", "5432")
            
            self.connection_string = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
            
        # Pool configuration
        pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        echo = os.getenv("DB_ECHO", "false").lower() == "true"

        # Create database engine with connection pooling
        self.engine: Engine = create_engine(
            self.connection_string,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
            pool_pre_ping=True,
        )

        # Session factory
        self.session_factory = sessionmaker(bind=self.engine)


    def get_engine(self) -> Engine:
        '''
        Get the SQLAlchemy engine instance.
        '''
        return self.engine
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        '''
        Context manager for database sessions.
        Provides automatic commit/rollback on exit.
        '''
        session: Session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(self, *, query: str, params: Optional[Dict[str, Any]] = None) -> Iterable[Mapping[str, Any]]:
        '''
        Execute a SELECT query and return an iterable of row mappings.
        '''
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            rows = [dict(row._mapping) for row in result]
            return rows

    def execute_update(self, *, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        '''
        Execute an INSERT/UPDATE/DELETE query and return affected row count.
        '''
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            cursor_result = cast(CursorResult[Any], result)
            return cursor_result.rowcount
    
    def execute_many(self, *, query: str, params_list: List[Dict[str, Any]]) -> int:
        '''
        Execute the same non-SELECT query multiple times with different params.
        '''
        if not params_list:
            return 0

        with self.get_session() as session:
            total_affected = 0
            for params in params_list:
                result = session.execute(text(query), params)
                cursor_result = cast(CursorResult[Any], result)
                total_affected += cursor_result.rowcount
            return total_affected
    
    def health_check(self) -> bool:
        '''
        Basic health check: attempts to run `SELECT 1`.
        '''
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
    
    def close(self) -> None:
        '''
        Dispose of the engine and close all connections.
        '''
        if self.engine:
            self.engine.dispose()

    def save_user(self, user: User) -> None:
        '''
        Save a user to the database.
        '''
        query = '''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (:username, :email, :password_hash, NOW())
            RETURNING id, created_at
        '''
        params = {
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash
        }
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            row = result.fetchone()
            if row:
                user.id = row.id
                user.created_at = row.created_at

    def get_user_by_username(self, username: str):
        '''
        Retrieve a user by username.
        '''
        query = "SELECT * FROM users WHERE username = :username"
        
        with self.get_session() as session:
            result = session.execute(text(query), {"username": username})
            row = result.fetchone()
            
            if row:
                return User(
                    id=row.id,
                    username=row.username,
                    email=row.email,
                    password_hash=row.password_hash,
                    created_at=row.created_at
                )
            return None

