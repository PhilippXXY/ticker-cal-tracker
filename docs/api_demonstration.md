## API Demonstration

This guide demonstrates how to use the API to create a watchlist and subscribe to its calendar feed.
You can follow along using curl commands or try the interactive [Swagger UI](https://ticker-cal-tracker-1052233055044.europe-west2.run.app/docs).

### Log In
First, authenticate to get an access token.
In this case we use a demo user with username `demo` and password `demo`.

Send a POST request to `api/auth/login` with these credentials:
```
curl -X 'POST' \
  'https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "demo",
  "password": "demo"
}'
```

The response includes an `access_token` that you'll need to include in the `Authorization` header for subsequent requests.

### Create Watchlist

Now create a watchlist to organize your stocks.
For this demo, we'll create one called `FAANG Stocks` for Meta (Facebook), Apple, Amazon, Netflix, and Alphabet (Google).

We'll configure it to display all event types: `Earnings`, `Dividends`, and `Stock Splits`.

Send a POST request to `api/watchlists/`:
```
curl -X 'POST' \
  'https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/watchlists/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer ***' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "FAANG Stocks",
  "include_earnings_announcement": true,
  "include_dividend_ex": true,
  "include_dividend_declaration": true,
  "include_dividend_record": true,
  "include_dividend_payment": true,
  "include_stock_split": true
}'
```

The API returns a 201 status with the watchlist details:
```
{
  "created_at": "2025-12-12T10:42:31.123426+00:00",
  "id": "76ad0a4e-81a0-4968-8a43-d23185274d3b",
  "include_dividend_declaration": true,
  "include_dividend_ex": true,
  "include_dividend_payment": true,
  "include_dividend_record": true,
  "include_earnings_announcement": true,
  "include_stock_split": true,
  "name": "FAANG Stocks"
}
```

Save the `id` value - you'll need it to add stocks and retrieve the calendar URL.

### Add Stocks to Watchlist

Now add the FAANG stocks to your watchlist.
The `api/watchlists/{watchlist_id}/stocks/{stock_ticker}` endpoint adds one stock at a time, so repeat this process for each ticker.

Here's an example adding Meta (META):
```
curl -X 'POST' \
  'https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/watchlists/76ad0a4e-81a0-4968-8a43-d23185274d3b/stocks/META' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer ***' \
  -d ''
```

After adding all five stocks (META, AAPL, AMZN, NFLX, GOOGL), verify them with a GET request to `api/watchlists/{watchlist_id}/stocks`:
```
https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/watchlists/76ad0a4e-81a0-4968-8a43-d23185274d3b/stocks
```

You should see all five stocks with their full names:
```
[
  {
    "name": "Alphabet, Inc.",
    "ticker": "GOOGL"
  },
  {
    "name": "Netflix, Inc.",
    "ticker": "NFLX"
  },
  {
    "name": "Amazon.com, Inc.",
    "ticker": "AMZN"
  },
  {
    "name": "Apple Inc.",
    "ticker": "AAPL"
  },
  {
    "name": "Meta Platforms, Inc.",
    "ticker": "META"
  }
]
```

### Get Calendar URL

Retrieve the calendar feed URL for your watchlist using the `api/cal/{watchlist_id}` endpoint:
```
https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/cal/76ad0a4e-81a0-4968-8a43-d23185274d3b
```

The response includes the calendar URL and its token:
```
{
  "calendar_url": "https://ticker-cal-tracker-1052233055044.europe-west2.run.app/api/cal/PA9iHoKQGwq7otzZXmLR2oSvZnof7AHjqfN0WIp9hx8.ics",
  "token": "PA9iHoKQGwq7otzZXmLR2oSvZnof7AHjqfN0WIp9hx8"
}
```

### Subscribe to the Calendar

Use the `calendar_url` to add the feed as a subscription to your calendar app.
Your calendar client will periodically fetch updates from `api/cal/{token}.ics` and display the events.

Here's what the calendar looks like for January 2026 with this watchlist:

![Calendar Demo Watchlist FAANG](img/calendar_demo_watchlist_faang.png)

Since none of these companies have declared dividend dates or stock splits for January 2026, only earnings announcements are displayed.