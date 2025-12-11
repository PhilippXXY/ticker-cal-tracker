# Get Watchlist Follows

This diagram depicts retrieving all stocks that are followed by a specific watchlist. The system verifies watchlist ownership and returns stock information including ticker, name, and when each stock was added to the watchlist.

```puml
@startuml sequence_diagram_watchlist_follows
title Get Watchlist Follows - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: GET /api/watchlists/{watchlist_id}/stocks

== Authentication ==
REST -> REST: auth_utils.get_current_user_id()

== Get Watchlist Stocks ==
REST -> SVC: get_watchlist_stocks(\n  user_id,\n  watchlist_id)

== Verify Watchlist Access ==
SVC -> SVC: get_watchlist_by_id(user_id, watchlist_id)
SVC -> DB: SELECT w.*, ws.*\nFROM watchlists w\nWHERE w.id = :watchlist_id\nAND w.user_id = :user_id
DB --> SVC: watchlist or None

alt watchlist not found
  SVC --> REST: ValueError
  REST --> User: 404 Not Found\n{ message: "Watchlist not found or access denied" }
end

== Fetch Followed Stocks ==
SVC -> DB: SELECT s.ticker, s.name, s.last_updated,\n       f.created_at AS followed_at\nFROM follows f\nJOIN stocks s ON f.stock_ticker = s.ticker\nWHERE f.watchlist_id = :watchlist_id\nORDER BY f.created_at DESC

DB --> SVC: List of stock records

SVC --> REST: List[Dict] (stocks with follow timestamps)
REST --> User: 200 OK\n[\n  {\n    ticker,\n    name,\n    last_updated,\n    followed_at\n  }\n]

@enduml
```
