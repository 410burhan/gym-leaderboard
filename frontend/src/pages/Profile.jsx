import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useProfile } from "../lib/ProfileContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";

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

  if (loading) return <p className="empty-text">Loading...</p>;
  if (error) return <p className="error-text">{error}</p>;
  if (!profile) return null;

  return (
    <div>
      <div className="profile-header">
        <Avatar name={profile.display_name} url={profile.avatar_url} size={72} />
        <div className="profile-stats">
          <div><strong>{profile.workout_count}</strong><span>workouts</span></div>
          <div><strong>{profile.follower_count}</strong><span>followers</span></div>
          <div><strong>{profile.following_count}</strong><span>following</span></div>
        </div>
      </div>

      <div className="profile-identity">
        <h1>{profile.display_name}</h1>
        <p className="subtitle">@{profile.username}</p>
        {profile.bio && <p className="profile-bio">{profile.bio}</p>}
      </div>

      {!isOwnProfile && (
        <button
          onClick={toggleFollow}
          disabled={busy}
          className={profile.is_following ? "btn-secondary follow-btn-full" : "follow-btn-full"}
        >
          {busy ? "..." : profile.is_following ? "Following" : "Follow"}
        </button>
      )}

      <h2 className="section-heading">Recent workouts</h2>
      {workouts.length === 0 ? (
        <p className="empty-text">No workouts logged yet.</p>
      ) : (
        <ul className="feed-list">
          {workouts.map((w) => (
            <li key={w.id} className="feed-card feed-card-compact">
              <span className="feed-detail">
                <strong>{w.body_part}</strong>
                {w.duration_minutes ? ` \u00b7 ${w.duration_minutes}m` : ""}
              </span>
              <span className="feed-date">{w.logged_on}</span>
            </li>
          ))}
        </ul>
      )}

      <h2 className="section-heading">PRs</h2>
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
