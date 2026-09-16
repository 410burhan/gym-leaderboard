import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { supabase } from "../lib/supabase";

export default function Groups() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [newGroupName, setNewGroupName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      setGroups(await api.listMyGroups());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createGroup(newGroupName, displayName);
      setNewGroupName("");
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleJoin(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.joinGroup(joinCode, displayName);
      setJoinCode("");
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Your groups</h1>
        <button className="link-button" onClick={() => supabase.auth.signOut()}>
          Sign out
        </button>
      </header>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p>Loading...</p>
      ) : groups.length === 0 ? (
        <p className="empty-text">No groups yet - create one or join with a friend's code below.</p>
      ) : (
        <ul className="group-list">
          {groups.map((g) => (
            <li key={g.id}>
              <Link to={`/groups/${g.id}`} className="group-card">
                <span className="group-name">{g.name}</span>
                <span className="invite-code">Code: {g.invite_code}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <div className="forms-row">
        <form onSubmit={handleCreate} className="panel">
          <h2>Create a group</h2>
          <label>
            Group name
            <input value={newGroupName} onChange={(e) => setNewGroupName(e.target.value)} required />
          </label>
          <label>
            Your display name
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          </label>
          <button type="submit" disabled={busy}>Create</button>
        </form>

        <form onSubmit={handleJoin} className="panel">
          <h2>Join with a code</h2>
          <label>
            Invite code
            <input
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              maxLength={6}
              required
            />
          </label>
          <label>
            Your display name
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          </label>
          <button type="submit" disabled={busy}>Join</button>
        </form>
      </div>
    </div>
  );
}
