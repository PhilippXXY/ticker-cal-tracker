# Disclaimer: Created by GitHub Copilot
# IMPORTANT: These tests will modify data in the database

import unittest
import os
from pathlib import Path
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import text


from src.database.local_adapter import LocalDatabaseAdapter


# Skip integration tests if flag is set
SKIP_DB_INTEGRATION = os.getenv('SKIP_DB_INTEGRATION_TESTS') == '1'


@unittest.skipIf(SKIP_DB_INTEGRATION, "Skipping database integration tests")
class TestLocalDatabaseAdapterIntegration(unittest.TestCase):
    """Integration tests for LocalDatabaseAdapter with real database."""
    
    @classmethod
    def setUpClass(cls):
        """Set up database connection for all tests."""
        # Use default connection parameters for local dev database
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
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database connection."""
        cls.adapter.close()
    
    def setUp(self):
        """Set up test data before each test."""
        # Create a test table for our integration tests
        with self.adapter.get_session() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS test_integration (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
    
    def tearDown(self):
        """Clean up test data after each test."""
        # Drop test table
        with self.adapter.get_session() as session:
            session.execute(text("DROP TABLE IF EXISTS test_integration CASCADE"))
    
    def test_health_check_with_real_database(self):
        """Test health_check with real database connection."""
        is_healthy = self.adapter.health_check()
        self.assertTrue(is_healthy)
    
    def test_get_engine(self):
        """Test get_engine returns valid engine."""
        engine = self.adapter.get_engine()
        self.assertIsNotNone(engine)
        
        # Verify we can connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            self.assertIsNotNone(result)
    
    def test_get_session_context_manager(self):
        """Test get_session works as context manager."""
        with self.adapter.get_session() as session:
            result = session.execute(text("SELECT 1 as value"))
            row = result.fetchone()
            self.assertEqual(row[0], 1)  # type: ignore
    
    def test_execute_query_select(self):
        """Test execute_query with SELECT statement."""
        # Insert test data
        with self.adapter.get_session() as session:
            session.execute(text("""
                INSERT INTO test_integration (name, value) 
                VALUES ('test1', 100), ('test2', 200), ('test3', 300)
            """))
        
        # Query the data
        results = self.adapter.execute_query(
            query="SELECT name, value FROM test_integration ORDER BY value"
        )
        
        self.assertEqual(len(results), 3)  # type: ignore
        self.assertEqual(results[0]['name'], 'test1')  # type: ignore
        self.assertEqual(results[0]['value'], 100)  # type: ignore
        self.assertEqual(results[1]['name'], 'test2')  # type: ignore
        self.assertEqual(results[1]['value'], 200)  # type: ignore
    
    def test_execute_query_with_parameters(self):
        """Test execute_query with parameterized query."""
        # Insert test data
        with self.adapter.get_session() as session:
            session.execute(text("""
                INSERT INTO test_integration (name, value) 
                VALUES ('test1', 100), ('test2', 200)
            """))
        
        # Query with parameters
        results = self.adapter.execute_query(
            query="SELECT * FROM test_integration WHERE value > :min_value",
            params={'min_value': 150}
        )
        
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0]['name'], 'test2')  # type: ignore
    
    def test_execute_query_no_results(self):
        """Test execute_query when no rows match."""
        results = self.adapter.execute_query(
            query="SELECT * FROM test_integration WHERE id = :id",
            params={'id': 99999}
        )
        
        self.assertEqual(len(results), 0)  # type: ignore
    
    def test_execute_update_insert(self):
        """Test execute_update with INSERT statement."""
        affected = self.adapter.execute_update(
            query="INSERT INTO test_integration (name, value) VALUES (:name, :value)",
            params={'name': 'test_insert', 'value': 42}
        )
        
        self.assertEqual(affected, 1)
        
        # Verify the insert
        results = self.adapter.execute_query(
            query="SELECT * FROM test_integration WHERE name = :name",
            params={'name': 'test_insert'}
        )
        
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0]['value'], 42)  # type: ignore
    
    def test_execute_update_update(self):
        """Test execute_update with UPDATE statement."""
        # Insert test data
        self.adapter.execute_update(
            query="INSERT INTO test_integration (name, value) VALUES (:name, :value)",
            params={'name': 'test_update', 'value': 100}
        )
        
        # Update the data
        affected = self.adapter.execute_update(
            query="UPDATE test_integration SET value = :new_value WHERE name = :name",
            params={'new_value': 200, 'name': 'test_update'}
        )
        
        self.assertEqual(affected, 1)
        
        # Verify the update
        results = self.adapter.execute_query(
            query="SELECT value FROM test_integration WHERE name = :name",
            params={'name': 'test_update'}
        )
        
        self.assertEqual(results[0]['value'], 200)  # type: ignore
    
    def test_execute_update_delete(self):
        """Test execute_update with DELETE statement."""
        # Insert test data
        with self.adapter.get_session() as session:
            session.execute(text("""
                INSERT INTO test_integration (name, value) 
                VALUES ('test1', 100), ('test2', 200), ('test3', 300)
            """))
        
        # Delete rows
        affected = self.adapter.execute_update(
            query="DELETE FROM test_integration WHERE value > :threshold",
            params={'threshold': 150}
        )
        
        # Should delete 2 rows (test2 and test3)
        self.assertEqual(affected, 2)
        
        # Verify only test1 remains
        results = self.adapter.execute_query(
            query="SELECT name FROM test_integration"
        )
        
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0]['name'], 'test1')  # type: ignore
    
    def test_execute_many(self):
        """Test execute_many with multiple inserts."""
        params_list = [
            {'name': 'bulk1', 'value': 1},
            {'name': 'bulk2', 'value': 2},
            {'name': 'bulk3', 'value': 3},
            {'name': 'bulk4', 'value': 4},
        ]
        
        total_affected = self.adapter.execute_many(
            query="INSERT INTO test_integration (name, value) VALUES (:name, :value)",
            params_list=params_list
        )
        
        self.assertEqual(total_affected, 4)
        
        # Verify all rows were inserted
        results = self.adapter.execute_query(
            query="SELECT COUNT(*) as count FROM test_integration"
        )
        
        self.assertEqual(results[0]['count'], 4)  # type: ignore
    
    def test_execute_many_with_updates(self):
        """Test execute_many with UPDATE statements."""
        # Insert initial data
        self.adapter.execute_many(
            query="INSERT INTO test_integration (name, value) VALUES (:name, :value)",
            params_list=[
                {'name': 'item1', 'value': 10},
                {'name': 'item2', 'value': 20},
                {'name': 'item3', 'value': 30},
            ]
        )
        
        # Update all items
        params_list = [
            {'name': 'item1', 'new_value': 100},
            {'name': 'item2', 'new_value': 200},
            {'name': 'item3', 'new_value': 300},
        ]
        
        total_affected = self.adapter.execute_many(
            query="UPDATE test_integration SET value = :new_value WHERE name = :name",
            params_list=params_list
        )
        
        self.assertEqual(total_affected, 3)
        
        # Verify updates
        results = self.adapter.execute_query(
            query="SELECT value FROM test_integration WHERE name = :name",
            params={'name': 'item2'}
        )
        
        self.assertEqual(results[0]['value'], 200)  # type: ignore
    
    def test_transaction_commit(self):
        """Test that transactions are committed automatically."""
        # Insert data in a session
        with self.adapter.get_session() as session:
            session.execute(text("""
                INSERT INTO test_integration (name, value) VALUES ('commit_test', 999)
            """))
        # Session auto-commits on exit
        
        # Verify data persists in a new session
        results = self.adapter.execute_query(
            query="SELECT * FROM test_integration WHERE name = :name",
            params={'name': 'commit_test'}
        )
        
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0]['value'], 999)  # type: ignore
    
    def test_transaction_rollback_on_error(self):
        """Test that transactions rollback on error."""
        # Insert initial data
        self.adapter.execute_update(
            query="INSERT INTO test_integration (name, value) VALUES (:name, :value)",
            params={'name': 'rollback_test', 'value': 100}
        )
        
        # Try to execute invalid SQL in a session (should rollback)
        try:
            with self.adapter.get_session() as session:
                session.execute(text("""
                    INSERT INTO test_integration (name, value) VALUES ('valid', 200)
                """))
                # This will fail (invalid column)
                session.execute(text("""
                    INSERT INTO test_integration (invalid_column) VALUES ('fail')
                """))
        except Exception:
            pass  # Expected to fail
        
        # Verify the valid insert was rolled back
        results = self.adapter.execute_query(
            query="SELECT * FROM test_integration WHERE name = :name",
            params={'name': 'valid'}
        )
        
        self.assertEqual(len(results), 0)  # type: ignore
    
    def test_concurrent_sessions(self):
        """Test multiple concurrent sessions."""
        # Create multiple sessions and execute queries
        with self.adapter.get_session() as session1:
            session1.execute(text("""
                INSERT INTO test_integration (name, value) VALUES ('concurrent1', 1)
            """))
        
        with self.adapter.get_session() as session2:
            session2.execute(text("""
                INSERT INTO test_integration (name, value) VALUES ('concurrent2', 2)
            """))
        
        # Verify both inserts succeeded
        results = self.adapter.execute_query(
            query="SELECT COUNT(*) as count FROM test_integration"
        )
        
        self.assertEqual(results[0]['count'], 2)  # type: ignore


@unittest.skipIf(SKIP_DB_INTEGRATION, "Skipping database integration tests")
class TestLocalDatabaseAdapterWithRealSchema(unittest.TestCase):
    """Integration tests using the actual database schema."""
    
    @classmethod
    def setUpClass(cls):
        """Set up database connection for all tests."""
        cls.adapter = LocalDatabaseAdapter(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'ticker_calendar_local_dev_db'),
            user=os.getenv('DB_USER', 'ticker_dev'),
            password=os.getenv('DB_PASSWORD', 'dev_password_123')
        )
        
        if not cls.adapter.health_check():
            raise unittest.SkipTest("Database is not accessible")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database connection."""
        cls.adapter.close()
    
    def setUp(self):
        """Store initial state for cleanup."""
        # Get count of test data we'll add
        self.test_email = f'test_{datetime.now().timestamp()}@integration.test'
    
    def tearDown(self):
        """Clean up test data."""
        # Clean up test user and cascading data
        self.adapter.execute_update(
            query="DELETE FROM users WHERE email = :email",
            params={'email': self.test_email}
        )
    
    def test_query_stocks_table(self):
        """Test querying the stocks table."""
        results = self.adapter.execute_query(
            query="SELECT ticker, name FROM stocks LIMIT 5"
        )
        
        # Should have stocks from seed data
        self.assertGreater(len(results), 0)  # type: ignore
        self.assertIn('ticker', results[0])  # type: ignore
        self.assertIn('name', results[0])  # type: ignore
    
    def test_query_with_joins(self):
        """Test complex query with joins."""
        query = """
            SELECT 
                w.name as watchlist_name,
                s.ticker,
                s.name as stock_name
            FROM watchlists w
            JOIN follows f ON w.id = f.watchlist_id
            JOIN stocks s ON f.stock_ticker = s.ticker
            LIMIT 5
        """
        
        results = self.adapter.execute_query(query=query)
        
        # Should have data from seed data
        if len(results) > 0:  # type: ignore
            self.assertIn('watchlist_name', results[0])  # type: ignore
            self.assertIn('ticker', results[0])  # type: ignore
            self.assertIn('stock_name', results[0])  # type: ignore
    
    def test_insert_and_query_user(self):
        """Test inserting and querying a user."""
        # Insert a test user
        affected = self.adapter.execute_update(
            query="INSERT INTO users (email, password) VALUES (:email, :password)",
            params={'email': self.test_email, 'password': 'hashed_password'}
        )
        
        self.assertEqual(affected, 1)
        
        # Query the user
        results = self.adapter.execute_query(
            query="SELECT email, created_at FROM users WHERE email = :email",
            params={'email': self.test_email}
        )
        
        self.assertEqual(len(results), 1)  # type: ignore
        self.assertEqual(results[0]['email'], self.test_email)  # type: ignore
        self.assertIsNotNone(results[0]['created_at'])  # type: ignore
    
    def test_insert_stock_and_events(self):
        """Test inserting stock and related events."""
        test_ticker = 'TEST'
        
        try:
            # Insert stock
            self.adapter.execute_update(
                query="INSERT INTO stocks (ticker, name) VALUES (:ticker, :name)",
                params={'ticker': test_ticker, 'name': 'Test Company'}
            )
            
            # Insert events using execute_many
            events = [
                {
                    'ticker': test_ticker,
                    'type': 'EARNINGS_ANNOUNCEMENT',
                    'date': (datetime.now() + timedelta(days=7)).date()
                },
                {
                    'ticker': test_ticker,
                    'type': 'DIVIDEND_EX',
                    'date': (datetime.now() + timedelta(days=14)).date()
                }
            ]
            
            total_affected = self.adapter.execute_many(
                query="""
                    INSERT INTO stock_events (stock_ticker, type, event_date) 
                    VALUES (:ticker, :type, :date)
                """,
                params_list=events
            )
            
            self.assertEqual(total_affected, 2)
            
            # Query events
            results = self.adapter.execute_query(
                query="SELECT type, event_date FROM stock_events WHERE stock_ticker = :ticker",
                params={'ticker': test_ticker}
            )
            
            self.assertEqual(len(results), 2)  # type: ignore
            
        finally:
            # Cleanup
            self.adapter.execute_update(
                query="DELETE FROM stocks WHERE ticker = :ticker",
                params={'ticker': test_ticker}
            )
    
    @unittest.skip("user_preferences table not implemented in schema")
    def test_user_preferences_cascade(self):
        """Test that user preferences are created and cascade on delete."""
        # Insert user
        self.adapter.execute_update(
            query="INSERT INTO users (email, password) VALUES (:email, :password)",
            params={'email': self.test_email, 'password': 'hashed_password'}
        )
        
        # Get user id
        user_result = self.adapter.execute_query(
            query="SELECT id FROM users WHERE email = :email",
            params={'email': self.test_email}
        )
        user_id = user_result[0]['id']  # type: ignore
        
        # Insert preferences
        self.adapter.execute_update(
            query="""
                INSERT INTO user_preferences (user_id, default_reminder_before) 
                VALUES (:user_id, :reminder)
            """,
            params={'user_id': user_id, 'reminder': '2 days'}
        )
        
        # Verify preferences exist
        prefs = self.adapter.execute_query(
            query="SELECT * FROM user_preferences WHERE user_id = :user_id",
            params={'user_id': user_id}
        )
        self.assertEqual(len(prefs), 1)  # type: ignore
        
        # Delete user (should cascade to preferences)
        self.adapter.execute_update(
            query="DELETE FROM users WHERE email = :email",
            params={'email': self.test_email}
        )
        
        # Verify preferences were deleted
        prefs_after = self.adapter.execute_query(
            query="SELECT * FROM user_preferences WHERE user_id = :user_id",
            params={'user_id': user_id}
        )
        self.assertEqual(len(prefs_after), 0) # type: ignore


if __name__ == '__main__':
    # Provide helpful message if database is not running
    adapter = LocalDatabaseAdapter()
    if not adapter.health_check():
        print("\n" + "="*70)
        print("⚠️  Database is not accessible!")
        print("="*70)
        print("\nPlease start the database first:")
        print("  python database/local/manage_db.py setup")
        print("\nOr set SKIP_DB_INTEGRATION_TESTS=1 to skip these tests.")
        print("="*70 + "\n")
        adapter.close()
        exit(1)
    adapter.close()
    
    unittest.main()
