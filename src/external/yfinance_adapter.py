import logging
import yfinance as yf # type: ignore
import requests_cache
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class YFinanceAdapter:
    '''
    Adapter for fetching stock data from Yahoo Finance using the yfinance library.
    
    This provides a mechanism to get near real-time stock prices without an API key,
    serving as a robust fallback or primary source for basic price data.
    '''
    
    def __init__(self):
        '''Initialize with a simple session to avoid rate limits and blocking.'''
        self.session = None
        # Try simple headers first without cache complications
        # requests_cache can cause SQLite locking errors in Flask threaded env
        pass

    def getStockPrice(self, *, symbol: str) -> dict:
        '''
        Retrieve current stock price information.
        '''
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"Invalid symbol provided: {symbol}")
            
        try:
             # Manually construct Ticker to ensure headers if needed, 
             # but let's try strict defaults first or lightweight approach.
             # Debugging: Print to stdout to capture in server logs
             print(f"DEBUG: Fetching price for {symbol}")
             
             ticker = yf.Ticker(symbol)
             
             # history() is the proven method in debug script
             data = ticker.history(period="1d")
             
             if data.empty:
                 print(f"DEBUG: Empty data for {symbol}")
                 raise ValueError("No price data found (history empty)")

             # Get the last row
             last_quote = data.iloc[-1]
             print(f"DEBUG: Found data for {symbol}: {last_quote['Close']}")

             current_price = float(last_quote['Close'])
             open_price = float(last_quote['Open'])
             high_price = float(last_quote['High'])
             low_price = float(last_quote['Low'])
            
             # Previous close is trickier with just 1d history.
             # We can try to get 'previousClose' from ticker.info (metadata)
             # Or fetch 2d history.
            
             # Fetching 2 days to calculate change if current session is active/closed
             data_2d = ticker.history(period="5d") # 5d to be safe over weekends
            
             if len(data_2d) >= 2:
                 previous_close = float(data_2d.iloc[-2]['Close'])
             else:
                 # Fallback if we only have 1 day of data (e.g. IPO)
                 previous_close = open_price
                
             change = current_price - previous_close
             percent_change = (change / previous_close) * 100 if previous_close else 0
            
             return {
                 'c': current_price,
                 'd': change,
                 'dp': percent_change,
                 'h': high_price,
                 'l': low_price,
                 'o': open_price,
                 'pc': previous_close
             }
            
        except Exception as e:
            logger.error(f"yfinance lookup failed for symbol '{symbol}': {str(e)}")
            raise ValueError(f"Failed to fetch price data for {symbol} using yfinance: {str(e)}")
