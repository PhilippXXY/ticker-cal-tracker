-- Ticker Calendar Tracker Database Schema
-- Generated from class_diagram_application.puml

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE event_type AS ENUM (
    'EARNINGS_ANNOUNCEMENT',
    'DIVIDEND_EX',
    'DIVIDEND_DECLARATION',
    'DIVIDEND_RECORD',
    'DIVIDEND_PAYMENT',
    'STOCK_SPLIT'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email
CREATE INDEX idx_users_email ON users(email);

-- Stocks table
CREATE TABLE stocks (
    ticker VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stock events table
CREATE TABLE stock_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_ticker VARCHAR(20) NOT NULL REFERENCES stocks(ticker) ON DELETE CASCADE,
    type event_type NOT NULL,
    event_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100)
);

-- Create indexes for stock events
CREATE INDEX idx_stock_events_ticker ON stock_events(stock_ticker);
CREATE INDEX idx_stock_events_date ON stock_events(event_date);
CREATE INDEX idx_stock_events_type ON stock_events(type);

-- User preferences table
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_reminder_before INTERVAL DEFAULT '1 day',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Watchlists table
CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    calendar_url VARCHAR(500) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id
CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);

-- Watchlist settings table
CREATE TABLE watchlist_settings (
    watchlist_id UUID PRIMARY KEY REFERENCES watchlists(id) ON DELETE CASCADE,
    include_earnings_announcement BOOLEAN DEFAULT TRUE,
    include_dividend_ex BOOLEAN DEFAULT TRUE,
    include_dividend_declaration BOOLEAN DEFAULT TRUE,
    include_dividend_record BOOLEAN DEFAULT TRUE,
    include_dividend_payment BOOLEAN DEFAULT TRUE,
    include_stock_split BOOLEAN DEFAULT TRUE,
    reminder_before INTERVAL DEFAULT '1 day',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Follows table (junction table for many-to-many relationship)
CREATE TABLE follows (
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    stock_ticker VARCHAR(20) NOT NULL REFERENCES stocks(ticker) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (watchlist_id, stock_ticker)
);

-- Create indexes for follows
CREATE INDEX idx_follows_watchlist_id ON follows(watchlist_id);
CREATE INDEX idx_follows_stock_ticker ON follows(stock_ticker);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for user_preferences
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for watchlist_settings
CREATE TRIGGER update_watchlist_settings_updated_at
    BEFORE UPDATE ON watchlist_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for stock_events
CREATE TRIGGER update_stock_events_updated_at
    BEFORE UPDATE ON stock_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
