import api from './api';
import type { Department } from '../types/department';

export interface DepartmentCreate {
  name: string;
  description: string | null;
}

export const departmentService = {
  list: async (): Promise<Department[]> => {
    const { data } = await api.get<Department[]>('/departments/');
    return data;
  },

  create: async (payload: DepartmentCreate): Promise<Department> => {
    const { data } = await api.post<Department>('/departments/', payload);
    return data;
  },
};
