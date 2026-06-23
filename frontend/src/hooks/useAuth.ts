import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { useMemo, useCallback } from 'react';
import { loginRequest } from '../config/authConfig';
import type { AppRole, AuthUser } from '../types/auth';

const ROLE_MAP: Record<string, AppRole> = {
  [import.meta.env.VITE_AZURE_GROUP_HR || '']: 'HR',
  [import.meta.env.VITE_AZURE_GROUP_IT || '']: 'IT',
  [import.meta.env.VITE_AZURE_GROUP_ADMIN || '']: 'Admin',
};

function mapGroupsToRoles(groups: string[]): AppRole[] {
  const roles: AppRole[] = [];
  for (const groupId of groups) {
    const role = ROLE_MAP[groupId];
    if (role) {
      roles.push(role);
    }
  }
  return roles;
}

export function useAuth() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const account = accounts[0] ?? null;

  const roles: AppRole[] = useMemo(() => {
    if (!account) return [];

    const claims = account.idTokenClaims as
      | Record<string, unknown>
      | undefined;

    if (claims?.roles && Array.isArray(claims.roles)) {
      return claims.roles as AppRole[];
    }

    if (claims?.groups && Array.isArray(claims.groups)) {
      return mapGroupsToRoles(claims.groups as string[]);
    }

    return [];
  }, [account]);

  const user: AuthUser | null = useMemo(() => {
    if (!account) return null;
    return {
      name: account.name ?? '',
      email: account.username ?? '',
      roles,
    };
  }, [account, roles]);

  const login = useCallback(async () => {
    await instance.loginRedirect(loginRequest);
  }, [instance]);

  const logout = useCallback(async () => {
    await instance.logoutRedirect({
      postLogoutRedirectUri: window.location.origin,
    });
  }, [instance]);

  const getAccessToken = useCallback(async (): Promise<string> => {
    if (!account) {
      throw new Error('Nenhuma conta autenticada encontrada');
    }

    const response = await instance.acquireTokenSilent({
      ...loginRequest,
      account,
    });

    return response.accessToken;
  }, [instance, account]);

  return {
    isAuthenticated,
    account,
    user,
    roles,
    login,
    logout,
    getAccessToken,
  };
}
