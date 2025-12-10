import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.app.background.tasks import update_stale_stock_events

logger = logging.getLogger(__name__)

class TaskScheduler:
    '''
    Manages scheduled background tasks for the application.
    
    This class handles the initialization and lifecycle of scheduled jobs,
    including daily stock event updates.
    '''
    
    def __init__(self):
        '''
        Initialize the background scheduler.
        '''
        self.scheduler = BackgroundScheduler(timezone='UTC')
        
    def start(self):
        '''
        Start the scheduler and register all scheduled tasks.
        '''
        # Schedule daily stock events update at 23:00 UTC
        self.scheduler.add_job(
            func=update_stale_stock_events,
            trigger=CronTrigger(hour=23, minute=0, timezone='UTC'),
            id='update_stale_stock_events',
            name='Update stale stock events',
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Background scheduler started successfully")
        logger.info("Scheduled job: update_stale_stock_events (daily at 23:00 UTC)")
        
    def shutdown(self):
        '''
        Gracefully shutdown the scheduler.
        '''
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Background scheduler shut down successfully")
