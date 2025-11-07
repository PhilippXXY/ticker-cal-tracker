import logging
from datetime import datetime, timezone, timedelta
from src.database.adapter_factory import DatabaseAdapterFactory
from src.app.services.stocks_service import StocksService
from src.models.stock_model import Stock
from src.models.stock_event_model import EventType

logger = logging.getLogger(__name__)

def update_stale_stock_events():
    '''
    Background task to update stock events for stocks that haven't been updated in the last week.
    
    This task:
    1. Queries the database for stocks with last_updated older than 7 days
    2. Calls upsert_stock_events for each stale stock
    3. Logs progress and any errors encountered
    
    Runs daily at 23:00 UTC as scheduled by the TaskScheduler.
    '''
    logger.info("Starting scheduled update of stale stock events")
    
    try:
        db = DatabaseAdapterFactory.get_instance()
        stocks_service = StocksService()
        
        # Calculate the cutoff date (7 days ago)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Query for stocks that haven't been updated in the last week
        query = """
            SELECT ticker, name, last_updated
            FROM stocks
            WHERE last_updated < :cutoff_date
            ORDER BY last_updated ASC
        """
        
        results = list(db.execute_query(
            query=query,
            params={'cutoff_date': cutoff_date},
        ))
        
        total_stocks = len(results)
        logger.info(f"Found {total_stocks} stocks to update (last updated before {cutoff_date.isoformat()})")
        
        if total_stocks == 0:
            logger.info("No stale stocks found. Task completed.")
            return
        
        # Process each stale stock
        success_count = 0
        error_count = 0
        
        for idx, record in enumerate(results, 1):
            ticker = record['ticker']
            
            try:
                # Parse last_updated timestamp
                last_updated = record.get('last_updated')
                if isinstance(last_updated, str):
                    try:
                        last_updated = datetime.fromisoformat(last_updated)
                    except ValueError:
                        last_updated = datetime.now(timezone.utc)
                elif not isinstance(last_updated, datetime):
                    last_updated = datetime.now(timezone.utc)
                
                # Create Stock object
                stock = Stock(
                    name=record['name'],
                    symbol=ticker,
                    last_updated=last_updated,
                )
                
                # Update stock events for all event types
                event_types = list(EventType)
                stocks_service.upsert_stock_events(stock=stock, event_types=event_types)
                
                # Update the stock's last_updated timestamp
                update_query = """
                    UPDATE stocks
                    SET last_updated = :last_updated
                    WHERE ticker = :ticker
                """
                db.execute_update(
                    query=update_query,
                    params={
                        'ticker': ticker,
                        'last_updated': datetime.now(timezone.utc),
                    },
                )
                
                success_count += 1
                logger.info(f"[{idx}/{total_stocks}] Successfully updated events for {ticker}")
                
            except Exception as exc:
                error_count += 1
                logger.error(f"[{idx}/{total_stocks}] Failed to update events for {ticker}: {str(exc)}")
                # Continue with next stock even if one fails
                continue
        
        logger.info(
            f"Completed stale stock events update. "
            f"Success: {success_count}, Errors: {error_count}, Total: {total_stocks}"
        )
        
    except Exception as exc:
        logger.error(f"Critical error in update_stale_stock_events task: {str(exc)}")
        raise
