import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import { useProfile } from "../lib/ProfileContext";
import PostCard from "../components/PostCard";

export default function Profile() {
  const { username } = useParams();
  const { profile: myProfile } = useProfile();
  const [profile, setProfile] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const isOwnProfile = myProfile && myProfile.username === username;

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [p, w, posts] = await Promise.all([
        api.getProfile(username),
        api.getUserWorkouts(username),
        api.getUserPosts(username),
      ]);
      setProfile(p);
      setWorkouts(w);
      setPosts(posts);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  async function toggleFollow() {
    setBusy(true);
    try {
      if (profile.is_following) {
        await api.unfollow(username);
      } else {
        await api.follow(username);
      }
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <div className="page">Loading...</div>;
  if (error) return <div className="page"><p className="error-text">{error}</p></div>;
  if (!profile) return null;

  return (
    <div className="page">
      <header className="page-header">
        <Link to="/" className="link-button">&larr; Feed</Link>
      </header>

      <div className="profile-header">
        <div>
          <h1>{profile.display_name}</h1>
          <p className="subtitle">@{profile.username}</p>
          {profile.bio && <p className="profile-bio">{profile.bio}</p>}
        </div>
        {!isOwnProfile && (
          <button onClick={toggleFollow} disabled={busy} className={profile.is_following ? "btn-secondary" : ""}>
            {busy ? "..." : profile.is_following ? "Following" : "Follow"}
          </button>
        )}
      </div>

      <div className="profile-stats">
        <div><strong>{profile.workout_count}</strong><span>workouts</span></div>
        <div><strong>{profile.follower_count}</strong><span>followers</span></div>
        <div><strong>{profile.following_count}</strong><span>following</span></div>
      </div>

      <h2 className="feed-heading">Recent workouts</h2>
      {workouts.length === 0 ? (
        <p className="empty-text">No workouts logged yet.</p>
      ) : (
        <ul className="feed-list">
          {workouts.map((w) => (
            <li key={w.id} className="feed-card">
              <span className="feed-detail">
                <strong>{w.body_part}</strong>
                {w.duration_minutes ? ` for ${w.duration_minutes} min` : ""}
              </span>
              <span className="feed-date">{w.logged_on}</span>
            </li>
          ))}
        </ul>
      )}

      <h2 className="feed-heading">PRs</h2>
      {posts.length === 0 ? (
        <p className="empty-text">No PRs posted yet.</p>
      ) : (
        <div className="post-list">
          {posts.map((p) => (
            <PostCard key={p.id} post={p} showAuthor={false} />
          ))}
        </div>
      )}
    </div>
  );
}
