import React from "react";

function WelcomePanel() {
  const PROD_API =
    "https://ticker-cal-tracker-1052233055044.europe-west2.run.app";
  const DOCS_URL = "https://philippxxy.github.io/ticker-cal-tracker/docs/";
  const SWAGGER_URL = `${PROD_API}/docs`;
  const GITHUB_URL = "https://github.com/PhilippXXY/ticker-cal-tracker";

  return (
    <div className="panel welcome-panel">
      <h2>Welcome to Stock Ticker Calendar Tracker</h2>

      <div className="welcome-intro">
        <p>
          The Stock Ticker Calendar Tracker puts upcoming stock events directly
          into your private calendar. Create watchlists and subscribe to their
          calendar feeds to track earnings, dividends, and stock splits.
        </p>
      </div>

      <div className="welcome-features">
        <h3>Key Features</h3>
        <ul>
          <li>
            <strong>Watchlists to Calendars:</strong> Each watchlist generates
            its own <code>.ics</code> calendar feed URL
          </li>
          <li>
            <strong>Event Types:</strong> Track Earnings announcements,
            Dividends (ex-date, declaration, record, payment), and Stock Splits
          </li>
          <li>
            <strong>Filtering:</strong> Configure which event types appear in
            each watchlist
          </li>
          <li>
            <strong>Safe Sharing:</strong> Rotate calendar tokens to revoke
            access to shared feeds
          </li>
        </ul>
      </div>

      <div className="welcome-demo">
        <h3>How It Works</h3>
        <ol>
          <li>
            Create one or more watchlists (e.g., "Growth", "Dividend", "Value")
          </li>
          <li>Add stocks to each watchlist</li>
          <li>Choose which event types should appear</li>
          <li>Subscribe to the generated calendar feed in your calendar app</li>
        </ol>
      </div>

      <div className="welcome-links">
        <h3>Resources</h3>
        <div className="link-grid">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="link-card"
          >
            <div>
              <strong>GitHub Repository</strong>
              <p>Source code and CI/CD pipeline</p>
            </div>
          </a>
          <a
            href={DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="link-card"
          >
            <div>
              <strong>Documentation</strong>
              <p>Full guides and API walkthrough</p>
            </div>
          </a>
          <a
            href={SWAGGER_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="link-card"
          >
            <div>
              <strong>API Swagger UI</strong>
              <p>Interactive API documentation</p>
            </div>
          </a>
        </div>
      </div>

      <div className="welcome-cta">
        <p>
          <strong>Ready to get started?</strong> Click the{" "}
          <strong>Login</strong> button in the header to authenticate and start
          managing your watchlists!
        </p>
      </div>
    </div>
  );
}

export default WelcomePanel;
