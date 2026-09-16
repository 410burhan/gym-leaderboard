import { supabase } from "./supabase";

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Thin wrapper around fetch that attaches the current Supabase session's
 * access token as a Bearer header - this is the token the backend verifies
 * in app/auth.py on every protected route.
 */
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
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  createGroup: (name, displayName) =>
    request("/groups", { method: "POST", body: JSON.stringify({ name, display_name: displayName }) }),
  joinGroup: (inviteCode, displayName) =>
    request("/groups/join", {
      method: "POST",
      body: JSON.stringify({ invite_code: inviteCode, display_name: displayName }),
    }),
  listMyGroups: () => request("/groups"),
  logWorkout: (groupId, workout) =>
    request(`/groups/${groupId}/workouts`, { method: "POST", body: JSON.stringify(workout) }),
  listWorkouts: (groupId) => request(`/groups/${groupId}/workouts`),
  deleteWorkout: (groupId, workoutId) =>
    request(`/groups/${groupId}/workouts/${workoutId}`, { method: "DELETE" }),
  getLeaderboard: (groupId) => request(`/groups/${groupId}/leaderboard`),
};
