import React, { useState, useEffect } from "react";
import axios from "axios";

function UserPanel({ apiUrl, token }) {
  const [profile, setProfile] = useState(null);
  const [updateEmail, setUpdateEmail] = useState("");
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${apiUrl}/api/user/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfile(res.data);
      setUpdateEmail(res.data.email || "");
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.put(
        `${apiUrl}/api/user/profile`,
        { email: updateEmail },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse(res.data);
      setProfile(res.data);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [apiUrl, token]);

  return (
    <div className="panel">
      <h2>User Profile</h2>

      <button onClick={fetchProfile} disabled={loading} className="action-btn">
        Refresh Profile
      </button>

      {profile && (
        <div className="info-box">
          <h3>Current Profile</h3>
          {profile.id && (
            <p>
              <strong>ID:</strong> {profile.id}
            </p>
          )}
          {profile.username && (
            <p>
              <strong>Username:</strong> {profile.username}
            </p>
          )}
          <p>
            <strong>Email:</strong> {profile.email || "Not set"}
          </p>
          <p>
            <strong>Created:</strong>{" "}
            {new Date(profile.created_at).toLocaleString()}
          </p>
        </div>
      )}

      <h3>Update Profile</h3>
      <form onSubmit={handleUpdateProfile} className="api-form">
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            value={updateEmail}
            onChange={(e) => setUpdateEmail(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading} className="submit-btn">
          Update Email
        </button>
      </form>

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}

      {response && (
        <div className="response-box">
          <strong>Update Response:</strong>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default UserPanel;
