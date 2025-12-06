import yfinance as yf
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.external.external_base import ExternalApiBaseDefinition
from src.models.stock_model import Stock
from src.models.stock_event_model import StockEvent, EventType

logger = logging.getLogger(__name__)

class Finnhub(ExternalApiBaseDefinition):
    '''
    Real stock data implementation using yfinance (Yahoo Finance).
    Provides free, real-time (15-min delayed) stock quotes and historical data.
    '''
    
    def __init__(self):
        '''
        Initialize yfinance client.
        No API key needed - completely free!
        '''
        logger.info("Initialized yfinance (Yahoo Finance) for stock data")

    def get_quote(self, *, symbol: str) -> Optional[Dict[str, Any]]:
        '''
        Get real-time quote data from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            Dict with Finnhub-compatible format:
            {
                'c': current_price,
                'd': change_dollars,
                'dp': change_percent,
                'h': high,
                'l': low,
                'o': open,
                'pc': previous_close,
                't': timestamp
            }
            Returns None if data cannot be fetched.
        '''
        try:
            # Fetch stock data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price (try multiple fields for compatibility)
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or
                info.get('ask') or
                info.get('bid')
            )
            
            # Get previous close
            previous_close = (
                info.get('previousClose') or 
                info.get('regularMarketPreviousClose')
            )
            
            # Validate we have the essential data
            if not current_price or not previous_close:
                logger.warning(f"Missing price data for {symbol}: current={current_price}, previous={previous_close}")
                return None
            
            # Calculate change
            change_dollars = current_price - previous_close
            change_percent = (change_dollars / previous_close) * 100
            
            # Get high/low/open (with fallbacks)
            day_high = info.get('dayHigh') or info.get('regularMarketDayHigh') or current_price
            day_low = info.get('dayLow') or info.get('regularMarketDayLow') or current_price
            open_price = info.get('open') or info.get('regularMarketOpen') or current_price
            
            # Return Finnhub-compatible format
            result = {
                'c': round(float(current_price), 2),           # Current price
                'd': round(float(change_dollars), 2),          # Change in dollars
                'dp': round(float(change_percent), 2),         # Change in percent
                'h': round(float(day_high), 2),                # High
                'l': round(float(day_low), 2),                 # Low
                'o': round(float(open_price), 2),              # Open
                'pc': round(float(previous_close), 2),         # Previous close
                't': int(datetime.now(timezone.utc).timestamp())  # Timestamp
            }
            
            logger.debug(f"Fetched quote for {symbol}: ${result['c']} ({result['dp']:+.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            return None

    def getStockInfoFromSymbol(self, *, symbol: str) -> Stock:
        '''
        Get stock information by ticker symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Stock object with name, symbol, and last_updated
            
        Raises:
            ValueError: If stock symbol is invalid or not found
        '''
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get company name (try multiple fields)
            name = (
                info.get('longName') or 
                info.get('shortName') or 
                info.get('name') or
                symbol
            )
            
            # Validate we got some data
            if not info or len(info) < 5:
                raise ValueError(f"No data found for symbol {symbol}")
            
            return Stock(
                name=name,
                symbol=symbol.upper(),
                last_updated=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            raise ValueError(f"Stock {symbol} not found: {e}")

    def getStockInfoFromName(self, *, name: str) -> Stock:
        '''
        Get stock information by company name.
        
        Note: yfinance doesn't support name-based search well.
        This is a simplified implementation that won't work for all cases.
        Consider using Alpha Vantage for name-based searches.
        
        Args:
            name: Company name
            
        Returns:
            Stock object
            
        Raises:
            NotImplementedError: Name search not well supported by yfinance
        '''
        # yfinance doesn't have a good name search API
        # You could implement a mapping or use a different service
        raise NotImplementedError(
            "Name-based stock search is not supported with yfinance. "
            "Please use ticker symbols instead, or implement Alpha Vantage for this feature."
        )

    def getStockEventDatesFromStock(self, *, stock: Stock, event_types: List[EventType]) -> List[StockEvent]:
        '''
        Get stock events (dividends, splits) from Yahoo Finance.
        
        Note: Earnings announcements are not available through yfinance.
        Consider using Alpha Vantage for earnings data.
        
        Args:
            stock: Stock object to get events for
            event_types: List of EventType enums to fetch
            
        Returns:
            List of StockEvent objects
        '''
        events = []
        
        try:
            ticker = yf.Ticker(stock.symbol)
            
            # Get dividends
            dividend_types = [
                EventType.DIVIDEND_EX,
                EventType.DIVIDEND_DECLARATION,
                EventType.DIVIDEND_RECORD,
                EventType.DIVIDEND_PAYMENT
            ]
            
            if any(et in event_types for et in dividend_types):
                try:
                    dividends = ticker.dividends
                    if not dividends.empty:
                        # yfinance provides dividend payment dates
                        for date, amount in dividends.items():
                            if EventType.DIVIDEND_PAYMENT in event_types:
                                events.append(StockEvent(
                                    stock=stock,
                                    type=EventType.DIVIDEND_PAYMENT,
                                    date=date.to_pydatetime(),
                                    last_updated=datetime.now(timezone.utc),
                                    source='yfinance'
                                ))
                except Exception as e:
                    logger.warning(f"Failed to fetch dividends for {stock.symbol}: {e}")
            
            # Get stock splits
            if EventType.STOCK_SPLIT in event_types:
                try:
                    splits = ticker.splits
                    if not splits.empty:
                        for date, ratio in splits.items():
                            events.append(StockEvent(
                                stock=stock,
                                type=EventType.STOCK_SPLIT,
                                date=date.to_pydatetime(),
                                last_updated=datetime.now(timezone.utc),
                                source='yfinance'
                            ))
                except Exception as e:
                    logger.warning(f"Failed to fetch splits for {stock.symbol}: {e}")
            
            # Note: Earnings announcements not available in yfinance
            if EventType.EARNINGS_ANNOUNCEMENT in event_types:
                logger.info(
                    f"Earnings announcements requested for {stock.symbol} but not available in yfinance. "
                    "Consider using Alpha Vantage for earnings data."
                )
            
        except Exception as e:
            logger.error(f"Failed to fetch events for {stock.symbol}: {e}")
        
        return events
