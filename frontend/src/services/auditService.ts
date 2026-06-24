import api from './api';
import type { AuditLogList, AuditLogFilter } from '../types/auditLog';

export const auditService = {
  list: async (
    page: number,
    size: number,
    filters?: AuditLogFilter,
  ): Promise<AuditLogList> => {
    const params: Record<string, string | number> = { page: Math.max(1, page + 1), size };

    if (filters) {
      if (filters.action) params.action = filters.action;
      if (filters.actor_email) params.actor_email = filters.actor_email;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
    }

    const { data } = await api.get<AuditLogList>('/audit-logs/', { params });
    return data;
  },
};
