# Stock Ticker Calendar Tracker

Welcome to the **Stock Ticker Calendar Tracker** documentation.

This application allows users to track important stock market events (earnings announcements, dividends, stock splits) for their favorite companies and receive them as calendar feeds.

---

## What is Stock Ticker Calendar Tracker?

The Stock Ticker Calendar Tracker is a cloud-native web application that:

- **Tracks Stock Events** - Monitors earnings announcements, dividend dates, and stock splits
- **Generates Calendar Feeds** - Creates subscribable iCalendar feeds for your watchlists
- **Secure User Management** - JWT-based authentication and user-specific watchlists
- **Cloud-Native Architecture** - Deployed on Google Cloud Platform with auto-scaling
- **Automated CI/CD** - Continuous integration and deployment via GitHub Actions

---

## Quick Links

### Getting Started

- **[Running Locally](running_locally.md)** - Step-by-step guide to set up your development environment
- **[Local Setup](local_setup.md)** - Technical details about the local development environment
- **[API Demonstration](api_demonstration.md)** - Example API workflows and usage

### Development

- **[Testing](testing.md)** - Comprehensive testing guide (unit, integration, API tests)
- **[CI/CD Pipeline](ci_cd_pipeline.md)** - Automated deployment and quality checks

### Architecture

- **[Cloud Architecture](cloud_architecture.md)** - Production deployment on Google Cloud Platform
- **[Event Types](event_types.md)** - Stock event types supported by the application
- **[UML Diagrams](uml/class_diagram_application.md)** - System design and sequence diagrams

---

## Features

### Watchlist Management

Create and manage multiple watchlists with customizable event types:

- Add/remove stocks from watchlists
- Configure which events to include (earnings, dividends, splits)
- Rename and delete watchlists
- Secure calendar token generation

### Event Tracking

Automatically fetch and track important stock events:

- **Earnings Announcements** - Quarterly and annual earnings reports
- **Dividend Events** - Ex-dividend, declaration, record, and payment dates
- **Stock Splits** - Forward and reverse stock split announcements

### Calendar Integration

Subscribe to your watchlists in any calendar application:

- **iCalendar format** - Compatible with Google Calendar, Apple Calendar, Outlook
- **Automatic updates** - Events sync automatically as they're announced
- **Customizable feeds** - Different feeds for different watchlists

---

## Technology Stack

| Layer              | Technology             | Purpose                          |
| ------------------ | ---------------------- | -------------------------------- |
| **Backend**        | Python 3.12, Flask     | REST API server                  |
| **Database**       | PostgreSQL             | Persistent data storage          |
| **External APIs**  | Alpha Vantage, Finnhub | Stock market data                |
| **Cloud Platform** | Google Cloud Platform  | Production hosting               |
| **Compute**        | Cloud Run              | Serverless container hosting     |
| **CI/CD**          | GitHub Actions         | Automated testing and deployment |
| **Documentation**  | MkDocs                 | This documentation site          |

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

---

## Project Repository

The project is open source and available on GitHub:

**Repository:** [PhilippXXY/ticker-cal-tracker](https://github.com/PhilippXXY/ticker-cal-tracker)

---

## Live Application

The production application is hosted on Google Cloud Run:

**URL:** [https://ticker-cal-tracker-1052233055044.europe-west2.run.app](https://ticker-cal-tracker-1052233055044.europe-west2.run.app)

**Interactive API Documentation:** [https://ticker-cal-tracker-1052233055044.europe-west2.run.app/docs](https://ticker-cal-tracker-1052233055044.europe-west2.run.app/docs)

---

## License

This project is licensed under the GNU General Public License (GPL). See the [LICENSE](https://github.com/PhilippXXY/ticker-cal-tracker/blob/main/LICENSE) file for details.
