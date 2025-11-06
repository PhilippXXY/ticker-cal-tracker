
from datetime import datetime, timezone
from src.models.stock_model import Stock

class StocksService:
    
    def get_stock_from_ticker(self, *, ticker) -> Stock:
        # Should return the stock if found in db and otherwise fetch the external API and populate the db
        # TODO: Implement database lookup and external API fetching
        # For now, returning a mock Apple stock object
        return Stock(
            name="Apple Inc.",
            symbol="AAPL",
            last_updated=datetime.now(timezone.utc)
        )
        