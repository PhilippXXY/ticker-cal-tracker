import yfinance as yf
print("Attempting to fetch AAPL ticker...")
try:
    ticker = yf.Ticker('AAPL')
    print("Ticker object created.")
    info = ticker.fast_info
    print(f"Fast Info accessed: {info}")
    print(f"LAST: {info.last_price}")
    print(f"PREV: {info.previous_close}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
