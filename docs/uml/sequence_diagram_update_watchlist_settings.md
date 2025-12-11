# Update Watchlist Settings

This diagram illustrates updating a watchlist's name and event type preferences (earnings, dividends, stock splits). The system validates ownership, updates both the watchlist name and settings, then returns the complete updated watchlist.

```puml
@startuml sequence_diagram_update_watchlist_settings
title Update Watchlist Settings - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: PUT /api/watchlists/{watchlist_id}\n{\n  name: "Tech Stocks",\n  include_earnings_announcement: true,\n  include_dividend_ex: false\n}

== Authentication & Validation ==
REST -> REST: auth_utils.get_current_user_id()
REST -> REST: Validate payload
REST -> REST: _extract_watchlist_settings(payload)

== Update Watchlist ==
REST -> SVC: update_watchlist(\n  user_id,\n  watchlist_id,\n  name,\n  watchlist_settings)

== Verify Watchlist Exists ==
SVC -> SVC: get_watchlist_by_id(user_id, watchlist_id)
SVC -> DB: SELECT w.*, ws.*\nFROM watchlists w\nWHERE w.id = :watchlist_id\nAND w.user_id = :user_id
DB --> SVC: existing watchlist or None

alt watchlist not found
  SVC --> REST: False
  REST --> User: 404 Not Found
end

== Update Watchlist Name (if provided) ==
alt name is not None
  SVC -> DB: UPDATE watchlists\nSET name = :name\nWHERE id = :watchlist_id\nAND user_id = :user_id
  DB --> SVC: rows affected
end

== Update Watchlist Settings (if provided) ==
alt watchlist_settings is not None
  SVC -> DB: UPDATE watchlist_settings\nSET include_earnings_announcement = :value1,\n    include_dividend_ex = :value2,\n    ...,\n    updated_at = CURRENT_TIMESTAMP\nWHERE watchlist_id = :watchlist_id
  DB --> SVC: rows affected
end

SVC --> REST: True
REST -> SVC: get_watchlist_by_id(user_id, watchlist_id)
SVC -> DB: SELECT w.*, ws.*...
DB --> SVC: updated watchlist
SVC --> REST: watchlist dict
REST --> User: 200 OK\n{ id, name, settings... }

@enduml
```
