import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, BODY_PARTS } from "../lib/api";
import { useProfile } from "../lib/ProfileContext";
import { supabase } from "../lib/supabase";

export default function Feed() {
  const { profile } = useProfile();
  const navigate = useNavigate();
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [bodyPart, setBodyPart] = useState(BODY_PARTS[0]);
  const [duration, setDuration] = useState(45);
  const [busy, setBusy] = useState(false);

  const [followTarget, setFollowTarget] = useState("");
  const [followBusy, setFollowBusy] = useState(false);
  const [followError, setFollowError] = useState("");

  async function refresh() {
    setLoading(true);
    try {
      setFeed(await api.getFeed());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleLog(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.logWorkout({ body_part: bodyPart, duration_minutes: Number(duration) });
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleFollow(e) {
    e.preventDefault();
    setFollowBusy(true);
    setFollowError("");
    try {
      const uname = followTarget.trim().toLowerCase();
      await api.follow(uname);
      setFollowTarget("");
      navigate(`/u/${uname}`);
    } catch (e) {
      setFollowError(e.message);
    } finally {
      setFollowBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Feed</h1>
        <div className="header-links">
          <Link to="/posts" className="link-button">PRs</Link>
          {profile && (
            <Link to={`/u/${profile.username}`} className="link-button">My profile</Link>
          )}
          <button className="link-button" onClick={() => supabase.auth.signOut()}>Sign out</button>
        </div>
      </header>

      <form onSubmit={handleFollow} className="panel follow-form">
        <h2>Follow someone</h2>
        <label>
          Their username
          <input
            value={followTarget}
            onChange={(e) => setFollowTarget(e.target.value)}
            placeholder="e.g. friend123"
            required
          />
        </label>
        {followError && <p className="error-text">{followError}</p>}
        <button type="submit" disabled={followBusy}>{followBusy ? "Following..." : "Follow"}</button>
      </form>

      <form onSubmit={handleLog} className="panel log-form">
        <h2>Log a workout</h2>
        <label>
          Body part
          <select value={bodyPart} onChange={(e) => setBodyPart(e.target.value)}>
            {BODY_PARTS.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </label>
        <label>
          Duration (minutes)
          <input
            type="number"
            min={0}
            max={600}
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          />
        </label>
        <button type="submit" disabled={busy}>{busy ? "Logging..." : "Log it"}</button>
      </form>

      {error && <p className="error-text">{error}</p>}

      <h2 className="feed-heading">What your friends hit</h2>

      {loading ? (
        <p>Loading...</p>
      ) : feed.length === 0 ? (
        <p className="empty-text">
          Nothing here yet - follow people to see what they're training. Search a username on their profile page.
        </p>
      ) : (
        <ul className="feed-list">
          {feed.map((entry) => (
            <li key={entry.workout.id} className="feed-card">
              <Link to={`/u/${entry.username}`} className="feed-name">{entry.display_name}</Link>
              <span className="feed-detail">
                hit <strong>{entry.workout.body_part}</strong>
                {entry.workout.duration_minutes ? ` for ${entry.workout.duration_minutes} min` : ""}
              </span>
              <span className="feed-date">{entry.workout.logged_on}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
