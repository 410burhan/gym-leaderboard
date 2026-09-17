import { Outlet, Link } from "react-router-dom";
import { LogOut } from "lucide-react";
import { supabase } from "../lib/supabase";
import BottomNav from "./BottomNav";

export default function AppShell() {
  return (
    <div className="app-frame">
      <header className="app-topbar">
        <Link to="/" className="app-wordmark">SetTogether</Link>
        <button className="icon-button" onClick={() => supabase.auth.signOut()} aria-label="Sign out">
          <LogOut size={20} />
        </button>
      </header>

      <main className="app-content">
        <Outlet />
      </main>

      <BottomNav />
    </div>
  );
}
