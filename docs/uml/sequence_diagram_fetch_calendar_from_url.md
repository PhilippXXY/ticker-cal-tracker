# Fetch Calendar from URL

This diagram shows how calendar clients retrieve a watchlist's stock events as an iCalendar (.ics) file using a unique token. The system fetches relevant stock events based on watchlist settings and generates a properly formatted iCalendar response.

```puml
@startuml sequence_diagram_fetch_calendar_from_url
title Fetch Calendar from URL - Sequence Diagram

participant "Calendar Client" as CAL
participant "CalendarREST" as REST
participant "CalendarService" as SVC
database "SQL Database" as DB

CAL -> REST: GET /api/calendar/{token}.ics

== Validate Token ==
REST -> REST: Validate token not empty

== Get Calendar ==
REST -> SVC: get_calendar(token)

== Lookup Watchlist by Token ==
SVC -> DB: SELECT w.id, w.name, ws.reminder_before\nFROM watchlists w\nLEFT JOIN watchlist_settings ws\nWHERE w.calendar_token = :token
DB --> SVC: watchlist data

alt watchlist not found
  SVC --> REST: LookupError
  REST --> CAL: 404 Not Found
end

== Fetch Stock Events ==
SVC -> DB: SELECT s.ticker, s.name, se.type, se.event_date, se.source\nFROM stock_events se\nJOIN stocks s ON se.stock_ticker = s.ticker\nJOIN follows f ON s.ticker = f.stock_ticker\nJOIN watchlists w ON f.watchlist_id = w.id\nJOIN watchlist_settings ws\nWHERE w.id = :watchlist_id\nAND event type matches settings
DB --> SVC: List of stock events

== Build iCalendar ==
SVC -> SVC: calendar_utils.build_ics(\n  stock_events,\n  watchlist_name,\n  reminder_before)

SVC --> REST: ics_content (VCALENDAR string)

== Return iCalendar File ==
REST --> CAL: 200 OK\nContent-Type: text/calendar\nContent-Disposition: attachment; filename="{token}.ics"\n\nBEGIN:VCALENDAR\n...\nEND:VCALENDAR

@enduml
```
