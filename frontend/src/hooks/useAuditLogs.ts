import { useQuery } from '@tanstack/react-query';
import { auditService } from '../services/auditService';
import type { AuditLogFilter } from '../types/auditLog';

export function useAuditLogs(
  page: number,
  size: number,
  filters?: AuditLogFilter,
) {
  return useQuery({
    queryKey: ['auditLogs', page, size, filters],
    queryFn: () => auditService.list(page, size, filters),
    placeholderData: (previousData) => previousData,
  });
}
