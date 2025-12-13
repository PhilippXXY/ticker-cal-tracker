import React, { useState } from "react";

function CalendarPanel({ apiUrl }) {
  const [token, setToken] = useState("");
  const [calendarUrl, setCalendarUrl] = useState("");

  const generateUrl = (e) => {
    e.preventDefault();
    const url = `${apiUrl}/api/cal/${token}.ics`;
    setCalendarUrl(url);
  };

  return (
    <div className="panel">
      <h2>Calendar Subscription</h2>

      <p className="info-text">
        Enter a calendar token to generate the iCalendar (.ics) subscription
        URL. This endpoint does not require authentication.
      </p>

      <form onSubmit={generateUrl} className="api-form">
        <div className="form-group">
          <label>Calendar Token:</label>
          <input
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Enter calendar token"
            required
          />
        </div>
        <button type="submit" className="submit-btn">
          Generate Calendar URL
        </button>
      </form>

      {calendarUrl && (
        <div className="info-box">
          <h3>Calendar Subscription URL</h3>
          <p className="calendar-url">
            <a href={calendarUrl} target="_blank" rel="noopener noreferrer">
              {calendarUrl}
            </a>
          </p>
          <p className="small">
            Copy this URL to subscribe in your calendar application (Google
            Calendar, Apple Calendar, Outlook, etc.)
          </p>
        </div>
      )}
    </div>
  );
}

export default CalendarPanel;
