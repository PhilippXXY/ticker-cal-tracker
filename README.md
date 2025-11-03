# Stock Ticker Calendar Tracker

## Deployment
Install the required packages using pip:

```bash
pip install -r requirements.txt
```

Navigate to the root directory of the repository and run the application:

```bash
python -m src.app.main
```

## API Documentation

While running the application, you can access the API documentation at `ip:port/docs`.

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
