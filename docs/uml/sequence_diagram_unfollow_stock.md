# Unfollow Stock

This diagram illustrates removing a stock from a watchlist. The system verifies watchlist ownership, deletes the follow relationship, while keeping stock data cached for potential future use.

```puml
@startuml sequence_diagram_unfollow_stock
title Unfollow Stock - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: DELETE /api/watchlists/{watchlist_id}/stocks/{ticker}

== Authentication & Validation ==
REST -> REST: auth_utils.get_current_user_id()
REST -> REST: Validate ticker not empty

== Remove Stock from Watchlist ==
REST -> SVC: remove_stock_to_watchlist(\n  user_id,\n  watchlist_id,\n  stock_ticker)

SVC -> SVC: Normalize ticker to uppercase

== Verify Watchlist Access ==
SVC -> SVC: get_watchlist_by_id(watchlist_id, user_id)
SVC -> DB: SELECT w.*, ws.*\nFROM watchlists w\nWHERE w.id = :watchlist_id\nAND w.user_id = :user_id
DB --> SVC: watchlist or None

alt watchlist not found
  SVC --> REST: LookupError
  REST --> User: 404 Not Found
end

== Delete Follow Relationship ==
SVC -> DB: DELETE FROM follows\nWHERE watchlist_id = :watchlist_id\nAND stock_ticker = :ticker
DB --> SVC: rows_affected

note right
  Stock and stock_events remain in database
  for caching purposes. They may be reused
  if added to another watchlist later.
end note

alt rows_affected > 0
  SVC --> REST: True
  REST --> User: 204 No Content
else no rows deleted
  SVC --> REST: False
  REST --> User: 404 Not Found\n{ message: "Stock not in watchlist" }
end

@enduml
```
