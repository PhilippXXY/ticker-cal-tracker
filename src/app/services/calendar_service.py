from typing import List, Optional
from datetime import timedelta
from src.database.adapter_factory import DatabaseAdapterFactory
from src.models.stock_event_model import StockEvent, EventType
from src.models.stock_model import Stock
import src.app.utils.calendar_utils as calendar_utils

class CalendarService:
    
    def __init__(self) -> None:
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
