import api from './api';
import type {
  EmployeeCreate,
  EmployeeList,
  Employee,
  OnboardResponse,
} from '../types/employee';

export const employeeService = {
  list: async (
    page: number,
    size: number,
    status?: string,
  ): Promise<EmployeeList> => {
    const params: Record<string, string | number> = { page: Math.max(1, page + 1), size };
    if (status) params.status = status;
    const { data } = await api.get<EmployeeList>('/employees/', { params });
    return data;
  },

  getById: async (id: string): Promise<Employee> => {
    const { data } = await api.get<Employee>(
      `/employees/${encodeURIComponent(id)}`,
    );
    return data;
  },

  onboard: async (payload: EmployeeCreate): Promise<OnboardResponse> => {
    const { data } = await api.post<OnboardResponse>(
      '/employees/onboard',
      payload,
    );
    return data;
  },

  offboard: async (id: string, retentionMinutes?: number): Promise<Employee> => {
    const params = retentionMinutes !== undefined ? { retention_minutes: retentionMinutes } : {};
    const { data } = await api.post<Employee>(
      `/employees/${encodeURIComponent(id)}/offboard`,
      null,
      { params },
    );
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/employees/${encodeURIComponent(id)}`);
  },
};
