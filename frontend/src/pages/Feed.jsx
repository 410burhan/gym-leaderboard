import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Check, X } from "lucide-react";
import { api, BODY_PARTS } from "../lib/api";
import Avatar from "../components/Avatar";

export default function Feed() {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Picking a body part just stages it - nothing is logged until the
  // person explicitly confirms, so a stray tap can't silently log a workout.
  const [pendingPart, setPendingPart] = useState(null);
  const [duration, setDuration] = useState(45);
  const [busy, setBusy] = useState(false);
  const [justLogged, setJustLogged] = useState(false);

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

  function selectPart(part) {
    setPendingPart(part);
    setJustLogged(false);
  }

  function cancelSelection() {
    setPendingPart(null);
  }

  async function confirmLog() {
    setBusy(true);
    setError("");
    try {
      await api.logWorkout({ body_part: pendingPart, duration_minutes: Number(duration) });
      await refresh();
      setJustLogged(true);
      setPendingPart(null);
      setTimeout(() => setJustLogged(false), 2500);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <section className="quick-log">
        <div className="quick-log-head">
          <h2>Log today's session</h2>
        </div>

        <div className="chip-row">
          {BODY_PARTS.map((part) => (
            <button
              key={part}
              className={`chip${pendingPart === part ? " chip-active" : ""}`}
              onClick={() => selectPart(part)}
            >
              {part}
            </button>
          ))}
        </div>

        {pendingPart && (
          <div className="log-confirm">
            <label className="duration-row">
              <span>Duration</span>
              <input
                type="range"
                min={0}
                max={120}
                step={5}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
              <span className="duration-value">{duration}m</span>
            </label>

            <p className="log-confirm-text">
              Log <strong>{pendingPart}</strong> for {duration} minutes?
            </p>

            <div className="log-confirm-actions">
              <button onClick={cancelSelection} disabled={busy} className="btn-secondary">
                <X size={16} /> Cancel
              </button>
              <button onClick={confirmLog} disabled={busy}>
                <Check size={16} /> {busy ? "Logging..." : "Confirm"}
              </button>
            </div>
          </div>
        )}

        {justLogged && <p className="log-success">Logged \u2713</p>}
      </section>

      {error && <p className="error-text">{error}</p>}

      <h2 className="section-heading">What your friends hit</h2>

      {loading ? (
        <p className="empty-text">Loading...</p>
      ) : feed.length === 0 ? (
        <p className="empty-text">
          Nothing here yet - use Search to find and follow people.
        </p>
      ) : (
        <ul className="feed-list">
          {feed.map((entry) => (
            <li key={entry.workout.id} className="feed-card">
              <Link to={`/u/${entry.username}`}>
                <Avatar name={entry.display_name} url={entry.avatar_url} size={38} />
              </Link>
              <div className="feed-card-body">
                <Link to={`/u/${entry.username}`} className="feed-name">{entry.display_name}</Link>
                <span className="feed-detail">
                  hit <strong>{entry.workout.body_part}</strong>
                  {entry.workout.duration_minutes ? ` \u00b7 ${entry.workout.duration_minutes}m` : ""}
                </span>
              </div>
              <span className="feed-date">{entry.workout.logged_on}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
