-- Seed data for development and testing
-- This provides sample data to test the application

-- Insert sample users (passwords are hashed versions of 'password123' using werkzeug)
INSERT INTO users (username, email, password_hash) VALUES
    ('alice', 'alice@example.com', 'scrypt:32768:8:1$KsYwG2T0vSt2U4cJ$d1ac8c1567def3d3f29f6a9f4352917ddeb52da4fb3f09610fd12f33edfd35b87e868f501751a932c2336b2ec38e039947a0a921e3b497a11717eadcdeb626a8'),
    ('bob', 'bob@example.com', 'scrypt:32768:8:1$KsYwG2T0vSt2U4cJ$d1ac8c1567def3d3f29f6a9f4352917ddeb52da4fb3f09610fd12f33edfd35b87e868f501751a932c2336b2ec38e039947a0a921e3b497a11717eadcdeb626a8'),
    ('charlie', 'charlie@example.com', 'scrypt:32768:8:1$KsYwG2T0vSt2U4cJ$d1ac8c1567def3d3f29f6a9f4352917ddeb52da4fb3f09610fd12f33edfd35b87e868f501751a932c2336b2ec38e039947a0a921e3b497a11717eadcdeb626a8');

-- Insert sample stocks
INSERT INTO stocks (ticker, name) VALUES
    ('AAPL', 'Apple Inc.'),
    ('MSFT', 'Microsoft Corporation'),
    ('GOOGL', 'Alphabet Inc.'),
    ('AMZN', 'Amazon.com Inc.'),
    ('TSLA', 'Tesla Inc.'),
    ('META', 'Meta Platforms Inc.'),
    ('NVDA', 'NVIDIA Corporation'),
    ('JPM', 'JPMorgan Chase & Co.'),
    ('V', 'Visa Inc.'),
    ('WMT', 'Walmart Inc.');

-- Insert sample stock events (upcoming and recent)
INSERT INTO stock_events (stock_ticker, type, event_date, source) VALUES
    ('AAPL', 'EARNINGS_ANNOUNCEMENT', '2025-11-15', 'AlphaVantage'),
    ('AAPL', 'DIVIDEND_EX', '2025-11-08', 'AlphaVantage'),
    ('AAPL', 'DIVIDEND_PAYMENT', '2025-11-22', 'AlphaVantage'),
    ('MSFT', 'EARNINGS_ANNOUNCEMENT', '2025-11-20', 'Finnhub'),
    ('MSFT', 'DIVIDEND_EX', '2025-11-14', 'Finnhub'),
    ('MSFT', 'DIVIDEND_PAYMENT', '2025-12-08', 'Finnhub'),
    ('GOOGL', 'EARNINGS_ANNOUNCEMENT', '2025-11-12', 'AlphaVantage'),
    ('AMZN', 'EARNINGS_ANNOUNCEMENT', '2025-11-25', 'Finnhub'),
    ('TSLA', 'EARNINGS_ANNOUNCEMENT', '2025-11-18', 'AlphaVantage'),
    ('TSLA', 'STOCK_SPLIT', '2025-12-01', 'Finnhub'),
    ('META', 'EARNINGS_ANNOUNCEMENT', '2025-11-10', 'AlphaVantage'),
    ('META', 'DIVIDEND_DECLARATION', '2025-11-05', 'AlphaVantage'),
    ('NVDA', 'EARNINGS_ANNOUNCEMENT', '2025-11-22', 'Finnhub'),
    ('NVDA', 'DIVIDEND_EX', '2025-11-12', 'Finnhub'),
    ('JPM', 'DIVIDEND_EX', '2025-11-06', 'AlphaVantage'),
    ('JPM', 'DIVIDEND_RECORD', '2025-11-07', 'AlphaVantage'),
    ('JPM', 'DIVIDEND_PAYMENT', '2025-11-30', 'AlphaVantage'),
    ('V', 'EARNINGS_ANNOUNCEMENT', '2025-11-28', 'Finnhub'),
    ('V', 'DIVIDEND_EX', '2025-11-15', 'Finnhub'),
    ('WMT', 'EARNINGS_ANNOUNCEMENT', '2025-11-16', 'AlphaVantage'),
    ('WMT', 'DIVIDEND_EX', '2025-11-08', 'AlphaVantage');

INSERT INTO watchlists (user_id, name, calendar_token) VALUES
    (
        (SELECT id FROM users WHERE email = 'alice@example.com'),
        'Tech Stocks',
        'tech-stocks-' || md5(random()::text)
    ),
    (
        (SELECT id FROM users WHERE email = 'alice@example.com'),
        'Dividend Payers',
        'dividend-payers-' || md5(random()::text)
    ),
    (
        (SELECT id FROM users WHERE email = 'bob@example.com'),
        'Growth Portfolio',
        'growth-portfolio-' || md5(random()::text)
    ),
    (
        (SELECT id FROM users WHERE email = 'charlie@example.com'),
        'All Stocks',
        'all-stocks-' || md5(random()::text)
    );

-- Insert watchlist settings
INSERT INTO watchlist_settings (watchlist_id, reminder_before, include_dividend_ex, include_dividend_declaration, include_dividend_record, include_dividend_payment) VALUES
    (
        (SELECT id FROM watchlists WHERE name = 'Tech Stocks' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        '2 days'::INTERVAL,
        TRUE,
        TRUE,
        TRUE,
        TRUE
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        '1 day'::INTERVAL,
        TRUE,
        TRUE,
        TRUE,
        TRUE
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Growth Portfolio' AND user_id = (SELECT id FROM users WHERE email = 'bob@example.com')),
        '12 hours'::INTERVAL,
        FALSE,
        FALSE,
        FALSE,
        FALSE
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'All Stocks' AND user_id = (SELECT id FROM users WHERE email = 'charlie@example.com')),
        '1 day'::INTERVAL,
        TRUE,
        TRUE,
        TRUE,
        TRUE
    );

-- Insert follows (stocks in watchlists)
-- Alice's Tech Stocks watchlist
INSERT INTO follows (watchlist_id, stock_ticker) VALUES
    (
        (SELECT id FROM watchlists WHERE name = 'Tech Stocks' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'AAPL'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Tech Stocks' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'MSFT'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Tech Stocks' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'GOOGL'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Tech Stocks' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'NVDA'
    );

-- Alice's Dividend Payers watchlist
INSERT INTO follows (watchlist_id, stock_ticker) VALUES
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'AAPL'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'MSFT'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'JPM'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'V'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Dividend Payers' AND user_id = (SELECT id FROM users WHERE email = 'alice@example.com')),
        'WMT'
    );

-- Bob's Growth Portfolio
INSERT INTO follows (watchlist_id, stock_ticker) VALUES
    (
        (SELECT id FROM watchlists WHERE name = 'Growth Portfolio' AND user_id = (SELECT id FROM users WHERE email = 'bob@example.com')),
        'TSLA'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Growth Portfolio' AND user_id = (SELECT id FROM users WHERE email = 'bob@example.com')),
        'AMZN'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Growth Portfolio' AND user_id = (SELECT id FROM users WHERE email = 'bob@example.com')),
        'META'
    ),
    (
        (SELECT id FROM watchlists WHERE name = 'Growth Portfolio' AND user_id = (SELECT id FROM users WHERE email = 'bob@example.com')),
        'NVDA'
    );

-- Charlie's All Stocks watchlist
INSERT INTO follows (watchlist_id, stock_ticker)
SELECT 
    (SELECT id FROM watchlists WHERE name = 'All Stocks' AND user_id = (SELECT id FROM users WHERE email = 'charlie@example.com')),
    ticker
FROM stocks;
