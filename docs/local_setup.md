# Local Setup

This section describes how to run the **Stock Ticker Calendar Tracker** locally for development and testing purposes.  
It is intended for technically experienced users and explains the required environment, dependencies, and startup steps in detail.

---

## Requirements

To run the application locally, the following tools and services are required:

| Requirement | Purpose                       |
| ----------- | ----------------------------- |
| Python      | Application runtime           |
| Docker      | Local PostgreSQL database     |
| Git         | Source code management        |
| API Keys    | External stock data providers |

### Python Version

The project enforces a specific Python version via the `.python-version` file:

```text
3.12.0
```

---

## Python Environment Setup

The project enforces a fixed Python version to ensure consistent behaviour across development machines and CI pipelines.

The required version is specified in the `.python-version` file and should be installed using a Python version manager such as `pyenv`.

### Virtual Environment

A dedicated virtual environment is used to isolate project dependencies from the global system environment.

After selecting the correct Python version, create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

---

## Dependency Installation

All required Python dependencies for the application are defined in the `requirements.txt` file at the project root.

To install them inside the active virtual environment, run:

```bash
pip install -r requirements.txt
```

---

## Local Database Setup

The application requires a PostgreSQL database to store users, watchlists, stocks, and event data.

For local development, the database is provided using **Docker** to ensure a consistent and isolated environment without requiring a native PostgreSQL installation.

### Docker Compose

Database configuration is defined in the `docker-compose.yml` file at the project root.

To start the database container, run:

```bash
docker compose up -d
```

## Environment Variables

The application requires API keys and database configuration to be provided via environment variables.

A template file `.env.example` is included at the project root.

To configure the environment:

```bash
cp .env.example .env
```

---

## Running the Application

After configuring the environment and starting the database, the application can be started locally.

From the project root, run:

```bash
python -m src.app

```

---

## Database Initialisation

The database schema is provisioned automatically during the initial container startup.

On first launch, the PostgreSQL container executes the SQL initialisation scripts mounted via Docker Compose. These scripts create the required schema and seed any initial data. No manual database initialisation step is required for local development.

---

## Stopping the Application

To stop the database container:

```bash
docker compose down
```
