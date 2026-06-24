export type AppRole = 'admin' | 'viewer';

export interface AuthUser {
  name: string;
  email: string;
  role: AppRole;
  permissions: string[];
}
