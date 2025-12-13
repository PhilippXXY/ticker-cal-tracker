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

- supports containerized applications
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
- Authorization is enforced at the API level
- Database roles distinguish between administrative and application access

---

## CI/CD Pipeline

The project uses **GitHub Actions** to implement a continuous integration and deployment pipeline.

### Pipeline Stages

1. Code checkout
2. Static analysis and linting
3. Type checking
4. Automated testing
5. Docker image build
6. Deployment to Cloud Run

This ensures that changes are automatically tested and validated prior to deployment.

---

## Documentation Pipeline

Technical documentation is built using **MkDocs** and deployed automatically via GitHub Actions.

- Documentation is generated from Markdown files
- UML diagrams are rendered automatically using PlantUML
- The documentation site is published to GitHub Pages

This guarantees that documentation remains consistent with the codebase.

---

## Scalability and Reliability

The architecture supports:

- automatic horizontal scaling
- zero-downtime deployments
- fault isolation through stateless services

Cloud-managed services reduce operational overhead and increase system reliability.

---

## Mapping to Grading Criteria

| Requirement            | Fulfilled By                       |
| ---------------------- | ---------------------------------- |
| CI/CD pipeline         | GitHub Actions                     |
| HTTPS                  | Google Cloud Run                   |
| GCP database           | Cloud SQL for PostgreSQL           |
| REST services          | Flask-based API                    |
| Documentation          | MkDocs + GitHub Pages              |
| Testing & checks       | Automated CI workflows             |
| Scalability            | Serverless Cloud Run               |
| Authentication         | JWT-based auth                     |
| Access management      | Role separation & service accounts |
| Secure database access | Cloud SQL Auth Proxy               |
