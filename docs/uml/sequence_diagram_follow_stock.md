# Follow Stock

This diagram shows the process of adding a stock to a watchlist. The system verifies watchlist ownership, fetches stock information from external APIs if not cached, stores stock events, and creates the follow relationship.

```puml
@startuml sequence_diagram_follow_stock
title Follow Stock - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as WSVC
participant "StocksService" as SSVC
participant "ExternalApiFacade" as EXT
database "SQL Database" as DB

User -> REST: POST /api/watchlists/{watchlist_id}/stocks\n{ ticker: "AAPL" }

== Authentication & Validation ==
REST -> REST: auth_utils.get_current_user_id()
REST -> REST: Validate payload

== Add Stock to Watchlist ==
REST -> WSVC: add_stock_to_watchlist(\n  user_id,\n  watchlist_id,\n  stock_ticker)

WSVC -> WSVC: Normalize ticker to uppercase

== Verify Watchlist Access ==
WSVC -> WSVC: get_watchlist_by_id(watchlist_id, user_id)
WSVC -> DB: SELECT w.*, ws.*\nFROM watchlists w\nWHERE w.id = :watchlist_id\nAND w.user_id = :user_id
DB --> WSVC: watchlist or None

alt watchlist not found
  WSVC --> REST: LookupError
  REST --> User: 404 Not Found
end

== Get or Fetch Stock ==
WSVC -> SSVC: get_stock_from_ticker(ticker)

== Check Local Cache ==
SSVC -> DB: SELECT ticker, name, last_updated\nFROM stocks\nWHERE ticker = :ticker
DB --> SSVC: stock data or None

alt stock not in cache
  == Fetch from External API ==
  SSVC -> EXT: getStockInfoFromSymbol(symbol)
  EXT --> SSVC: Stock(name, symbol, last_updated)
  
  == Cache Stock Data ==
  SSVC -> DB: INSERT INTO stocks\n(ticker, name, last_updated)\nVALUES (:ticker, :name, :last_updated)\nON CONFLICT (ticker) DO UPDATE
  DB --> SSVC: Success
  
  == Fetch Stock Events ==
  SSVC -> EXT: getStockEventDatesFromStock(\n  stock,\n  event_types=[all EventTypes])
  EXT --> SSVC: List[StockEvent]
  
  == Cache Stock Events ==
  loop for each event
    SSVC -> DB: INSERT INTO stock_events\n(stock_ticker, type, event_date, last_updated, source)\nVALUES (...)\nON CONFLICT (id) DO UPDATE
  end
end

SSVC --> WSVC: Stock

== Create Follow Relationship ==
WSVC -> DB: INSERT INTO follows\n(watchlist_id, stock_ticker)\nVALUES (:watchlist_id, :ticker)\nON CONFLICT DO NOTHING
DB --> WSVC: Success

WSVC --> REST: True
REST --> User: 201 Created\n{ message: "Successfully added stock" }

@enduml
```
