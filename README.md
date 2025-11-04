# Stock Ticker Calendar Tracker

---

## Quick Start for Local Developement

### Prerequisites

- Python 3.8+
- Docker Desktop (for local database)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/PhilippXXY/ticker-cal-tracker.git
cd ticker-cal-tracker
```

### 2. Set Up the Database

The project uses PostgreSQL running in Docker for local development. Setup is automated with a Python script:

```bash
# First time setup (creates database with schema and sample data)
python database/local/manage_db.py setup
```

**Database Management Commands:**

```bash
python database/local/manage_db.py setup   # Create and initialize database
python database/local/manage_db.py start   # Start existing database
python database/local/manage_db.py stop    # Stop database
python database/local/manage_db.py reset   # Delete all data and recreate fresh
python database/local/manage_db.py status  # Check database status
python database/local/manage_db.py logs    # View database logs
python database/local/manage_db.py shell   # Open PostgreSQL shell (psql)
```

**Connection Details:**

- Host: `localhost`
- Port: `5432`
- Database: `ticker_calendar_local_dev_db`
- User: `ticker_dev`
- Password: `dev_password_123`
- Connection String: `postgresql://ticker_dev:dev_password_123@localhost:5432/ticker_calendar_local_dev_db`

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root with your API keys:

```bash
API_KEY_ALPHA_VANTAGE=your_alpha_vantage_key_here
API_KEY_FINNHUB=your_finnhub_key_here
API_KEY_OPEN_FIGI=your_open_figi_key_here
```

### 5. Run the Application

```bash
python -m src.app.main
```

---

## API Documentation

While running the application, you can access the API documentation at `ip:port/docs`.

---

## Testing

### Unit Tests (No API Calls)

Run unit tests that use mocks and don't make real API calls:

```bash
# Using the test runner
python src/tests/run_tests.py --unit

# Or directly with unittest
cd src
python -m unittest tests.test_alpha_vantage -v
python -m unittest tests.test_finnhub -v
```

### Integration Tests (Real API Calls)

Integration tests verify the actual external APIs return expected data. **These make real API calls and count against rate limits!**

The API keys need to be in your `.env` file in the project root:

```
API_KEY_ALPHA_VANTAGE=your_alpha_vantage_key_here
API_KEY_FINNHUB=your_finnhub_key_here
```

Then run the integration tests:

```bash
# Using the test runner (with confirmation prompt)
python src/tests/run_tests.py --integration

# Or directly with unittest
cd src
python -m unittest tests.test_alpha_vantage_integration -v
python -m unittest tests.test_finnhub_integration -v
```

### Run All Tests

```bash
python src/tests/run_tests.py --all
```
