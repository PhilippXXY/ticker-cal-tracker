# Cloud Architecture

This section describes the cloud architecture chosen for the **Stock Ticker Calendar Tracker**.  
It explains the deployed components, their responsibilities, security considerations and operational characteristics.

---

## Architectural Overview

The application follows a **cloud-native, serverless-first architecture** hosted on **Google Cloud Platform (GCP)**.

At a high level, the system consists of:

- Stateless backend service
- Managed PostgreSQL database
- CI/CD pipeline for automated builds and deployments
- Managed authentication and secure networking

This architecture emphasizes scalability, security, and operational simplicity.

---

## Backend Service – Google Cloud Run

The backend API is deployed using **Google Cloud Run**.

### Rationale

Google Cloud Run was chosen because it:

- supports containerised applications
- scales automatically based on incoming traffic
- requires no infrastructure management
- charges only for actual usage

### Characteristics

- Stateless REST API
- Container image built via Docker
- HTTPS enabled by default
- Auto-scaling from zero to multiple instances

Cloud Run enables horizontal scaling without manual intervention, fulfilling the requirement for scalable cloud services.

---

## Database – Google Cloud SQL for PostgreSQL

Persistent data is stored in **Google Cloud SQL for PostgreSQL**.

### Key Properties

- Fully managed PostgreSQL database
- Automated backups
- Built-in high availability options
- Secure private connectivity

### Security Model

- The database is **not publicly accessible**
- Access is restricted to the backend service
- Authentication is handled via service accounts
- Local access requires the **Cloud SQL Auth Proxy**

This separation ensures that administrative privileges are isolated from application-level access.

---

## Networking and Security

### HTTPS

All external traffic is served over HTTPS, enforced by Google Cloud Run.

### Authentication

- JWT-based authentication is used
- Tokens are issued after successful login
- Protected endpoints require valid JWTs

### Access Control

- User accounts are isolated
- Authorisation is enforced at the API level
- Database roles distinguish between administrative and application access

---

## CI/CD Pipeline

The project uses **GitHub Actions** to implement a continuous integration and deployment pipeline.

### Pipeline Stages

The CI/CD pipeline consists of two primary workflows:

#### Pull Request Validation Workflow

1. **Code checkout** - Fetches the latest code from the feature branch
2. **Environment setup** - Installs Python and dependencies
3. **Static analysis** - Runs `ruff` for linting and code style checks
4. **Type checking** - Executes `mypy` to verify type annotations
5. **Automated testing** - Runs complete test suite (unit + integration tests)
6. **PR status update** - Blocks merge if any check fails

#### Main Branch Deployment Workflow

1. **Docker image build** - Creates containerised application image
2. **Image publishing** - Pushes to GitHub Container Registry
3. **Cloud authentication** - Authenticates with Google Cloud using service account
4. **Deployment to Cloud Run** - Deploys new version with zero downtime
5. **Release creation** - Automatically creates GitHub release with versioning
6. **Documentation deployment** - Builds and publishes MkDocs site to GitHub Pages

This ensures that changes are automatically tested and validated prior to deployment. Only code that passes all quality gates reaches production.

### Zero-Downtime Deployment

Cloud Run implements **rolling deployments**:

1. New container instances are started alongside existing ones
2. Health checks verify new instances are ready
3. Traffic gradually shifts from old to new instances
4. Old instances are terminated after successful migration

This guarantees continuous service availability during deployments.

For detailed pipeline documentation and diagrams, see [CI/CD Pipeline](ci_cd_pipeline.md).

---

## Documentation Pipeline

Technical documentation is built using **MkDocs** and deployed automatically via GitHub Actions.

### Documentation Workflow

- Documentation is generated from Markdown files in the `docs/` directory
- UML diagrams (class diagrams, sequence diagrams) are rendered automatically using PlantUML
- The documentation site is built with `mkdocs build` command
- Built site is published to GitHub Pages
- Accessible at: [https://philippxxy.github.io/ticker-cal-tracker/docs](https://philippxxy.github.io/ticker-cal-tracker/docs)

This guarantees that documentation remains consistent with the codebase.

---

## Scalability and Reliability

The architecture supports:

- automatic horizontal scaling
- zero-downtime deployments
- fault isolation through stateless services

Cloud-managed services reduce operational overhead and increase system reliability.

