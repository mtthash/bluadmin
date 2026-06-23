import React, { useState } from 'react';
import { Box } from '@mui/material';
import { PageHeader } from '../components/common/PageHeader';
import { AuditLogFilters } from '../components/audit/AuditLogFilters';
import { AuditLogTable } from '../components/audit/AuditLogTable';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import type { AuditLogFilter } from '../types/auditLog';

export const AuditLogPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [filters, setFilters] = useState<AuditLogFilter | undefined>(
    undefined,
  );

  const handleApplyFilters = (newFilters: AuditLogFilter) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handleClearFilters = () => {
    setFilters(undefined);
    setPage(0);
  };

  return (
    <Box>
      <Breadcrumbs />
      <PageHeader
        title="Logs de Auditoria"
        subtitle="Historico de acoes realizadas no sistema"
      />
      <AuditLogFilters onApply={handleApplyFilters} onClear={handleClearFilters} />
      <AuditLogTable
        page={page}
        pageSize={pageSize}
        filters={filters}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
      />
    </Box>
  );
};
