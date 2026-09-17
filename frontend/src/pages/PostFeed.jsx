import { useEffect, useState } from "react";
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
    <div>
      <h2 className="section-heading" style={{ marginTop: 0 }}>PRs</h2>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p className="empty-text">Loading...</p>
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
