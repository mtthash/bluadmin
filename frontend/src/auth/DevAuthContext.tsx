import React, { createContext, useContext, useMemo } from 'react';
import type { AuthUser } from '../types/auth';

interface DevAuthContextValue {
  isAuthenticated: boolean;
  user: AuthUser;
  permissions: string[];
  login: (username?: string, password?: string) => Promise<void>;
  logout: () => void;
  getAccessToken: () => Promise<string>;
  isLoading: boolean;
}

const ALL_PERMISSIONS = [
  'employee:create', 'employee:read', 'employee:list',
  'employee:disable', 'department:read', 'audit:read', 'user:manage',
];

const DEV_USER: AuthUser = {
  name: 'Dev Admin',
  email: 'admin@bluadmin.local',
  role: 'admin',
  permissions: ALL_PERMISSIONS,
};

const DevAuthCtx = createContext<DevAuthContextValue | null>(null);

export const DevAuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const value = useMemo<DevAuthContextValue>(
    () => ({
      isAuthenticated: true,
      user: DEV_USER,
      permissions: ALL_PERMISSIONS,
      login: async () => {},
      logout: () => {
        window.location.href = '/login';
      },
      getAccessToken: async () => 'dev-bypass-token',
      isLoading: false,
    }),
    [],
  );

  return <DevAuthCtx.Provider value={value}>{children}</DevAuthCtx.Provider>;
};

export function useDevAuth(): DevAuthContextValue | null {
  return useContext(DevAuthCtx);
}
