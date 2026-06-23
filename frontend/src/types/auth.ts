export type AppRole = 'HR' | 'IT' | 'Admin';

export interface AuthUser {
  name: string;
  email: string;
  roles: AppRole[];
}
