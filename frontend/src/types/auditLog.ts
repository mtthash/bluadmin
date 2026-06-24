export interface AuditLog {
  id: string;
  action: string;
  actor_email: string;
  target_email: string | null;
  details: Record<string, unknown> | null;
  result: 'success' | 'failure' | 'partial' | 'blocked';
  error_message: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogFilter {
  action?: string;
  actor_email?: string;
  date_from?: string;
  date_to?: string;
}

export interface AuditLogList {
  items: AuditLog[];
  total: number;
  page: number;
  size: number;
}
