import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function PostCard({ post, showAuthor = true }) {
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [busy, setBusy] = useState(false);

  async function toggleLike() {
    setBusy(true);
    try {
      if (liked) {
        await api.unlikePost(post.id);
        setLiked(false);
        setLikeCount((c) => c - 1);
      } else {
        await api.likePost(post.id);
        setLiked(true);
        setLikeCount((c) => c + 1);
      }
    } catch {
      // Leave optimistic-free: on error, state just stays as it was.
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="post-card">
      {showAuthor && (
        <Link to={`/u/${post.username}`} className="post-author">
          {post.display_name}
        </Link>
      )}
      <video src={post.video_url} controls className="post-video" />
      {post.caption && <p className="post-caption">{post.caption}</p>}
      <div className="post-actions">
        <button
          onClick={toggleLike}
          disabled={busy}
          className={liked ? "like-btn liked" : "like-btn"}
        >
          {liked ? "\u2665" : "\u2661"} {likeCount}
        </button>
        <Link to={`/posts/${post.id}`} className="comment-link">
          {post.comment_count} comment{post.comment_count === 1 ? "" : "s"}
        </Link>
      </div>
    </div>
  );
}
