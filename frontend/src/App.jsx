import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/AuthContext";
import Login from "./pages/Login";
import Groups from "./pages/Groups";
import GroupDetail from "./pages/GroupDetail";
import "./App.css";

function RequireAuth({ children }) {
  const { session, loading } = useAuth();
  if (loading) return <div className="page">Loading...</div>;
  if (!session) return <Navigate to="/login" replace />;
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
      <Route path="/" element={<RequireAuth><Groups /></RequireAuth>} />
      <Route path="/groups/:groupId" element={<RequireAuth><GroupDetail /></RequireAuth>} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </AuthProvider>
  );
}
