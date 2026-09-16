import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import PostCard from "../components/PostCard";

export default function PostFeed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getPostFeed()
      .then(setPosts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <h1>PRs</h1>
        <div className="header-links">
          <Link to="/posts/new" className="link-button">Post a PR</Link>
          <Link to="/" className="link-button">Feed</Link>
        </div>
      </header>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p>Loading...</p>
      ) : posts.length === 0 ? (
        <p className="empty-text">No PRs yet from people you follow.</p>
      ) : (
        <div className="post-list">
          {posts.map((p) => (
            <PostCard key={p.id} post={p} />
          ))}
        </div>
      )}
    </div>
  );
}
