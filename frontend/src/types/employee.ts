export interface Employee {
  id: string;
  ad_username: string;
  display_name: string;
  email: string;
  user_principal_name: string;
  job_title: string | null;
  department: string | null;
  department_group_id: string | null;
  status: 'active' | 'disabled';
  created_at: string;
  updated_at: string;
  disabled_at: string | null;
  scheduled_deletion_at: string | null;
}

export interface EmployeeCreate {
  first_name: string;
  last_name: string;
  mail_nickname: string;
  password: string;
  department_group_id: string | null;
  department_name: string | null;
  job_title: string | null;
}

export interface OnboardResponse {
  user: Employee;
  temporary_password: string;
  status: string;
}

export interface EmployeeList {
  items: Employee[];
  total: number;
  page: number;
  size: number;
}
