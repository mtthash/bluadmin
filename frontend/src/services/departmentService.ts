import api from './api';
import type { Department } from '../types/department';

export const departmentService = {
  list: async (): Promise<Department[]> => {
    const { data } = await api.get<Department[]>('/departments');
    return data;
  },
};
