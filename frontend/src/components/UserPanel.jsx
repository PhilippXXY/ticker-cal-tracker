import React, { useState, useEffect } from "react";
import axios from "axios";

function UserPanel({ apiUrl, token }) {
  const [profile, setProfile] = useState(null);
  const [updateEmail, setUpdateEmail] = useState("");
  const [updatePassword, setUpdatePassword] = useState("");
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

    // Build payload with only non-empty fields
    const payload = {};
    if (updateEmail && updateEmail.trim()) {
      payload.email = updateEmail.trim();
    }
    if (updatePassword && updatePassword.trim()) {
      payload.password = updatePassword;
    }

    // Validate that at least one field is provided
    if (Object.keys(payload).length === 0) {
      setError("Please provide at least one field to update.");
      setLoading(false);
      return;
    }

    try {
      const res = await axios.put(`${apiUrl}/api/user/profile`, payload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfile(res.data);
      // Clear password field after successful update
      setUpdatePassword("");
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
            placeholder="Enter new email (optional)"
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            value={updatePassword}
            onChange={(e) => setUpdatePassword(e.target.value)}
            placeholder="Enter new password (optional)"
          />
        </div>
        <p className="form-hint">
          Update one or both fields. At least one field must be provided.
        </p>
        <button type="submit" disabled={loading} className="submit-btn">
          Update Profile
        </button>
      </form>

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default UserPanel;
