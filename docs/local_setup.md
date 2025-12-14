# Local Setup

This guide provides **step-by-step instructions** for running the **Stock Ticker Calendar Tracker** on your local machine for development purposes.

---

## Prerequisites

Before starting, ensure you have the following installed:

| Tool               | Version | Purpose                       | Installation                                                   |
| ------------------ | ------- | ----------------------------- | -------------------------------------------------------------- |
| **Python**         | 3.12    | Application runtime           | [python.org](https://www.python.org/downloads/) or use `uv` |
| **Docker Desktop** | Latest  | PostgreSQL database container | [docker.com](https://www.docker.com/products/docker-desktop/)  |
| **Git**            | Latest  | Version control               | [git-scm.com](https://git-scm.com/downloads)                   |
| **pip**            | Latest  | Python package manager        | Included with Python                                           |

### Verify Installation

```bash
python --version    # Should show Python 3.12.x
docker --version    # Should show Docker version
git --version       # Should show Git version
```

---

## Step 1: Clone the Repository

Clone the project from GitHub and navigate to the project directory:

```bash
git clone https://github.com/PhilippXXY/ticker-cal-tracker.git
cd ticker-cal-tracker
```

---

## Step 2: Create Virtual Environment Environment

Create an isolated Python environment to avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

**After activation, your terminal prompt should show `(venv)` prefix:**

```bash
(venv) user@machine:~/ticker-cal-tracker$
```

---

## Step 3: Install Python Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Step 4: Set Up the Database

The application uses PostgreSQL running in Docker for local development.

### Start the Database (First Time)

For setup, use the automated setup script:

```bash
python database/local/manage_db.py setup
```

**This command will:**

1. Check if Docker is running
2. Pull the PostgreSQL Docker image
3. Create and start the database container
4. Create the database schema (tables, indexes, constraints)
5. Seed initial data (demo user, sample watchlists)


### Database Connection Details

The local database is configured with the following credentials:

| Parameter             | Value                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------- |
| **Host**              | `localhost`                                                                            |
| **Port**              | `5432`                                                                                 |
| **Database**          | `ticker_calendar_local_dev_db`                                                         |
| **User**              | `ticker_dev`                                                                           |
| **Password**          | `dev_password_123`                                                                     |
| **Connection String** | `postgresql://ticker_dev:dev_password_123@localhost:5432/ticker_calendar_local_dev_db` |

### Database Management Commands

```bash
# Start existing database container
python database/local/manage_db.py start

# Stop database container
python database/local/manage_db.py stop

# Check database status
python database/local/manage_db.py status

# View database logs
python database/local/manage_db.py logs

# Reset database (delete all data and recreate)
python database/local/manage_db.py reset

# Open PostgreSQL shell (psql)
python database/local/manage_db.py shell
```

### Verify Database is Running

```bash
python database/local/manage_db.py status
```

**Expected output:**

```
✓ Container 'ticker_calendar_postgres_local' is running
✓ Database is accepting connections
✓ Status: healthy
```

---

## Step 5: Configure API Keys

The application requires API keys from external stock data providers.

### Obtain API Keys

1. **Alpha Vantage** (free tier: 25 requests/day)

   - Sign up at: [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
   - Copy your API key

2. **Finnhub** (free tier: 60 requests/minute)
   - Register at: [finnhub.io/register](https://finnhub.io/register)
   - Copy your API key from the dashboard

### Create Environment Variables File

Create a `.env` file in the project root directory:

```bash
touch .env
```

### Add API Keys to `.env`

Edit the `.env` file and add your API keys:

```bash
# External API Keys
API_KEY_ALPHA_VANTAGE=your_alpha_vantage_key_here
API_KEY_FINNHUB=your_finnhub_key_here
```

**Important:**

- Replace `your_alpha_vantage_key_here` with your actual Alpha Vantage API key
- Replace `your_finnhub_key_here` with your actual Finnhub API key
- Never commit `.env` file to version control (it's in `.gitignore`)

### Verify Configuration

```bash
# Check that .env file exists and contains keys
cat .env | grep API_KEY
```

**Expected output:**

```
API_KEY_ALPHA_VANTAGE=ABC123...
API_KEY_FINNHUB=XYZ789...
```

---

## Step 6: Run the Application

Start the application using Python's module execution:

```bash
python -m src.app.main
```

---

## Step 7: Access the Application

### API Documentation (Swagger UI)

Open your web browser and navigate to:

```
http://localhost:8080/docs
```

This opens the **interactive API documentation** where you can:

- View all available endpoints
- Test API calls directly in the browser
- See request/response schemas
- Try authentication flow

---

## Common Issues and Troubleshooting

### Issue 1: Docker Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**

```bash
# Start Docker Desktop application
# Then verify:
docker ps
```

### Issue 2: Port 5432 Already in Use

**Error:** `Port 5432 is already allocated`

**Solution:**

```bash
# Check what's using port 5432
lsof -i :5432

# Stop conflicting PostgreSQL instance
brew services stop postgresql  # If using Homebrew on macOS

# Or use different port in docker-compose.yml
```

### Issue 3: Port 8080 Already in Use

**Error:** `Address already in use: 0.0.0.0:8080`

**Solution:**

```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or run on different port
uvicorn src.app.main:app --port 8081
```

### Issue 4: Missing API Keys

**Error:** `API_KEY_ALPHA_VANTAGE not found in environment`

**Solution:**

```bash
# Verify .env file exists and contains keys
cat .env

# Ensure you're in the correct directory (project root)
pwd  # Should show /path/to/ticker-cal-tracker
```

### Issue 5: Database Connection Failed

**Error:** `FATAL:  password authentication failed for user "ticker_dev"`

**Solution:**

```bash
# Reset database
python database/local/manage_db.py reset

# Verify database is running
python database/local/manage_db.py status
```

---

## Stopping the Application

### Stop the Application Server

Press `CTRL+C` in the terminal where the application is running.

### Stop the Database

```bash
python database/local/manage_db.py stop
```

### Deactivate Virtual Environment

```bash
deactivate
```

Your terminal prompt will no longer show `(venv)` prefix.
