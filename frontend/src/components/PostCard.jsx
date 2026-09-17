import { useState } from "react";
import { Link } from "react-router-dom";
import { Heart, MessageCircle } from "lucide-react";
import { api } from "../lib/api";
import Avatar from "./Avatar";

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
      // state simply stays as it was if the request fails
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="post-card">
      {showAuthor && (
        <Link to={`/u/${post.username}`} className="post-author">
          <Avatar name={post.display_name} url={post.avatar_url} size={32} />
          <span>{post.display_name}</span>
        </Link>
      )}
      <video src={post.video_url} controls playsInline className="post-video" />
      {post.caption && <p className="post-caption">{post.caption}</p>}
      <div className="post-actions">
        <button onClick={toggleLike} disabled={busy} className={liked ? "like-btn liked" : "like-btn"}>
          <Heart size={20} fill={liked ? "currentColor" : "none"} /> {likeCount}
        </button>
        <Link to={`/posts/${post.id}`} className="comment-link">
          <MessageCircle size={19} /> {post.comment_count}
        </Link>
      </div>
    </div>
  );
}
