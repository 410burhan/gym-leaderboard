import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { api } from "./api";

const ProfileContext = createContext(null);

export function ProfileProvider({ children }) {
  const { session, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    if (authLoading) {
      return;
    }
    if (!session) {
      setProfile(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const p = await api.getMyProfile();
      setProfile(p);
    } catch (e) {
      if (e.status === 400) {
        setProfile(null);
      } else {
        setError(e.message || "Couldn't load your profile");
      }
    } finally {
      setLoading(false);
    }
  }, [session, authLoading]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <ProfileContext.Provider value={{ profile, loading, error, refresh }}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  return useContext(ProfileContext);
}