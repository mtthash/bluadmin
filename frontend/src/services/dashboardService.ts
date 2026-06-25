import api from './api';

export interface DepartmentCount {
  name: string;
  count: number;
}

export interface MonthlyActivity {
  month: string;
  onboards: number;
  offboards: number;
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface RecentAction {
  action: string;
  actor_email: string | null;
  target_email: string | null;
  result: string | null;
  created_at: string;
}

export interface DashboardStats {
  employees_by_department: DepartmentCount[];
  monthly_activity: MonthlyActivity[];
  status_counts: StatusCount[];
  recent_actions: RecentAction[];
}

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/dashboard/');
    return response.data;
  },
};
