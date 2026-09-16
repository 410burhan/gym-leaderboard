import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/AuthContext";
import { ProfileProvider, useProfile } from "./lib/ProfileContext";
import Login from "./pages/Login";
import ProfileSetup from "./pages/ProfileSetup";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import PostFeed from "./pages/PostFeed";
import NewPost from "./pages/NewPost";
import PostDetail from "./pages/PostDetail";
import "./App.css";

function RequireAuth({ children }) {
  const { session, loading } = useAuth();
  if (loading) return <div className="page">Loading...</div>;
  if (!session) return <Navigate to="/login" replace />;
  return children;
}

// Gate for pages that need a completed profile (username chosen) - most of
// the app. If the user is signed in but hasn't created a profile yet, every
// route except /setup-profile bounces them there first.
function RequireProfile({ children }) {
  const { profile, loading } = useProfile();
  if (loading) return <div className="page">Loading...</div>;
  if (!profile) return <Navigate to="/setup-profile" replace />;
  return children;
}

function Shell() {
  const { session, loading } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={loading ? <div className="page">Loading...</div> : session ? <Navigate to="/" replace /> : <Login />}
      />
      <Route path="/setup-profile" element={<RequireAuth><ProfileSetup /></RequireAuth>} />
      <Route path="/" element={<RequireAuth><RequireProfile><Feed /></RequireProfile></RequireAuth>} />
      <Route path="/u/:username" element={<RequireAuth><RequireProfile><Profile /></RequireProfile></RequireAuth>} />
      <Route path="/posts" element={<RequireAuth><RequireProfile><PostFeed /></RequireProfile></RequireAuth>} />
      <Route path="/posts/new" element={<RequireAuth><RequireProfile><NewPost /></RequireProfile></RequireAuth>} />
      <Route path="/posts/:postId" element={<RequireAuth><RequireProfile><PostDetail /></RequireProfile></RequireAuth>} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ProfileProvider>
        <BrowserRouter>
          <Shell />
        </BrowserRouter>
      </ProfileProvider>
    </AuthProvider>
  );
}
