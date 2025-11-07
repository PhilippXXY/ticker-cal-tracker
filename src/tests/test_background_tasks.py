# Disclaimer: Created by GitHub Copilot

import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from src.app.background.tasks import update_stale_stock_events
from src.models.stock_model import Stock
from src.models.stock_event_model import EventType


class TestBackgroundTasks(unittest.TestCase):
    '''Test suite for background tasks.'''
    
    @patch('src.app.background.tasks.DatabaseAdapterFactory')
    @patch('src.app.background.tasks.StocksService')
    def test_update_stale_stock_events_success(self, mock_stocks_service_class, mock_db_factory):
        '''Test successful update of stale stock events.'''
        # Arrange
        mock_db = Mock()
        mock_db_factory.get_instance.return_value = mock_db
        
        # Mock stale stocks from database
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        
        mock_db.execute_query.return_value = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'last_updated': old_date,
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'last_updated': old_date,
            },
        ]
        
        mock_stocks_service = Mock()
        mock_stocks_service_class.return_value = mock_stocks_service
        
        # Act
        update_stale_stock_events()
        
        # Assert
        # Verify query was called with correct cutoff date
        self.assertTrue(mock_db.execute_query.called)
        query_call = mock_db.execute_query.call_args
        self.assertIn('cutoff_date', query_call[1]['params'])
        
        # Verify upsert_stock_events was called for each stock
        self.assertEqual(mock_stocks_service.upsert_stock_events.call_count, 2)
        
        # Verify stock objects were created correctly
        calls = mock_stocks_service.upsert_stock_events.call_args_list
        self.assertEqual(calls[0][1]['stock'].symbol, 'AAPL')
        self.assertEqual(calls[1][1]['stock'].symbol, 'MSFT')
        
        # Verify all event types were requested
        for call in calls:
            event_types = call[1]['event_types']
            self.assertEqual(len(event_types), len(list(EventType)))
        
        # Verify last_updated was updated for each stock
        self.assertEqual(mock_db.execute_update.call_count, 2)
    
    @patch('src.app.background.tasks.DatabaseAdapterFactory')
    @patch('src.app.background.tasks.StocksService')
    def test_update_stale_stock_events_no_stale_stocks(self, mock_stocks_service_class, mock_db_factory):
        '''Test when there are no stale stocks to update.'''
        # Arrange
        mock_db = Mock()
        mock_db_factory.get_instance.return_value = mock_db
        mock_db.execute_query.return_value = []
        
        mock_stocks_service = Mock()
        mock_stocks_service_class.return_value = mock_stocks_service
        
        # Act
        update_stale_stock_events()
        
        # Assert
        # Verify query was called
        self.assertTrue(mock_db.execute_query.called)
        
        # Verify no updates were attempted
        self.assertEqual(mock_stocks_service.upsert_stock_events.call_count, 0)
        self.assertEqual(mock_db.execute_update.call_count, 0)
    
    @patch('src.app.background.tasks.DatabaseAdapterFactory')
    @patch('src.app.background.tasks.StocksService')
    @patch('src.app.background.tasks.logger')
    def test_update_stale_stock_events_partial_failure(self, mock_logger, mock_stocks_service_class, mock_db_factory):
        '''Test that task continues even if some stocks fail to update.'''
        # Arrange
        mock_db = Mock()
        mock_db_factory.get_instance.return_value = mock_db
        
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        mock_db.execute_query.return_value = [
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'last_updated': old_date},
            {'ticker': 'FAIL', 'name': 'Fail Corp.', 'last_updated': old_date},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'last_updated': old_date},
        ]
        
        mock_stocks_service = Mock()
        
        # Make the second stock fail
        def upsert_side_effect(*args, **kwargs):
            stock = kwargs.get('stock')
            if stock.symbol == 'FAIL': # pyright: ignore[reportOptionalMemberAccess]
                raise Exception("API error")
        
        mock_stocks_service.upsert_stock_events.side_effect = upsert_side_effect
        mock_stocks_service_class.return_value = mock_stocks_service
        
        # Act
        update_stale_stock_events()
        
        # Assert
        # Verify all stocks were attempted
        self.assertEqual(mock_stocks_service.upsert_stock_events.call_count, 3)
        
        # Verify error was logged
        error_logs = [call for call in mock_logger.error.call_args_list 
                      if 'FAIL' in str(call)]
        self.assertGreater(len(error_logs), 0)
        
        # Verify successful stocks were still updated (only 2 updates, not 3)
        self.assertEqual(mock_db.execute_update.call_count, 2)


if __name__ == '__main__':
    unittest.main()
