import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export default function NewPost() {
  const { session } = useAuth();
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [caption, setCaption] = useState("");
  const [workoutId, setWorkoutId] = useState("");
  const [myWorkouts, setMyWorkouts] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getMyWorkouts().then(setMyWorkouts).catch(() => {});
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      setError("Pick a video first");
      return;
    }
    setUploading(true);
    setError("");
    try {
      const videoUrl = await api.uploadVideo(file, session.user.id);
      const post = await api.createPost(videoUrl, caption, workoutId || null);
      navigate(`/posts/${post.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <h1>Post a PR</h1>
      <p className="subtitle">Share a video, let people cheer you on.</p>

      <form onSubmit={handleSubmit} className="panel" style={{ maxWidth: 480 }}>
        <label>
          Video
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
        </label>

        <label>
          Caption
          <input
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            maxLength={280}
            placeholder="225 for 3, felt heavy but I got it"
          />
        </label>

        {myWorkouts.length > 0 && (
          <label>
            Link to a workout (optional)
            <select value={workoutId} onChange={(e) => setWorkoutId(e.target.value)}>
              <option value="">None</option>
              {myWorkouts.slice(0, 10).map((w) => (
                <option key={w.id} value={w.id}>
                  {w.logged_on} - {w.body_part}
                </option>
              ))}
            </select>
          </label>
        )}

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={uploading}>
          {uploading ? "Uploading..." : "Post it"}
        </button>
      </form>
    </div>
  );
}
