import { supabase } from "./supabase";

const API_URL = import.meta.env.VITE_API_URL;
const VIDEO_BUCKET = "post-videos";

async function request(path, options = {}) {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.detail || `Request failed: ${res.status}`);
    err.status = res.status;
    throw err;
  }

  if (res.status === 204) return null;
  return res.json();
}

export const BODY_PARTS = ["push", "pull", "legs", "core", "cardio", "full body", "rest day"];

export const api = {
  // Profiles
  createProfile: (username, displayName, bio) =>
    request("/profiles", {
      method: "POST",
      body: JSON.stringify({ username, display_name: displayName, bio: bio || null }),
    }),
  getMyProfile: () => request("/profiles/me"),
  updateMyProfile: (updates) =>
    request("/profiles/me", { method: "PATCH", body: JSON.stringify(updates) }),
  getProfile: (username) => request(`/profiles/${username}`),
  searchProfiles: (q) => request(`/profiles/search?q=${encodeURIComponent(q)}`),
  getUserWorkouts: (username) => request(`/profiles/${username}/workouts`),

  // Follows
  follow: (username) => request(`/follows/${username}`, { method: "POST" }),
  unfollow: (username) => request(`/follows/${username}`, { method: "DELETE" }),

  // Workouts
  logWorkout: (workout) => request("/workouts", { method: "POST", body: JSON.stringify(workout) }),
  getMyWorkouts: () => request("/workouts/me"),
  deleteWorkout: (workoutId) => request(`/workouts/${workoutId}`, { method: "DELETE" }),

  // Feed
  getFeed: () => request("/feed"),

  // Video upload - straight to Supabase Storage, never through the backend.
  // File lives at post-videos/{userId}/{uuid}.{ext}; RLS on the bucket
  // restricts each user to writing inside their own folder.
  uploadVideo: async (file, userId) => {
    const ext = file.name.split(".").pop();
    const path = `${userId}/${crypto.randomUUID()}.${ext}`;

    const { error } = await supabase.storage.from(VIDEO_BUCKET).upload(path, file);
    if (error) throw new Error(error.message);

    const { data } = supabase.storage.from(VIDEO_BUCKET).getPublicUrl(path);
    return data.publicUrl;
  },

  // Posts
  createPost: (videoUrl, caption, workoutId) =>
    request("/posts", {
      method: "POST",
      body: JSON.stringify({ video_url: videoUrl, caption: caption || null, workout_id: workoutId || null }),
    }),
  getPostFeed: () => request("/posts/feed"),
  getPost: (postId) => request(`/posts/${postId}`),
  deletePost: (postId) => request(`/posts/${postId}`, { method: "DELETE" }),
  getUserPosts: (username) => request(`/profiles/${username}/posts`),

  // Likes
  likePost: (postId) => request(`/posts/${postId}/like`, { method: "POST" }),
  unlikePost: (postId) => request(`/posts/${postId}/like`, { method: "DELETE" }),

  // Comments
  addComment: (postId, body) =>
    request(`/posts/${postId}/comments`, { method: "POST", body: JSON.stringify({ body }) }),
  getComments: (postId) => request(`/posts/${postId}/comments`),
  deleteComment: (commentId) => request(`/comments/${commentId}`, { method: "DELETE" }),
};
