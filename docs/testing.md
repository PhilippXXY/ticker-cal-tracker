# Testing

This section provides comprehensive information about testing the **Stock Ticker Calendar Tracker** application.

---

## Test Structure Overview

The project uses a modular testing strategy with three independent test categories:

| Test Type                      | Command             | Requirements                | External API Calls | Database Access |
| ------------------------------ | ------------------- | --------------------------- | ------------------ | --------------- |
| **Unit Tests**                 | `--unit`            | None                        | No                 | No              |
| **API Integration Tests**      | `--api-integration` | API keys in `.env`          | Yes (rate limited) | No              |
| **Database Integration Tests** | `--db-integration`  | Running PostgreSQL database | No                 | Yes             |
| **All Integration Tests**      | `--integration`     | API keys + Database         | Yes                | Yes             |
| **All Tests**                  | `--all`             | API keys + Database         | Yes                | Yes             |

This modular approach allows developers to run tests independently based on available resources and development context.

---

## Unit Tests

Unit tests verify isolated components without external dependencies. They use mocks and stubs to simulate external services.

### Characteristics

- **No external dependencies required**
- **Fast execution**
- **No API rate limits**
- **No database required**

### Running Unit Tests

From the project root directory:

```bash
# Using the test runner (recommended)
python src/tests/run_tests.py --unit

# Or run specific test files directly with unittest
python -m unittest src.tests.test_alpha_vantage -v
python -m unittest src.tests.test_finnhub -v
python -m unittest src.tests.test_local_adapter -v
```

### What Unit Tests Cover

- External API client logic (mocked responses)
- Database adapter logic (mocked connections)
- Data transformation and validation
- Error handling and edge cases

---

## API Integration Tests

API integration tests verify that external APIs (Alpha Vantage, Finnhub) return expected data formats and handle real-world scenarios correctly.

### Important Warnings

**These tests make REAL API calls that count against your rate limits:**

- **Alpha Vantage**: 25 requests per day, 5 requests per minute (free tier)
- **Finnhub**: 60 requests per minute (free tier)

**Use these tests sparingly to avoid exhausting your API quotas.**

### Setup Requirements

1. Obtain API keys from:

   - [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - [Finnhub](https://finnhub.io/register)

2. Create a `.env` file in the project root:

```bash
API_KEY_ALPHA_VANTAGE=your_alpha_vantage_key_here
API_KEY_FINNHUB=your_finnhub_key_here
```

### Running API Integration Tests

```bash
# Run only API integration tests
python src/tests/run_tests.py --api-integration

# Or run specific API test files
python -m unittest src.tests.test_alpha_vantage_integration -v
python -m unittest src.tests.test_finnhub_integration -v
```

### What API Integration Tests Cover

- Real API endpoint connectivity
- Response format validation
- Error handling for invalid symbols
- Rate limiting behaviour
- Data accuracy verification

---

## Database Integration Tests

Database integration tests verify that the database adapter correctly interacts with PostgreSQL.

### Characteristics

- **No external API calls** (safe for unlimited runs)
- Requires a running PostgreSQL database
- Tests CRUD operations
- Validates data integrity and constraints

### Setup Requirements

The database must be running before executing these tests:

```bash
# First-time setup
python database/local/manage_db.py setup

# Or start existing database
python database/local/manage_db.py start

# Verify database is running
python database/local/manage_db.py status
```

### Running Database Integration Tests

```bash
# Run only database integration tests
python src/tests/run_tests.py --db-integration

# Or run specific database test files
python -m unittest src.tests.test_local_adapter_integration -v
```

### What Database Integration Tests Cover

- Database connection and authentication
- CRUD operations (Create, Read, Update, Delete)
- Foreign key constraints and referential integrity
- Transaction handling and rollbacks
- Query performance and indexing

---

## Running All Integration Tests

To run both API and database integration tests together:

```bash
python src/tests/run_tests.py --integration
```

**Prerequisites:**

- API keys configured in `.env`
- PostgreSQL database running

---

## Running All Tests

To execute the complete test suite (unit + all integration tests):

```bash
python src/tests/run_tests.py --all
```

**Prerequisites:**

- API keys configured in `.env`
- PostgreSQL database running
- Be mindful of API rate limits

---

## Test Runner Options

The custom test runner (`src/tests/run_tests.py`) provides convenient test execution with clear output:

| Flag                | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `--unit`            | Run only unit tests (no external dependencies)          |
| `--api-integration` | Run only API integration tests (requires API keys)      |
| `--db-integration`  | Run only database integration tests (requires database) |
| `--integration`     | Run both API and database integration tests             |
| `--all`             | Run all tests (unit + integration)                      |