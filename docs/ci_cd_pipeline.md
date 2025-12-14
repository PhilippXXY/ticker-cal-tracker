# CI/CD Pipeline

This section describes the **Continuous Integration and Continuous Deployment (CI/CD)** pipeline for the **Stock Ticker Calendar Tracker**.

The pipeline ensures code quality, automates testing, and deploys the application to production seamlessly.

---

## Pipeline Overview

The CI/CD pipeline is implemented using **GitHub Actions** and consists of two main workflows:

1. **Pull Request Checks** - Validates code quality before merging
2. **Main Branch Deployment** - Deploys to production after merge

---

## Pull Request Workflow

When a developer opens a pull request, the following automated checks are triggered:

### 1. Code Checkout

- GitHub Actions checks out the repository code
- Sets up Python environment
- Installs all dependencies from `requirements.txt`

### 2. Type Checking with mypy

- Performs static type analysis
- Ensures type annotations are correct
- Verifies type safety across the codebase
- **Blocks PR merge if type errors are found**

### 3. Linting with ruff

- Checks code style and formatting
- Identifies potential code quality issues
- Enforces PEP 8 compliance
- **Blocks PR merge if linting issues are found**

### 4. Automated Testing

- Runs all unit tests
- **Blocks PR merge if any tests fail**

### 5. PR Status Update

- GitHub displays check results on the PR
- Green checkmarks indicate all checks passed
- Red X marks indicate failures requiring fixes
- **PR can only be merged when all checks pass**

---

## Main Branch Deployment Workflow

When a pull request is merged to the `main` branch, the deployment workflow automatically:

### 1. Build Docker Image

- Builds application container using `Dockerfile`
- Tags image with commit SHA for traceability
- Pushes image to **GitHub Container Registry (ghcr.io)**

### 2. Create GitHub Release

- Automatically creates a new GitHub release
- Tags the release with semantic versioning
- Includes release notes with recent changes
- Provides traceability for deployed versions
- Has Docker image as attachement

### 3. Deploy to Google Cloud Run

**Deployment steps:**

1. Authenticates with Google Cloud using service account
2. Pulls the Docker image from the registry
3. Deploys new container instances to Cloud Run
4. Gradually shifts traffic from old to new instances (zero-downtime deployment)
5. Terminates old instances after successful traffic migration

**Deployment characteristics:**

- **Region**: `europe-west2` (London)
- **Platform**: Serverless (managed Cloud Run)
- **Scaling**: Automatic (0 to N instances based on traffic)
- **HTTPS**: Enabled by default
- **Zero downtime**: Rolling deployment strategy

### 4. Build and Deploy Frontend

**Frontend:**

1. Installs Node.js and npm dependencies from `frontend/package.json`
2. Builds the frontend application using Vite
3. Publishes to GitHub Pages

Accessible at: [https://philippxxy.github.io/ticker-cal-tracker/](https://philippxxy.github.io/ticker-cal-tracker/)
  
**Documentation:**

1. Builds the MkDocs documentation site
2. Publishes to GitHub Pages

---

## Workflow Configuration

The pipeline is defined in GitHub Actions workflow files located at: [https://github.com/PhilippXXY/ticker-cal-tracker/tree/main/.github/workflows](https://github.com/PhilippXXY/ticker-cal-tracker/tree/main/.github/workflows)

---

## Security Considerations

### Secret Management

- API keys and credentials are stored as **GitHub Secrets**
- Secrets are injected into workflows at runtime
- Never committed to the repository

### Google Cloud Authentication

- Uses **service account credentials**
- Stored as GitHub Secret: `GCP_SERVICE_ACCOUNT_KEY`
- Principle of least privilege (deploy-only permissions)

### Container Registry Access

- GitHub Container Registry requires authentication
- Uses GitHub token with package write permissions
- Automatic cleanup of old images