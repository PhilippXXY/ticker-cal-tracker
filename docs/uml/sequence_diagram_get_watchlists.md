# Get Watchlists

This diagram depicts how the system retrieves all watchlists belonging to an authenticated user. It fetches watchlist data along with their associated settings and returns them sorted by creation date.

```puml
@startuml sequence_diagram_get_watchlists
title Get Watchlists - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: GET /api/watchlists

== Authentication ==
REST -> REST: auth_utils.get_current_user_id()

== Fetch User Watchlists ==
REST -> SVC: get_all_watchlists_for_user(user_id)

SVC -> DB: SELECT w.id, w.name, w.calendar_token, w.created_at,\n  ws.include_earnings_announcement,\n  ws.include_dividend_ex,\n  ws.include_dividend_declaration,\n  ws.include_dividend_record,\n  ws.include_dividend_payment,\n  ws.include_stock_split,\n  ws.reminder_before,\n  ws.updated_at\nFROM watchlists w\nLEFT JOIN watchlist_settings ws ON w.id = ws.watchlist_id\nWHERE w.user_id = :user_id\nORDER BY w.created_at DESC

DB --> SVC: List of watchlist records

SVC --> REST: List[Dict] (watchlists with settings)
REST --> User: 200 OK\n[\n  {\n    id, name, calendar_token,\n    include_earnings_announcement,\n    ...\n  }\n]

@enduml
```
