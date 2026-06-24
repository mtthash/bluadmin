import React, { useState, useEffect, useRef } from 'react';
import { Box, Chip, Typography } from '@mui/material';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import { PageHeader } from '../components/common/PageHeader';
import { AuditLogFilters } from '../components/audit/AuditLogFilters';
import { AuditLogTable } from '../components/audit/AuditLogTable';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import { useQueryClient } from '@tanstack/react-query';
import type { AuditLogFilter } from '../types/auditLog';

export const AuditLogPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [filters, setFilters] = useState<AuditLogFilter | undefined>(undefined);
  const [liveMode, setLiveMode] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (liveMode) {
      intervalRef.current = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['auditLogs'] });
      }, 5000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [liveMode, queryClient]);

  const handleApplyFilters = (newFilters: AuditLogFilter) => {
    setFilters(newFilters);
    setPage(0);
    setLiveMode(false);
  };

  const handleClearFilters = () => {
    setFilters(undefined);
    setPage(0);
  };

  const handleToggleLive = () => {
    if (!liveMode) {
      setFilters(undefined);
      setPage(0);
    }
    setLiveMode(!liveMode);
  };

  return (
    <Box>
      <Breadcrumbs />
      <PageHeader
        title="Atividades"
        subtitle="Log de todas as acoes executadas na plataforma"
        action={
          liveMode ? (
            <Chip
              icon={<FiberManualRecordIcon sx={{ fontSize: 12, animation: 'blink 1s infinite', '@keyframes blink': { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.3 } } }} />}
              label="AO VIVO"
              color="error"
              size="small"
              variant="filled"
            />
          ) : undefined
        }
      />
      <AuditLogFilters
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
        liveMode={liveMode}
        onToggleLive={handleToggleLive}
      />
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
