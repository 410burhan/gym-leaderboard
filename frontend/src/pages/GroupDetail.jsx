import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";

const WORKOUT_TYPES = ["push", "pull", "legs", "cardio", "full body", "rest day"];

export default function GroupDetail() {
  const { groupId } = useParams();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [workoutType, setWorkoutType] = useState(WORKOUT_TYPES[0]);
  const [duration, setDuration] = useState(45);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      setLeaderboard(await api.getLeaderboard(groupId));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupId]);

  async function handleLog(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.logWorkout(groupId, { workout_type: workoutType, duration_minutes: Number(duration) });
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
        <Link to="/" className="link-button">&larr; All groups</Link>
      </header>

      <h1>Leaderboard</h1>
      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Name</th>
              <th>Workouts</th>
              <th>Total minutes</th>
              <th>Streak</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, i) => (
              <tr key={entry.user_id}>
                <td>{i + 1}</td>
                <td>{entry.display_name}</td>
                <td>{entry.workout_count}</td>
                <td>{entry.total_minutes}</td>
                <td>{entry.current_streak_days > 0 ? `${entry.current_streak_days}d` : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <form onSubmit={handleLog} className="panel log-form">
        <h2>Log a workout</h2>
        <label>
          Type
          <select value={workoutType} onChange={(e) => setWorkoutType(e.target.value)}>
            {WORKOUT_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
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
    </div>
  );
}
