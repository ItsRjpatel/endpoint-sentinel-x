import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { apiClient } from "../api/client";

interface User {
  id: string;
  email: string;
  role?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("sentinelx_token"));
  const [user, setUser] = useState<User | null>(null);

  // Set the token provider for the API client once, or whenever token changes
  useEffect(() => {
    apiClient.setTokenProvider(() => token);
  }, [token]);

  // In a real app, you would decode the JWT or fetch /api/v1/auth/me
  // For Sprint 5.1 MVP, we simulate decoding
  useEffect(() => {
    if (token) {
      setUser({ id: "1", email: "admin@sentinelx.local", role: "admin" });
    } else {
      setUser(null);
    }
  }, [token]);

  const login = useCallback((newToken: string) => {
    localStorage.setItem("sentinelx_token", newToken);
    setToken(newToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("sentinelx_token");
    setToken(null);
  }, []);

  const getToken = useCallback(() => {
    return token;
  }, [token]);

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!token, user, token, login, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
