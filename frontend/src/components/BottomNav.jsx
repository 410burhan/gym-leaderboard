import { NavLink } from "react-router-dom";
import { Home, Search, PlaySquare, PlusSquare, User } from "lucide-react";
import { useProfile } from "../lib/ProfileContext";

export default function BottomNav() {
  const { profile } = useProfile();

  return (
    <nav className="bottom-nav">
      <NavLink to="/" end className={({ isActive }) => `nav-tab${isActive ? " active" : ""}`}>
        <Home size={23} strokeWidth={2} />
      </NavLink>

      <NavLink to="/search" className={({ isActive }) => `nav-tab${isActive ? " active" : ""}`}>
        <Search size={23} strokeWidth={2} />
      </NavLink>

      <NavLink to="/posts/new" className="nav-tab nav-tab-add">
        <PlusSquare size={27} strokeWidth={2} />
      </NavLink>

      <NavLink to="/posts" className={({ isActive }) => `nav-tab${isActive ? " active" : ""}`}>
        <PlaySquare size={23} strokeWidth={2} />
      </NavLink>

      <NavLink
        to={profile ? `/u/${profile.username}` : "/"}
        className={({ isActive }) => `nav-tab${isActive ? " active" : ""}`}
      >
        <User size={23} strokeWidth={2} />
      </NavLink>
    </nav>
  );
}
