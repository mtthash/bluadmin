import api from './api';

export interface PlatformUser {
  id: string;
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlatformUserList {
  items: PlatformUser[];
  total: number;
}

export interface PlatformUserCreate {
  username: string;
  password: string;
  display_name: string;
  role: string;
}

export interface PlatformUserUpdate {
  display_name?: string;
  role?: string;
  is_active?: boolean;
  password?: string;
}

export const platformUserService = {
  list: () => api.get<PlatformUserList>('/platform-users/').then((r) => r.data),

  create: (data: PlatformUserCreate) =>
    api.post<PlatformUser>('/platform-users/', data).then((r) => r.data),

  update: (id: string, data: PlatformUserUpdate) =>
    api.put<PlatformUser>(`/platform-users/${id}`, data).then((r) => r.data),

  remove: (id: string) => api.delete(`/platform-users/${id}`),
};
