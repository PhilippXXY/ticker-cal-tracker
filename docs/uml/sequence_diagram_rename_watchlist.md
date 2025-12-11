# Rename Watchlist

This diagram shows how a user can rename an existing watchlist. The system verifies ownership, updates the watchlist name in the database, and returns the updated watchlist information.

```puml
@startuml sequence_diagram_rename_watchlist
title Rename Watchlist - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: PUT /api/watchlists/{watchlist_id}\n{ name: "Earnings Only" }

== Authentication & Validation ==
REST -> REST: auth_utils.get_current_user_id()
REST -> REST: Validate name not empty

== Update Watchlist ==
REST -> SVC: update_watchlist(\n  user_id,\n  watchlist_id,\n  name,\n  watchlist_settings=None)

== Verify Watchlist Exists ==
SVC -> SVC: get_watchlist_by_id(user_id, watchlist_id)
SVC -> DB: SELECT w.*, ws.*\nFROM watchlists w\nWHERE w.id = :watchlist_id\nAND w.user_id = :user_id
DB --> SVC: existing watchlist or None

alt watchlist not found
  SVC --> REST: False
  REST --> User: 404 Not Found
end

== Update Watchlist Name ==
SVC -> DB: UPDATE watchlists\nSET name = :name\nWHERE id = :watchlist_id\nAND user_id = :user_id
DB --> SVC: rows affected

SVC --> REST: True
REST -> SVC: get_watchlist_by_id(user_id, watchlist_id)
SVC -> DB: SELECT w.*, ws.*...
DB --> SVC: updated watchlist
SVC --> REST: watchlist dict
REST --> User: 200 OK\n{ id, name, calendar_token, settings... }

@enduml
```
