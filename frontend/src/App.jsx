import React, { useState } from "react";
import WelcomePanel from "./components/WelcomePanel";
import AuthPanel from "./components/AuthPanel";
import UserPanel from "./components/UserPanel";
import WatchlistsPanel from "./components/WatchlistsPanel";
import "./styles/App.css";

// Use relative URL in development (proxied by Vite), absolute URL in production
const API_BASE_URL = import.meta.env.DEV
  ? ""
  : "https://ticker-cal-tracker-1052233055044.europe-west2.run.app";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [activeTab, setActiveTab] = useState("home");

  const handleLogin = (newToken) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
    setActiveTab("user");
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("token");
    setActiveTab("home");
  };

  const handleAuthClick = () => {
    setActiveTab("auth");
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Stock Ticker Calendar Tracker</h1>
          <div className="header-right">
            <a
              href="https://github.com/PhilippXXY/ticker-cal-tracker"
              target="_blank"
              rel="noopener noreferrer"
              className="repo-link"
              title="Go to repository"
            >
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path
                  fill="currentColor"
                  d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
                />
              </svg>
            </a>
            {token ? (
              <button className="logout-btn" onClick={handleLogout}>
                Logout
              </button>
            ) : (
              <button className="logout-btn" onClick={handleAuthClick}>
                Login
              </button>
            )}
          </div>
        </div>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === "home" ? "active" : ""}
          onClick={() => setActiveTab("home")}
        >
          Home
        </button>
        <button
          className={activeTab === "watchlists" ? "active" : ""}
          onClick={() => setActiveTab("watchlists")}
          disabled={!token}
        >
          Watchlists
        </button>
        <button
          className={activeTab === "user" ? "active" : ""}
          onClick={() => setActiveTab("user")}
          disabled={!token}
        >
          User
        </button>
      </nav>

      <main className="content">
        {activeTab === "home" && <WelcomePanel />}
        {activeTab === "auth" && (
          <AuthPanel apiUrl={API_BASE_URL} onLogin={handleLogin} />
        )}
        {activeTab === "watchlists" && token && (
          <WatchlistsPanel apiUrl={API_BASE_URL} token={token} />
        )}
        {activeTab === "user" && token && (
          <UserPanel apiUrl={API_BASE_URL} token={token} />
        )}
      </main>
    </div>
  );
}

export default App;
