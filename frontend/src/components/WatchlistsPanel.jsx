import React, { useState, useEffect } from "react";
import axios from "axios";

function WatchlistsPanel({ apiUrl, token }) {
  const [watchlists, setWatchlists] = useState([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState(null);
  const [follows, setFollows] = useState([]);
  const [newWatchlistName, setNewWatchlistName] = useState("");
  const [tickerToFollow, setTickerToFollow] = useState("");
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [calendarUrls, setCalendarUrls] = useState({});
  const [editingWatchlist, setEditingWatchlist] = useState(null);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [pendingWatchlistId, setPendingWatchlistId] = useState(null);
  const [eventSettings, setEventSettings] = useState({
    include_earnings_announcement: true,
    include_dividend_ex: true,
    include_dividend_declaration: true,
    include_dividend_record: true,
    include_dividend_payment: true,
    include_stock_split: true,
  });

  const fetchWatchlists = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await axios.get(`${apiUrl}/api/watchlists/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWatchlists(res.data);

      // Fetch calendar URLs for all watchlists (non-blocking)
      const urls = {};
      await Promise.all(
        res.data.map(async (wl) => {
          try {
            const calRes = await axios.get(`${apiUrl}/api/cal/${wl.id}`, {
              headers: { Authorization: `Bearer ${token}` },
            });
            urls[wl.id] = calRes.data.calendar_url;
          } catch (err) {
            // Silently fail for calendar URLs - they're not critical
            console.warn(`Could not fetch calendar URL for ${wl.id}`);
            urls[wl.id] = "Calendar URL unavailable";
          }
        })
      );
      setCalendarUrls(urls);
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message;
      if (err.response?.status === 401) {
        setError("Authentication expired. Please login again.");
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchFollows = async (watchlistId) => {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await axios.get(
        `${apiUrl}/api/watchlists/${watchlistId}/stocks`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setFollows(res.data);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const createWatchlist = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post(
        `${apiUrl}/api/watchlists/`,
        { name: newWatchlistName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse(res.data);
      setNewWatchlistName("");
      setPendingWatchlistId(res.data.id);
      await fetchWatchlists();
      // Show modal to configure event settings
      setShowSettingsModal(true);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveEventSettings = async () => {
    if (!pendingWatchlistId) return;

    setLoading(true);
    setError(null);

    try {
      await axios.put(
        `${apiUrl}/api/watchlists/${pendingWatchlistId}`,
        eventSettings,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowSettingsModal(false);
      setPendingWatchlistId(null);
      // Reset event settings to defaults
      setEventSettings({
        include_earnings_announcement: true,
        include_dividend_ex: true,
        include_dividend_declaration: true,
        include_dividend_record: true,
        include_dividend_payment: true,
        include_stock_split: true,
      });
      await fetchWatchlists();
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateWatchlist = async (e) => {
    e.preventDefault();
    if (!editingWatchlist) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      await axios.put(
        `${apiUrl}/api/watchlists/${editingWatchlist.id}`,
        { name: editingWatchlist.name, ...editingWatchlist.settings },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse({ message: "Watchlist updated successfully" });
      setEditingWatchlist(null);
      await fetchWatchlists();
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const startEditingWatchlist = (wl) => {
    setEditingWatchlist({
      id: wl.id,
      name: wl.name,
      settings: {
        include_earnings_announcement: wl.include_earnings_announcement ?? true,
        include_dividend_ex: wl.include_dividend_ex ?? true,
        include_dividend_declaration: wl.include_dividend_declaration ?? true,
        include_dividend_record: wl.include_dividend_record ?? true,
        include_dividend_payment: wl.include_dividend_payment ?? true,
        include_stock_split: wl.include_stock_split ?? true,
      },
    });
    setResponse(null);
    setError(null);
  };

  const followStock = async (e) => {
    e.preventDefault();
    if (!selectedWatchlist) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post(
        `${apiUrl}/api/watchlists/${selectedWatchlist}/stocks/${tickerToFollow.toUpperCase()}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse(res.data);
      setTickerToFollow("");
      await fetchFollows(selectedWatchlist);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const unfollowStock = async (ticker) => {
    if (!selectedWatchlist) return;

    const confirmed = window.confirm(
      `Are you sure you want to unfollow ${ticker}?`
    );
    if (!confirmed) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.delete(
        `${apiUrl}/api/watchlists/${selectedWatchlist}/stocks/${ticker}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse(res.data);
      await fetchFollows(selectedWatchlist);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteWatchlist = async (watchlistId) => {
    const watchlist = watchlists.find((wl) => wl.id === watchlistId);
    const confirmed = window.confirm(
      `Are you sure you want to delete the watchlist "${watchlist?.name}"? This cannot be undone.`
    );
    if (!confirmed) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      await axios.delete(`${apiUrl}/api/watchlists/${watchlistId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setResponse({ message: "Watchlist deleted successfully" });
      if (selectedWatchlist === watchlistId) {
        setSelectedWatchlist(null);
        setFollows([]);
      }
      await fetchWatchlists();
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const rotateCalendarToken = async (watchlistId) => {
    const confirmed = window.confirm(
      "Are you sure you want to rotate the calendar token? The old calendar URL will no longer work."
    );
    if (!confirmed) return;
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post(
        `${apiUrl}/api/cal/${watchlistId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse({ message: "Calendar token rotated successfully" });
      // Update the calendar URL in state
      setCalendarUrls((prev) => ({
        ...prev,
        [watchlistId]: res.data.calendar_url,
      }));
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, e) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      // Silently copy without showing a message
    } catch (err) {
      setError("Failed to copy to clipboard");
    }
  };

  const getCalendarUrl = (watchlistId) => {
    return calendarUrls[watchlistId] || "Loading...";
  };

  useEffect(() => {
    fetchWatchlists();
  }, []);

  useEffect(() => {
    if (selectedWatchlist) {
      fetchFollows(selectedWatchlist);
    }
  }, [selectedWatchlist]);

  return (
    <div className="panel">
      <h2>Watchlists</h2>

      <button
        onClick={fetchWatchlists}
        disabled={loading}
        className="action-btn"
      >
        Refresh Watchlists
      </button>

      <h3>Create New Watchlist</h3>
      <form onSubmit={createWatchlist} className="api-form">
        <div className="form-group">
          <label>Watchlist Name:</label>
          <input
            type="text"
            value={newWatchlistName}
            onChange={(e) => setNewWatchlistName(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading} className="submit-btn">
          Create
        </button>
      </form>

      <h3>My Watchlists</h3>
      {watchlists.length === 0 ? (
        <p>No watchlists yet. Create one above!</p>
      ) : (
        <div className="watchlist-grid">
          {watchlists.map((wl) => (
            <div
              key={wl.id}
              className={`watchlist-card ${
                selectedWatchlist === wl.id ? "selected" : ""
              }`}
              onClick={() => setSelectedWatchlist(wl.id)}
            >
              <h4>{wl.name}</h4>
              <p className="small">ID: {wl.id}</p>
              <p className="small">
                Created: {new Date(wl.created_at).toLocaleDateString()}
              </p>
              <div className="calendar-url-container">
                <label className="small">Calendar URL:</label>
                <div className="calendar-url-field">
                  <input
                    type="text"
                    value={getCalendarUrl(wl.id)}
                    readOnly
                    className="calendar-url-input"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <button
                    onClick={(e) => copyToClipboard(getCalendarUrl(wl.id), e)}
                    className="copy-btn"
                    title="Copy to clipboard"
                    disabled={!calendarUrls[wl.id]}
                  >
                    📋
                  </button>
                </div>
              </div>
              <div className="card-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    startEditingWatchlist(wl);
                  }}
                  className="small-btn"
                >
                  Edit
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    rotateCalendarToken(wl.id);
                  }}
                  className="small-btn"
                >
                  Rotate Token
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteWatchlist(wl.id);
                  }}
                  className="small-btn danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editingWatchlist && (
        <div
          className="modal-overlay"
          onClick={() => setEditingWatchlist(null)}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Watchlist</h3>
            <form onSubmit={updateWatchlist}>
              <div className="form-group">
                <label>Watchlist Name:</label>
                <input
                  type="text"
                  value={editingWatchlist.name}
                  onChange={(e) =>
                    setEditingWatchlist({
                      ...editingWatchlist,
                      name: e.target.value,
                    })
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label>Event Types to Track:</label>
                <div className="checkbox-grid">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={
                        editingWatchlist.settings.include_earnings_announcement
                      }
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_earnings_announcement: e.target.checked,
                          },
                        })
                      }
                    />
                    Earnings
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={editingWatchlist.settings.include_dividend_ex}
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_dividend_ex: e.target.checked,
                          },
                        })
                      }
                    />
                    Div. Ex-Date
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={
                        editingWatchlist.settings.include_dividend_declaration
                      }
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_dividend_declaration: e.target.checked,
                          },
                        })
                      }
                    />
                    Div. Declaration
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={
                        editingWatchlist.settings.include_dividend_record
                      }
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_dividend_record: e.target.checked,
                          },
                        })
                      }
                    />
                    Div. Record
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={
                        editingWatchlist.settings.include_dividend_payment
                      }
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_dividend_payment: e.target.checked,
                          },
                        })
                      }
                    />
                    Div. Payment
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={editingWatchlist.settings.include_stock_split}
                      onChange={(e) =>
                        setEditingWatchlist({
                          ...editingWatchlist,
                          settings: {
                            ...editingWatchlist.settings,
                            include_stock_split: e.target.checked,
                          },
                        })
                      }
                    />
                    Stock Splits
                  </label>
                </div>
              </div>
              <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
                <button type="submit" disabled={loading} className="submit-btn">
                  Update
                </button>
                <button
                  type="button"
                  onClick={() => setEditingWatchlist(null)}
                  className="submit-btn"
                  style={{ background: "#999" }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showSettingsModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowSettingsModal(false)}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Configure Event Types</h3>
            <p className="modal-description">
              Choose which event types to track in this watchlist:
            </p>
            <div className="checkbox-grid">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_earnings_announcement}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_earnings_announcement: e.target.checked,
                    })
                  }
                />
                Earnings
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_dividend_ex}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_dividend_ex: e.target.checked,
                    })
                  }
                />
                Div. Ex-Date
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_dividend_declaration}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_dividend_declaration: e.target.checked,
                    })
                  }
                />
                Div. Declaration
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_dividend_record}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_dividend_record: e.target.checked,
                    })
                  }
                />
                Div. Record
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_dividend_payment}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_dividend_payment: e.target.checked,
                    })
                  }
                />
                Div. Payment
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={eventSettings.include_stock_split}
                  onChange={(e) =>
                    setEventSettings({
                      ...eventSettings,
                      include_stock_split: e.target.checked,
                    })
                  }
                />
                Stock Splits
              </label>
            </div>
            <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
              <button
                onClick={saveEventSettings}
                disabled={loading}
                className="submit-btn"
              >
                Save Settings
              </button>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="submit-btn"
                style={{ background: "#999" }}
              >
                Skip
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedWatchlist && (
        <>
          <h3>Stocks in Watchlist</h3>
          <form onSubmit={followStock} className="api-form">
            <div className="form-group">
              <label>Follow Stock (Ticker):</label>
              <input
                type="text"
                value={tickerToFollow}
                onChange={(e) => setTickerToFollow(e.target.value)}
                placeholder="e.g., AAPL"
                required
              />
            </div>
            <button type="submit" disabled={loading} className="submit-btn">
              Follow Stock
            </button>
          </form>

          {follows.length === 0 ? (
            <p>No stocks followed yet.</p>
          ) : (
            <div className="follows-list">
              {follows.map((stock) => (
                <div key={stock.ticker} className="follow-item">
                  <div>
                    <strong>{stock.ticker}</strong>
                    <p className="small">{stock.name}</p>
                  </div>
                  <button
                    onClick={() => unfollowStock(stock.ticker)}
                    className="small-btn danger"
                  >
                    Unfollow
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}

      {response && (
        <div className="response-box">
          <strong>Response:</strong>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default WatchlistsPanel;
