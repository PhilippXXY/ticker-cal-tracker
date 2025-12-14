'''
Service layer for managing watchlists and their tracked stocks.
'''

from typing import Any, Dict, List, Optional
from uuid import UUID

import src.app.utils.calendar_utils as calendar_utils
from src.models.stock_event_model import EventType
from src.app.services.stocks_service import StocksService
from src.database.adapter_factory import DatabaseAdapterFactory


class WatchlistService:
    '''
    Business logic orchestrating watchlist persistence and stock associations.
    '''

    def __init__(self):
        '''
        Initialise the service with database and stock subsystem dependencies.
        '''
        self.db = DatabaseAdapterFactory.get_instance()
        self.stocks_service = StocksService()

    def create_watchlist(
        self,
        *,
        user_id: int,
        name: str,
        watchlist_settings: Dict[EventType, bool],
    ) -> Dict[str, Any]:
        '''
        Create a watchlist with associated settings.

        Returns:
            Dict containing the created watchlist with settings.
            
        Raises:
            ValueError: If inputs are invalid.
            Exception: If watchlist creation fails.
        '''
        if not isinstance(user_id, int):
            raise ValueError('user_id must be an integer.')
        if not name:
            raise ValueError('Watchlist name is required.')
        if not watchlist_settings:
            raise ValueError('Watchlist settings are required.')

        settings_columns = {
            event_type.db_column: bool(enabled)
            for event_type, enabled in watchlist_settings.items()
        }

        # Ensure every event type receives an explicit value.
        for event_type in EventType:
            settings_columns.setdefault(event_type.db_column, True)

        calendar_token = calendar_utils.generate_calendar_token()

        watchlist_query = """
            INSERT INTO watchlists (
                user_id,
                name,
                calendar_token
            )
            VALUES (
                :user_id,
                :name,
                :calendar_token
            )
            RETURNING id
        """

        settings_query = """
            INSERT INTO watchlist_settings (
                watchlist_id,
                include_earnings_announcement,
                include_dividend_ex,
                include_dividend_declaration,
                include_dividend_record,
                include_dividend_payment,
                include_stock_split
            )
            VALUES (
                :watchlist_id,
                :include_earnings_announcement,
                :include_dividend_ex,
                :include_dividend_declaration,
                :include_dividend_record,
                :include_dividend_payment,
                :include_stock_split
            )
        """

        try:
            result = self.db.execute_query(
                query=watchlist_query,
                params={
                    'user_id': user_id,
                    'name': name,
                    'calendar_token': calendar_token,
                },
            )
            result_list = list(result)
            watchlist_id = result_list[0]['id']

            settings_params = {'watchlist_id': watchlist_id}
            settings_params.update(settings_columns)

            self.db.execute_update(
                query=settings_query,
                params=settings_params,
            )
            created = self.get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
            if not created:
                raise Exception('Failed to load watchlist after creation.')
            return created
        except Exception as exc:
            raise Exception(f'Failed to create watchlist: {str(exc)}') from exc

    def get_all_watchlists_for_user(self, *, user_id: int) -> List[Dict[str, Any]]:
        '''
        Get all watchlists for a user.

        Returns:
            List of watchlist dicts with settings.

        Raises:
            TypeError: If user_id is not a UUID.
            Exception: If fetch fails.
        '''
        if not isinstance(user_id, int):
            raise TypeError('user_id must be an integer.')

        query = """
            SELECT
                w.id,
                w.name,
                w.calendar_token,
                w.created_at,
                ws.include_earnings_announcement,
                ws.include_dividend_ex,
                ws.include_dividend_declaration,
                ws.include_dividend_record,
                ws.include_dividend_payment,
                ws.include_stock_split,
                ws.reminder_before,
                ws.updated_at AS settings_updated_at,
                (SELECT COUNT(*) FROM follows f WHERE f.watchlist_id = w.id) AS stock_count
            FROM watchlists w
            LEFT JOIN watchlist_settings ws ON w.id = ws.watchlist_id
            WHERE w.user_id = :user_id
            ORDER BY w.created_at DESC
        """

        try:
            results = self.db.execute_query(
                query=query,
                params={'user_id': user_id},
            )
            return [dict(row) for row in results]
        except Exception as exc:
            raise Exception(f'Failed to fetch watchlists for user: {str(exc)}') from exc

    def get_watchlist_by_id(self, *, user_id: int, watchlist_id: UUID) -> Optional[Dict[str, Any]]:
        '''
        Get a specific watchlist by ID.

        Returns:
            Watchlist dict with settings, or None if not found.

        Raises:
            Exception: If fetch fails.
        '''
        query = """
            SELECT
                w.id,
                w.name,
                w.calendar_token,
                w.created_at,
                ws.include_earnings_announcement,
                ws.include_dividend_ex,
                ws.include_dividend_declaration,
                ws.include_dividend_record,
                ws.include_dividend_payment,
                ws.include_stock_split,
                ws.reminder_before,
                ws.updated_at AS settings_updated_at,
                (SELECT COUNT(*) FROM follows f WHERE f.watchlist_id = w.id) AS stock_count
            FROM watchlists w
            LEFT JOIN watchlist_settings ws ON w.id = ws.watchlist_id
            WHERE w.id = :watchlist_id AND w.user_id = :user_id
        """
        try:
            results = self.db.execute_query(
                query=query,
                params={'watchlist_id': watchlist_id, 'user_id': user_id},
            )
            results_list = list(results)
            return dict(results_list[0]) if results_list else None
        except Exception as exc:
            raise Exception(f'Failed to fetch watchlist: {str(exc)}') from exc

    def get_watchlist_stocks(self, *, user_id: int, watchlist_id: UUID) -> List[Dict[str, Any]]:
        '''
        Get all stocks tracked by a watchlist.

        Returns:
            List of stock dicts with follow timestamps.

        Raises:
            ValueError: If watchlist not found or access denied.
            Exception: If fetch fails.
        '''
        watchlist = self.get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
        if not watchlist:
            raise ValueError('Watchlist not found or access denied.')

        query = """
            SELECT s.ticker, s.name, s.last_updated, f.created_at AS followed_at
            FROM follows f
            JOIN stocks s ON f.stock_ticker = s.ticker
            WHERE f.watchlist_id = :watchlist_id
            ORDER BY f.created_at DESC
        """

        try:
            results = self.db.execute_query(
                query=query,
                params={'watchlist_id': watchlist_id},
            )
            return [dict(row) for row in results]
        except Exception as exc:
            raise Exception(f'Failed to fetch watchlist stocks: {str(exc)}') from exc

    def update_watchlist(
        self,
        *,
        user_id: int,
        watchlist_id: UUID,
        name: Optional[str] = None,
        watchlist_settings: Optional[Dict[EventType, bool]] = None,
    ) -> bool:
        '''
        Update watchlist name and/or settings.

        Returns:
            True if updated, False if watchlist not found.
        
        Raises:
            ValueError: If name is empty.
            Exception: If update fails.
        '''
        if name is not None and not name:
            raise ValueError('Watchlist name must not be empty.')

        existing = self.get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
        if not existing:
            return False

        updated = False

        if name is not None:
            update_watchlist_query = """
                UPDATE watchlists
                SET name = :name
                WHERE id = :watchlist_id AND user_id = :user_id
            """
            rows = self.db.execute_update(
                query=update_watchlist_query,
                params={'name': name, 'watchlist_id': watchlist_id, 'user_id': user_id},
            )
            updated = updated or rows > 0

        if watchlist_settings:
            update_fields = []
            params: Dict[str, Any] = {'watchlist_id': watchlist_id}
            for event_type, enabled in watchlist_settings.items():
                column_name = event_type.db_column
                update_fields.append(f'{column_name} = :{column_name}')
                params[column_name] = bool(enabled)

            if update_fields:
                update_settings_query = f"""
                    UPDATE watchlist_settings
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE watchlist_id = :watchlist_id
                """
                rows = self.db.execute_update(
                    query=update_settings_query,
                    params=params,
                )
                updated = updated or rows > 0

        return updated

    def add_stock_to_watchlist(self, *, user_id: int, watchlist_id: UUID, stock_ticker: str) -> bool:
        '''
        Add a stock to a watchlist.

        Returns:
            True if added successfully.

        Raises:
            ValueError: If ticker is empty.
            LookupError: If watchlist or stock not found.
            Exception: If add fails.
        '''
        if not stock_ticker or not stock_ticker.strip():
            raise ValueError('Stock ticker must not be empty.')

        normalized_ticker = stock_ticker.strip().upper()

        watchlist = self.get_watchlist_by_id(watchlist_id=watchlist_id, user_id=user_id)
        if not watchlist:
            raise LookupError(f'Watchlist {watchlist_id} not found or access denied.')

        try:
            stock = self.stocks_service.get_stock_from_ticker(ticker=normalized_ticker)
        except Exception as exc:
            raise LookupError(f'Stock {normalized_ticker} not found.') from exc

        ticker = stock.symbol

        query = """
            INSERT INTO follows (watchlist_id, stock_ticker)
            VALUES (:watchlist_id, :ticker)
            ON CONFLICT (watchlist_id, stock_ticker) DO NOTHING
        """

        try:
            self.db.execute_update(
                query=query,
                params={'watchlist_id': watchlist_id, 'ticker': ticker.upper()},
            )
            return True
        except Exception as exc:
            raise Exception(f'Failed to add stock to watchlist: {str(exc)}') from exc

    def delete_watchlist(self, *, user_id: int, watchlist_id: UUID) -> bool:
        '''
        Delete a watchlist.

        Returns:
            True if deleted, False if not found.

        Raises:
            Exception: If deletion fails.
        '''
        query = """
            DELETE FROM watchlists
            WHERE id = :watchlist_id AND user_id = :user_id
        """

        try:
            rows_affected = self.db.execute_update(
                query=query,
                params={'watchlist_id': watchlist_id, 'user_id': user_id},
            )
            return rows_affected > 0
        except Exception as exc:
            raise Exception(f'Failed to delete watchlist: {str(exc)}') from exc

    def remove_stock_to_watchlist(self, *, user_id: int, watchlist_id: UUID, stock_ticker: str) -> bool:
        '''
        Remove a stock from a watchlist.

        Returns:
            True if removed, False if stock not in watchlist.

        Raises:
            ValueError: If ticker is empty.
            LookupError: If watchlist not found or access denied.
            Exception: If removal fails.
        '''
        if not stock_ticker or not stock_ticker.strip():
            raise ValueError('Stock ticker must not be empty.')

        normalized_ticker = stock_ticker.strip().upper()

        watchlist = self.get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
        if not watchlist:
            raise LookupError(f'Watchlist {watchlist_id} not found or access denied.')

        query = """
            DELETE FROM follows
            WHERE watchlist_id = :watchlist_id AND stock_ticker = :ticker
        """

        try:
            rows_affected = self.db.execute_update(
                query=query,
                params={'watchlist_id': watchlist_id, 'ticker': normalized_ticker},
            )
            return rows_affected > 0
        except Exception as exc:
            raise Exception(f'Failed to remove stock from watchlist: {str(exc)}') from exc
