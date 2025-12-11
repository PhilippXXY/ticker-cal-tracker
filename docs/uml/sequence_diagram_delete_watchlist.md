# Delete Watchlist

This diagram shows the process of deleting a watchlist owned by a user. The system uses cascade deletion to automatically remove associated watchlist settings and stock follows.

```puml
@startuml sequence_diagram_delete_watchlist
title Delete Watchlist - Sequence Diagram

actor User
participant "WatchlistsREST" as REST
participant "WatchlistService" as SVC
database "SQL Database" as DB

User -> REST: DELETE /api/watchlists/{watchlist_id}

== Authentication & Validation ==
REST -> REST: auth_utils.get_current_user_id()

== Delete Watchlist ==
REST -> SVC: delete_watchlist(\n  user_id,\n  watchlist_id)

== Delete with Cascade ==
SVC -> DB: DELETE FROM watchlists\nWHERE id = :watchlist_id\nAND user_id = :user_id
note right
  ON DELETE CASCADE will automatically:
  - Delete from watchlist_settings
  - Delete from follows
end note
DB --> SVC: rows_affected

alt rows_affected > 0
  SVC --> REST: True
  REST --> User: 204 No Content
else no rows deleted
  SVC --> REST: False
  REST --> User: 404 Not Found
end

@enduml
```
