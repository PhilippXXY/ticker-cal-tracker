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

The project has three types of tests that can be run independently:

| Test Type | Command | Requires | API Calls | Database |
|-----------|---------|----------|-----------|----------|
| **Unit Tests** | `--unit` | Nothing | No | No |
| **API Integration** | `--api-integration` | API keys | Yes (rate limited) | No |
| **Database Integration** | `--db-integration` | Running DB | No | Yes |
| **All Integration** | `--integration` | API keys + DB | Yes | Yes |
| **All Tests** | `--all` | API keys + DB | Yes | Yes |

### Unit Tests (No External Dependencies)

Run unit tests that use mocks and don't make real API calls or require a database:

```bash
# Using the test runner
python src/tests/run_tests.py --unit

# Or directly with unittest
python -m unittest src.tests.test_alpha_vantage -v
python -m unittest src.tests.test_finnhub -v
python -m unittest src.tests.test_local_adapter -v
```

### Integration Tests

Integration tests are split into two independent categories so you can run them separately:

#### 1. API Integration Tests (Real API Calls - Rate Limited)

These tests verify external APIs (Alpha Vantage, Finnhub) return expected data. 

**These make REAL API calls and count against rate limits!**
- Alpha Vantage: 25 requests/day, 5 requests/minute
- Finnhub: 60 requests/minute

**Setup:** Add API keys to `.env` file in project root:
```
API_KEY_ALPHA_VANTAGE=your_alpha_vantage_key_here
API_KEY_FINNHUB=your_finnhub_key_here
```

**Run API integration tests ONLY:**
```bash
python src/tests/run_tests.py --api-integration
```

#### 2. Database Integration Tests (Requires Running Database)

These tests verify the database adapter works correctly with PostgreSQL. **No API calls are made.**

**Setup:** Ensure the database is running:
```bash
python database/local/manage_db.py setup  # First time
# or
python database/local/manage_db.py start  # If already set up
```

**Run database integration tests only:**
```bash
python src/tests/run_tests.py --db-integration
```

#### Run Both Integration Test Types Together

If you want to run all integration tests in one command:

```bash
python src/tests/run_tests.py --integration
```

#### Direct unittest Commands

You can also run tests directly:
```bash
# API integration tests only
python -m unittest src.tests.test_alpha_vantage_integration -v
python -m unittest src.tests.test_finnhub_integration -v

# Database integration tests only
python -m unittest src.tests.test_local_adapter_integration -v
```

### Run All Tests

```bash
python src/tests/run_tests.py --all
```
