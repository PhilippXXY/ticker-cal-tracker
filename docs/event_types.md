# Event Types

This section describes the event types supported by the **Stock Ticker Calendar Tracker**.

Event types define which categories of stock-related events are tracked for a watchlist and therefore appear in the generated calendar feed.

Each watchlist stores a set of boolean flags (one per event type). These flags are exposed via the watchlist REST API and are applied during calendar generation.

---

## Overview

An **event type** represents a specific category of market or company activity associated with a stock.  
When a watchlist has an event type enabled, the application will include matching events for all followed stocks in that watchlist.

Event types are represented in the codebase by the `EventType` enum and mapped to database columns (per-watchlist settings).

---

## Supported Event Types

The following table lists all supported event types and how they are represented in the system.

| Event Type (Enum)       | Meaning                             | Watchlist setting (API / DB column) |
| ----------------------- | ----------------------------------- | ----------------------------------- |
| `EARNINGS_ANNOUNCEMENT` | Track earnings announcement events. | `include_earnings_announcement`     |
| `DIVIDEND_EX`           | Track dividend ex-date events.      | `include_dividend_ex`               |
| `DIVIDEND_DECLARATION`  | Track dividend declaration events.  | `include_dividend_declaration`      |
| `DIVIDEND_RECORD`       | Track dividend record date events.  | `include_dividend_record`           |
| `DIVIDEND_PAYMENT`      | Track dividend payment date events. | `include_dividend_payment`          |
| `STOCK_SPLIT`           | Track stock split events.           | `include_stock_split`               |

---

## Default Behaviour

When creating a watchlist, all event types default to `true` unless explicitly overridden in the request payload.  
When updating a watchlist, each provided boolean field toggles the corresponding event type for that watchlist.

---

## Where Event Types Are Used

Event types affect the application in three main places:

1. **Watchlist settings**  
   Watchlist create/update payloads include the `include_*` boolean fields.

2. **Event retrieval**  
   The backend fetches stock events from the external data provider and stores them with a corresponding `EventType`.

3. **Calendar generation**  
   When generating an `.ics` calendar feed, the application filters stored events based on the watchlist settings and emits only the enabled event types.
