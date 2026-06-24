export function hasPermission(permissions: string[], required: string): boolean {
  return permissions.includes(required);
}

export function hasAnyPermission(permissions: string[], required: string[]): boolean {
  return required.some((p) => permissions.includes(p));
}

export function hasAllPermissions(permissions: string[], required: string[]): boolean {
  return required.every((p) => permissions.includes(p));
}

export function canCreateEmployee(permissions: string[]): boolean {
  return hasPermission(permissions, 'employee:create');
}

export function canDisableEmployee(permissions: string[]): boolean {
  return hasPermission(permissions, 'employee:disable');
}

export function canViewEmployees(permissions: string[]): boolean {
  return hasPermission(permissions, 'employee:list');
}

export function canViewAudit(permissions: string[]): boolean {
  return hasPermission(permissions, 'audit:read');
}

export function canManageUsers(permissions: string[]): boolean {
  return hasPermission(permissions, 'user:manage');
}
