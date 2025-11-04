-- Disclaimer: Created by GitHub Copilot

-- Combined initialization script
-- This file is automatically run when the Docker container starts for the first time

\echo 'Creating database schema...'
\i /schema.sql

\echo 'Seeding database with test data...'
\i /seed_data.sql

\echo 'Database initialization complete!'
