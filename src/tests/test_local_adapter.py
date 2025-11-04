# Disclaimer: Created by GitHub Copilot

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.database.local_adapter import LocalDatabaseAdapter


class TestLocalDatabaseAdapterInitialization(unittest.TestCase):
    """Test LocalDatabaseAdapter initialization."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_init_with_default_parameters(self, mock_sessionmaker, mock_create_engine):
        """Test initialization with default parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        adapter = LocalDatabaseAdapter()
        
        # Check default values
        self.assertEqual(adapter.host, "127.0.0.1")
        self.assertEqual(adapter.port, 5432)
        self.assertEqual(adapter.database, "ticker_calendar_local_dev_db")
        self.assertEqual(adapter.user, "ticker_dev")
        self.assertEqual(adapter.password, "dev_password_123")
        
        # Check connection string format
        expected_conn_str = "postgresql://ticker_dev:dev_password_123@127.0.0.1:5432/ticker_calendar_local_dev_db"
        self.assertEqual(adapter.connection_string, expected_conn_str)
        
        # Verify engine was created with correct parameters
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        self.assertEqual(call_args[0][0], expected_conn_str)
        self.assertEqual(call_args[1]['pool_size'], 5)
        self.assertEqual(call_args[1]['max_overflow'], 10)
        self.assertEqual(call_args[1]['echo'], False)
        self.assertTrue(call_args[1]['pool_pre_ping'])
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_init_with_custom_parameters(self, mock_sessionmaker, mock_create_engine):
        """Test initialization with custom parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        adapter = LocalDatabaseAdapter(
            host="custom_host",
            port=3306,
            database="custom_db",
            user="custom_user",
            password="custom_pass",
            pool_size=10,
            max_overflow=20,
            echo=True
        )
        
        # Check custom values
        self.assertEqual(adapter.host, "custom_host")
        self.assertEqual(adapter.port, 3306)
        self.assertEqual(adapter.database, "custom_db")
        self.assertEqual(adapter.user, "custom_user")
        self.assertEqual(adapter.password, "custom_pass")
        
        # Check connection string
        expected_conn_str = "postgresql://custom_user:custom_pass@custom_host:3306/custom_db"
        self.assertEqual(adapter.connection_string, expected_conn_str)
        
        # Verify engine parameters
        call_args = mock_create_engine.call_args
        self.assertEqual(call_args[1]['pool_size'], 10)
        self.assertEqual(call_args[1]['max_overflow'], 20)
        self.assertEqual(call_args[1]['echo'], True)
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_session_factory_created(self, mock_sessionmaker, mock_create_engine):
        """Test that session factory is created with engine."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        # Verify sessionmaker was called with engine
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        self.assertEqual(adapter.session_factory, mock_session_factory)


class TestLocalDatabaseAdapterGetEngine(unittest.TestCase):
    """Test get_engine method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_get_engine_returns_engine(self, mock_sessionmaker, mock_create_engine):
        """Test that get_engine returns the SQLAlchemy engine."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        adapter = LocalDatabaseAdapter()
        engine = adapter.get_engine()
        
        self.assertEqual(engine, mock_engine)


