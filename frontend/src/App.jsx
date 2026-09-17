import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/AuthContext";
import { ProfileProvider, useProfile } from "./lib/ProfileContext";
import AppShell from "./components/AppShell";
import Login from "./pages/Login";
import ProfileSetup from "./pages/ProfileSetup";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import PostFeed from "./pages/PostFeed";
import NewPost from "./pages/NewPost";
import PostDetail from "./pages/PostDetail";
import Search from "./pages/Search";
import "./App.css";

function RequireAuth({ children }) {
  const { session, loading } = useAuth();
  if (loading) return <div className="page-loading">Loading...</div>;
  if (!session) return <Navigate to="/login" replace />;
  return children;
}

function RequireProfile({ children }) {
  const { profile, loading, error } = useProfile();
  if (loading) return <div className="page-loading">Loading...</div>;
  if (error) return <div className="page-loading error-text">Couldn't reach the server: {error}</div>;
  if (!profile) return <Navigate to="/setup-profile" replace />;
  return children;
}

function Shell() {
  const { session, loading } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={loading ? <div className="page-loading">Loading...</div> : session ? <Navigate to="/" replace /> : <Login />}
      />
      <Route path="/setup-profile" element={<RequireAuth><ProfileSetup /></RequireAuth>} />

      <Route
        element={
          <RequireAuth>
            <RequireProfile>
              <AppShell />
            </RequireProfile>
          </RequireAuth>
        }
      >
        <Route path="/" element={<Feed />} />
        <Route path="/search" element={<Search />} />
        <Route path="/u/:username" element={<Profile />} />
        <Route path="/posts" element={<PostFeed />} />
        <Route path="/posts/new" element={<NewPost />} />
        <Route path="/posts/:postId" element={<PostDetail />} />
      </Route>
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
