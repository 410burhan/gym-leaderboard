import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { api } from "./api";

const ProfileContext = createContext(null);

export function ProfileProvider({ children }) {
  const { session } = useAuth();
  const [profile, setProfile] = useState(undefined); // undefined = loading, null = no profile yet
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!session) {
      setProfile(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const p = await api.getMyProfile();
      setProfile(p);
    } catch {
      // 400 means "no profile yet" - that's an expected state, not an error to surface.
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, [session]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <ProfileContext.Provider value={{ profile, loading, refresh }}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  return useContext(ProfileContext);
}
