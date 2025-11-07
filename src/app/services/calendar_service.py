from typing import List, Optional
from datetime import timedelta
from uuid import UUID
from src.database.adapter_factory import DatabaseAdapterFactory
from src.models.stock_event_model import StockEvent, EventType
from src.models.stock_model import Stock
import src.app.utils.calendar_utils as calendar_utils

class CalendarService:
    '''
    Service for managing calendar operations and iCalendar file generation.
    
    Handles fetching stock events for watchlists and generating iCalendar (.ics) files,
    as well as managing calendar tokens for secure access.
    '''
    
    def __init__(self) -> None:
        '''
        Initialize the CalendarService with database connection.
        '''
        self.db = DatabaseAdapterFactory.get_instance()
    
    def get_calendar(self, *, token: str) -> str:
        '''
        Fetch and generate an iCalendar (.ics) file for a given watchlist calendar token.
        
        Args:
            token: The unique calendar token for the watchlist.
            
        Returns:
            str: Valid iCalendar (.ics) formatted string
        '''
        if not token or not token.strip():
            raise ValueError('Calendar token must not be empty.')
        
        normalized_token = token.strip()
        
        watchlist_query = """
        SELECT
            w.id,
            w.name,
            ws.reminder_before
        FROM watchlists w
        LEFT JOIN watchlist_settings ws ON w.id = ws.watchlist_id
        WHERE w.calendar_token = :token
        """
        
        watchlist_rows = list(self.db.execute_query(query=watchlist_query, params={'token': normalized_token}))
        if not watchlist_rows:
            raise LookupError('Watchlist not found for the provided calendar token.')
        
        watchlist = dict(watchlist_rows[0])
        watchlist_id = watchlist['id']
        watchlist_name = watchlist.get('name') or 'Stock Events'
        reminder_before: Optional[timedelta] = watchlist.get('reminder_before')
        
        # Query to fetch stock events for the watchlist, filtered by watchlist settings
        stock_event_query = """
        SELECT 
            s.ticker,
            s.name,
            s.last_updated as stock_last_updated,
            se.type,
            se.event_date,
            se.last_updated as event_last_updated,
            se.source
        FROM stock_events se
        INNER JOIN stocks s ON se.stock_ticker = s.ticker
        INNER JOIN follows f ON s.ticker = f.stock_ticker
        INNER JOIN watchlists w ON f.watchlist_id = w.id
        INNER JOIN watchlist_settings ws ON w.id = ws.watchlist_id
        WHERE w.id = :watchlist_id
        AND (
            (se.type = 'EARNINGS_ANNOUNCEMENT' AND ws.include_earnings_announcement = TRUE) OR
            (se.type = 'DIVIDEND_EX' AND ws.include_dividend_ex = TRUE) OR
            (se.type = 'DIVIDEND_DECLARATION' AND ws.include_dividend_declaration = TRUE) OR
            (se.type = 'DIVIDEND_RECORD' AND ws.include_dividend_record = TRUE) OR
            (se.type = 'DIVIDEND_PAYMENT' AND ws.include_dividend_payment = TRUE) OR
            (se.type = 'STOCK_SPLIT' AND ws.include_stock_split = TRUE)
        )
        ORDER BY se.event_date ASC
        """
        
        results = self.db.execute_query(query=stock_event_query, params={"watchlist_id": watchlist_id})
        
        # Convert database results to StockEvent objects
        stock_events: List[StockEvent] = []
        
        for row in results:
            # Create Stock object
            stock = Stock(
                name=row['name'],
                symbol=row['ticker'],
                last_updated=row['stock_last_updated']
            )
            
            # Create StockEvent object
            stock_event = StockEvent(
                stock=stock,
                type=EventType(row['type']),
                date=row['event_date'],
                last_updated=row['event_last_updated'],
                source=row['source']
            )
            
            stock_events.append(stock_event)
        
        # Generate the iCalendar file
        ics_content = calendar_utils.build_ics(
            stock_events=stock_events,
            watchlist_name=watchlist_name,
            reminder_before=reminder_before
        )

        return ics_content

    def rotate_calendar_token(self, *, user_id: UUID, watchlist_id: UUID) -> str:
        '''
        Generate and update a new calendar token for a watchlist.
        
        Args:
            user_id: The ID of the user who owns the watchlist.
            watchlist_id: The ID of the watchlist to rotate the token for.
            
        Returns:
            str: The newly generated calendar token.
            
        Raises:
            ValueError: If user_id or watchlist_id are invalid.
            LookupError: If the watchlist doesn't exist or doesn't belong to the user.
        '''
        if not isinstance(user_id, UUID):
            raise ValueError('user_id must be a UUID instance.')
        if not isinstance(watchlist_id, UUID):
            raise ValueError('watchlist_id must be a UUID instance.')
        
        # Generate a new token
        new_token = calendar_utils.generate_calendar_token()
        
        # Update the watchlist with the new token, but only if it belongs to the user
        update_query = """
        UPDATE watchlists
        SET calendar_token = :new_token
        WHERE id = :watchlist_id AND user_id = :user_id
        RETURNING calendar_token
        """
        
        result = list(self.db.execute_query(
            query=update_query,
            params={
                'new_token': new_token,
                'watchlist_id': watchlist_id,
                'user_id': user_id
            }
        ))
        
        if not result:
            raise LookupError('Watchlist not found or does not belong to the user.')
        
        return new_token
    
    def get_calendar_token(self, *, user_id: UUID, watchlist_id: UUID) -> str:
        '''
        Retrieve the calendar token for a watchlist.
        
        Args:
            user_id: The ID of the user who owns the watchlist.
            watchlist_id: The ID of the watchlist to get the token for.
            
        Returns:
            str: The calendar token for the watchlist.
            
        Raises:
            ValueError: If user_id or watchlist_id are invalid.
            LookupError: If the watchlist doesn't exist or doesn't belong to the user.
        '''
        if not isinstance(user_id, UUID):
            raise ValueError('user_id must be a UUID instance.')
        if not isinstance(watchlist_id, UUID):
            raise ValueError('watchlist_id must be a UUID instance.')
        
        # Query the watchlist to get the calendar token
        query = """
        SELECT calendar_token
        FROM watchlists
        WHERE id = :watchlist_id AND user_id = :user_id
        """
        
        result = list(self.db.execute_query(
            query=query,
            params={
                'watchlist_id': watchlist_id,
                'user_id': user_id
            }
        ))
        
        if not result:
            raise LookupError('Watchlist not found or does not belong to the user.')
        
        return result[0]['calendar_token']
