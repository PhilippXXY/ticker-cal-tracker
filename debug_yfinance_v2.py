import yfinance as yf
import pandas as pd
import traceback
import requests_cache

print("--- YFinance Debug V3 (Session Fix) ---")
try:
    symbol = "AAPL"
    print(f"Fetching history for {symbol}...")
    
    # Create persistent session with browser-like user agent
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    
    # Pass session to Ticker (Wait, Ticker doesn't accept session directly in all versions)
    # The modern way is to rely on yfinance's internal handling or override.
    # Actually, yfinance 0.2.x handles headers better usually.
    # Let's try explicitly setting it via a hack or standard way if available.
    
    # Standard way doesn't easily expose session.
    # Let's try just standard instantiation again but maybe with a different symbol or longer timeout implicit?
    # No, let's try overriding the requests.get found in yfinance... no that's too hacky.
    
    # Trying the 'requests' library override which some suggest.
    # But first, let's just try to fetch a different ticker to rule out AAPL specific issue.
    # And print the version.
    print(f"YFinance Version: {yf.__version__}")
    
    msft = yf.Ticker("MSFT")
    hist = msft.history(period="1d")
    print("\nMSFT History:")
    print(hist)
    
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    traceback.print_exc()

print("--- End Debug ---")