class TestLocalDatabaseAdapterGetSession(unittest.TestCase):
    """Test get_session context manager."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_get_session_context_manager(self, mock_sessionmaker, mock_create_engine):
        """Test that get_session works as a context manager."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        with adapter.get_session() as session:
            self.assertEqual(session, mock_session)
            mock_session.begin.assert_called_once()
        
        # After context manager exits, session should be closed
        mock_session.close.assert_called_once()
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_get_session_closes_on_exception(self, mock_sessionmaker, mock_create_engine):
        """Test that session is closed even when exception occurs."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() raise an exception within the context manager
        mock_begin_cm = MagicMock()
        mock_begin_cm.__enter__.side_effect = RuntimeError("Test error")
        mock_session.begin.return_value = mock_begin_cm
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        with self.assertRaises(RuntimeError):
            with adapter.get_session() as session:
                pass
        
        # Session should still be closed
        mock_session.close.assert_called_once()


class TestLocalDatabaseAdapterExecuteQuery(unittest.TestCase):
    """Test execute_query method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_query_without_params(self, mock_sessionmaker, mock_create_engine):
        """Test execute_query without parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        # Setup mock session and result
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock query result
        mock_row1 = Mock()
        mock_row1._mapping = {'id': 1, 'name': 'Test'}
        mock_row2 = Mock()
        mock_row2._mapping = {'id': 2, 'name': 'Test2'}
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([mock_row1, mock_row2]))
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        # Execute query
        query = "SELECT * FROM test_table"
        results = adapter.execute_query(query=query)
        
        # Verify results
        self.assertEqual(len(results), 2)  # type: ignore
        self.assertEqual(results[0], {'id': 1, 'name': 'Test'})  # type: ignore
        self.assertEqual(results[1], {'id': 2, 'name': 'Test2'})  # type: ignore
        
        # Verify session.execute was called
        self.assertTrue(mock_session.execute.called)
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_query_with_params(self, mock_sessionmaker, mock_create_engine):
        """Test execute_query with parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock query result
        mock_row = Mock()
        mock_row._mapping = {'id': 1, 'name': 'Test'}
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([mock_row]))
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        # Execute query with parameters
        query = "SELECT * FROM test_table WHERE id = :id"
        params = {'id': 1}
        results = adapter.execute_query(query=query, params=params)
        
        # Verify results
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0], {'id': 1, 'name': 'Test'})  # type: ignore
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_query_empty_result(self, mock_sessionmaker, mock_create_engine):
        """Test execute_query with no results."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock empty result
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        query = "SELECT * FROM test_table WHERE id = :id"
        results = adapter.execute_query(query=query, params={'id': 999})
        
        self.assertEqual(len(results), 0)  # type: ignore


class TestLocalDatabaseAdapterExecuteUpdate(unittest.TestCase):
    """Test execute_update method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_update_returns_rowcount(self, mock_sessionmaker, mock_create_engine):
        """Test execute_update returns number of affected rows."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock result with rowcount
        mock_result = Mock()
        mock_result.rowcount = 3
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        query = "UPDATE test_table SET name = :name WHERE id = :id"
        params = {'name': 'Updated', 'id': 1}
        affected_rows = adapter.execute_update(query=query, params=params)
        
        self.assertEqual(affected_rows, 3)
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_update_without_params(self, mock_sessionmaker, mock_create_engine):
        """Test execute_update without parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        query = "DELETE FROM test_table"
        affected_rows = adapter.execute_update(query=query)
        
        self.assertEqual(affected_rows, 1)
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_update_no_rows_affected(self, mock_sessionmaker, mock_create_engine):
        """Test execute_update when no rows are affected."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        query = "UPDATE test_table SET name = :name WHERE id = :id"
        affected_rows = adapter.execute_update(query=query, params={'name': 'Test', 'id': 999})
        
        self.assertEqual(affected_rows, 0)


class TestLocalDatabaseAdapterExecuteMany(unittest.TestCase):
    """Test execute_many method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_many_with_multiple_params(self, mock_sessionmaker, mock_create_engine):
        """Test execute_many with multiple parameter sets."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock result for each execution
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        adapter = LocalDatabaseAdapter()
        
        query = "INSERT INTO test_table (name) VALUES (:name)"
        params_list = [
            {'name': 'Test1'},
            {'name': 'Test2'},
            {'name': 'Test3'}
        ]
        
        total_affected = adapter.execute_many(query=query, params_list=params_list)
        
        # Should return total affected rows (3)
        self.assertEqual(total_affected, 3)
        
        # Verify execute was called 3 times
        self.assertEqual(mock_session.execute.call_count, 3)
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_many_with_empty_list(self, mock_sessionmaker, mock_create_engine):
        """Test execute_many with empty parameter list."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        query = "INSERT INTO test_table (name) VALUES (:name)"
        total_affected = adapter.execute_many(query=query, params_list=[])
        
        # Should return 0 without executing
        self.assertEqual(total_affected, 0)
        mock_session.execute.assert_not_called()
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_execute_many_accumulates_rowcount(self, mock_sessionmaker, mock_create_engine):
        """Test execute_many accumulates rowcount from all executions."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        # Mock different rowcounts for each execution
        mock_result1 = Mock()
        mock_result1.rowcount = 2
        mock_result2 = Mock()
        mock_result2.rowcount = 3
        mock_result3 = Mock()
        mock_result3.rowcount = 1
        
        mock_session.execute.side_effect = [mock_result1, mock_result2, mock_result3]
        
        adapter = LocalDatabaseAdapter()
        
        query = "UPDATE test_table SET name = :name WHERE id = :id"
        params_list = [
            {'name': 'Test1', 'id': 1},
            {'name': 'Test2', 'id': 2},
            {'name': 'Test3', 'id': 3}
        ]
        
        total_affected = adapter.execute_many(query=query, params_list=params_list)
        
        # Should return sum of all rowcounts (2 + 3 + 1 = 6)
        self.assertEqual(total_affected, 6)


class TestLocalDatabaseAdapterHealthCheck(unittest.TestCase):
    """Test health_check method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_health_check_success(self, mock_sessionmaker, mock_create_engine):
        """Test health_check returns True when database is healthy."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_session.begin.return_value.__enter__ = Mock(return_value=None)
        mock_session.begin.return_value.__exit__ = Mock(return_value=None)
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        is_healthy = adapter.health_check()
        
        self.assertTrue(is_healthy)
        mock_session.execute.assert_called_once()
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_health_check_failure(self, mock_sessionmaker, mock_create_engine):
        """Test health_check returns False when database is unreachable."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock(spec=Session)
        # Make begin() return a proper context manager
        mock_begin_cm = MagicMock()
        mock_begin_cm.__enter__.side_effect = SQLAlchemyError("Connection failed")
        mock_session.begin.return_value = mock_begin_cm
        
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory
        
        adapter = LocalDatabaseAdapter()
        
        is_healthy = adapter.health_check()
        
        self.assertFalse(is_healthy)


class TestLocalDatabaseAdapterClose(unittest.TestCase):
    """Test close method."""
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_close_disposes_engine(self, mock_sessionmaker, mock_create_engine):
        """Test close disposes the engine."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        adapter = LocalDatabaseAdapter()
        adapter.close()
        
        mock_engine.dispose.assert_called_once()
    
    @patch('src.database.local_adapter.create_engine')
    @patch('src.database.local_adapter.sessionmaker')
    def test_close_with_none_engine(self, mock_sessionmaker, mock_create_engine):
        """Test close handles None engine gracefully."""
        mock_create_engine.return_value = None
        
        adapter = LocalDatabaseAdapter()
        adapter.engine = None  # type: ignore
        
        # Should not raise an error
        adapter.close()


if __name__ == '__main__':
    unittest.main()
