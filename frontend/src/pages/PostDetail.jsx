import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { api } from "../lib/api";
import { useProfile } from "../lib/ProfileContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";

export default function PostDetail() {
  const { postId } = useParams();
  const { profile } = useProfile();
  const navigate = useNavigate();

  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [commentBody, setCommentBody] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const [p, c] = await Promise.all([api.getPost(postId), api.getComments(postId)]);
      setPost(p);
      setComments(c);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId]);

  async function handleComment(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.addComment(postId, commentBody);
      setCommentBody("");
      const c = await api.getComments(postId);
      setComments(c);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDeletePost() {
    if (!confirm("Delete this post?")) return;
    await api.deletePost(postId);
    navigate("/posts");
  }

  if (loading) return <p className="empty-text">Loading...</p>;
  if (error) return <p className="error-text">{error}</p>;
  if (!post) return null;

  const isOwnPost = profile && profile.username === post.username;

  return (
    <div>
      <button className="back-button" onClick={() => navigate(-1)}>
        <ChevronLeft size={20} /> Back
      </button>

      <PostCard post={post} />

      {isOwnPost && (
        <button onClick={handleDeletePost} className="btn-secondary" style={{ marginTop: "0.75rem" }}>
          Delete post
        </button>
      )}

      <h2 className="section-heading">Comments</h2>

      <form onSubmit={handleComment} className="comment-form">
        <input
          value={commentBody}
          onChange={(e) => setCommentBody(e.target.value)}
          placeholder="Say something..."
          maxLength={500}
          required
        />
        <button type="submit" disabled={busy}>Post</button>
      </form>

      {comments.length === 0 ? (
        <p className="empty-text">No comments yet.</p>
      ) : (
        <ul className="comment-list">
          {comments.map((c) => (
            <li key={c.id} className="comment-item">
              <Link to={`/u/${c.username}`}>
                <Avatar name={c.display_name} url={c.avatar_url} size={30} />
              </Link>
              <div>
                <Link to={`/u/${c.username}`} className="comment-author">{c.display_name}</Link>{" "}
                <span className="comment-body">{c.body}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
