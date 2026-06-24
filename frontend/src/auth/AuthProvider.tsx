import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { API_BASE_URL } from '../config/apiConfig';
import { DevAuthProvider } from './DevAuthContext';
import type { AppRole, AuthUser } from '../types/auth';

const isDevBypass = import.meta.env.VITE_DEV_AUTH_BYPASS === 'true';

export interface AuthContextValue {
  isAuthenticated: boolean;
  user: AuthUser | null;
  permissions: string[];
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  getAccessToken: () => Promise<string>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const useAuthContext = () => useContext(AuthContext);

const LdapAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState<AuthUser | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp * 1000 < Date.now()) {
          handleLogout();
        } else {
          const role = (payload.role || 'viewer') as AppRole;
          const perms = payload.permissions || [];
          setUser({
            name: payload.display_name || '',
            email: payload.sub || '',
            role,
            permissions: perms,
          });
          setPermissions(perms);
        }
      } catch {
        handleLogout();
      }
    }
    setIsLoading(false);
  }, [token]);

  const handleLogin = useCallback(async (username: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || 'Falha na autenticacao');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    setToken(data.access_token);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
    setPermissions([]);
  }, []);

  const getAccessToken = useCallback(async () => {
    if (!token) throw new Error('Not authenticated');
    return token;
  }, [token]);

  return (
    <AuthContext.Provider value={{
      isAuthenticated: !!token && !!user,
      user,
      permissions,
      login: handleLogin,
      logout: handleLogout,
      getAccessToken,
      isLoading,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  if (isDevBypass) {
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }
  return <LdapAuthProvider>{children}</LdapAuthProvider>;
};
