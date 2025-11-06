-- Seed data for development and testing
-- This provides sample data to test the application

-- Insert sample users (passwords are hashed versions of 'password123')
INSERT INTO users (email, password) VALUES
    ('alice@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEuUhe'),
    ('bob@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEuUhe'),
    ('charlie@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEuUhe');

-- Insert user preferences for all users
INSERT INTO user_preferences (user_id, default_reminder_before)
SELECT id, '1 day'::INTERVAL FROM users;

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

-- Insert sample watchlists
INSERT INTO watchlists (user_id, name, calendar_url) VALUES
    (
        (SELECT id FROM users WHERE email = 'alice@example.com'),
        'Tech Stocks',
        'https://calendar.example.com/alice/tech-stocks-' || uuid_generate_v4()
    ),
    (
        (SELECT id FROM users WHERE email = 'alice@example.com'),
        'Dividend Payers',
        'https://calendar.example.com/alice/dividend-payers-' || uuid_generate_v4()
    ),
    (
        (SELECT id FROM users WHERE email = 'bob@example.com'),
        'Growth Portfolio',
        'https://calendar.example.com/bob/growth-portfolio-' || uuid_generate_v4()
    ),
    (
        (SELECT id FROM users WHERE email = 'charlie@example.com'),
        'All Stocks',
        'https://calendar.example.com/charlie/all-stocks-' || uuid_generate_v4()
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
