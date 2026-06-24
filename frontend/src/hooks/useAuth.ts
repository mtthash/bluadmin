import { useAuthContext } from '../auth/AuthProvider';
import { useDevAuth } from '../auth/DevAuthContext';

const isDevBypass = import.meta.env.VITE_DEV_AUTH_BYPASS === 'true';

function useLdapAuth() {
  const ctx = useAuthContext()!;
  return {
    isAuthenticated: ctx.isAuthenticated,
    user: ctx.user,
    permissions: ctx.permissions,
    login: ctx.login,
    logout: ctx.logout,
    getAccessToken: ctx.getAccessToken,
    isLoading: ctx.isLoading,
  };
}

function useDevBypassAuth() {
  const devAuth = useDevAuth()!;
  return {
    isAuthenticated: devAuth.isAuthenticated,
    user: devAuth.user,
    permissions: devAuth.permissions,
    login: devAuth.login,
    logout: devAuth.logout,
    getAccessToken: devAuth.getAccessToken,
    isLoading: false,
  };
}

export const useAuth = isDevBypass ? useDevBypassAuth : useLdapAuth;
