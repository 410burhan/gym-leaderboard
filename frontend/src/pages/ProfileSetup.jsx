import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useProfile } from "../lib/ProfileContext";

export default function ProfileSetup() {
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { refresh } = useProfile();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createProfile(username.toLowerCase(), displayName, bio);
      await refresh();
      navigate("/");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <h1>Choose your identity</h1>
        <p className="subtitle">This is how people find and follow you.</p>

        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="lowercase, no spaces"
              pattern="[a-z0-9_]{3,30}"
              required
            />
          </label>
          <label>
            Display name
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          </label>
          <label>
            Bio (optional)
            <input value={bio} onChange={(e) => setBio(e.target.value)} maxLength={160} />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" disabled={busy}>{busy ? "Creating..." : "Continue"}</button>
        </form>
      </div>
    </div>
  );
}
