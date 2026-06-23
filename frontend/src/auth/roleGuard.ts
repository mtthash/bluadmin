import type { AppRole } from '../types/auth';

export function hasRole(userRoles: string[], required: AppRole): boolean {
  return userRoles.includes(required);
}

export function hasAnyRole(userRoles: string[], required: AppRole[]): boolean {
  return required.some((role) => userRoles.includes(role));
}

export function canCreateEmployee(roles: string[]): boolean {
  return hasAnyRole(roles, ['HR', 'IT', 'Admin']);
}

export function canDisableEmployee(roles: string[]): boolean {
  return hasAnyRole(roles, ['IT', 'Admin']);
}

export function canViewAudit(roles: string[]): boolean {
  return hasRole(roles, 'Admin');
}

export function canManageUsers(roles: string[]): boolean {
  return hasRole(roles, 'Admin');
}
