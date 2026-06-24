import React from 'react';
import { Box, Chip, Tooltip, Typography } from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel, GridRenderCellParams } from '@mui/x-data-grid';
import type { AuditLog, AuditLogFilter } from '../../types/auditLog';
import { useAuditLogs } from '../../hooks/useAuditLogs';

interface AuditLogTableProps {
  page: number;
  pageSize: number;
  filters?: AuditLogFilter;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

const ACTION_LABELS: Record<string, string> = {
  'user.onboard': 'Onboarding',
  'user.offboard': 'Desativacao',
  'user.delete': 'Exclusao definitiva',
  'platform_user.create': 'Novo usuario API',
  'platform_user.update': 'Edicao usuario API',
  'platform_user.deactivate': 'Desativacao usuario API',
  'platform_user.protect': 'Tentativa bloqueada',
};

const RESULT_CONFIG: Record<string, { label: string; color: 'success' | 'error' | 'warning' | 'default' }> = {
  success: { label: 'Sucesso', color: 'success' },
  failure: { label: 'Falha', color: 'error' },
  partial: { label: 'Parcial', color: 'warning' },
  blocked: { label: 'Bloqueado', color: 'error' },
};

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function formatDetails(details: Record<string, unknown> | null): string {
  if (!details) return '';
  const parts: string[] = [];
  for (const [key, value] of Object.entries(details)) {
    if (value === null || value === undefined) continue;
    if (typeof value === 'object') {
      const obj = value as Record<string, unknown>;
      if (obj.from !== undefined && obj.to !== undefined) {
        parts.push(`${key}: ${obj.from} → ${obj.to}`);
      } else {
        parts.push(`${key}: ${JSON.stringify(value)}`);
      }
    } else {
      parts.push(`${key}: ${value}`);
    }
  }
  return parts.join(' | ');
}

export const AuditLogTable: React.FC<AuditLogTableProps> = ({
  page,
  pageSize,
  filters,
  onPageChange,
  onPageSizeChange,
}) => {
  const { data, isLoading } = useAuditLogs(page, pageSize, filters);

  const columns: GridColDef<AuditLog>[] = [
    {
      field: 'created_at',
      headerName: 'Data/Hora',
      width: 170,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
          {formatDateTime(params.value as string)}
        </Typography>
      ),
    },
    {
      field: 'action',
      headerName: 'Acao',
      width: 180,
      renderCell: (params) => {
        const action = params.value as string;
        const label = ACTION_LABELS[action] || action;
        const isProtect = action === 'platform_user.protect';
        return (
          <Chip
            label={label}
            size="small"
            color={isProtect ? 'error' : 'default'}
            variant={isProtect ? 'filled' : 'outlined'}
            sx={{ fontWeight: isProtect ? 700 : 400 }}
          />
        );
      },
    },
    {
      field: 'actor_email',
      headerName: 'Executado por',
      flex: 0.7,
      minWidth: 130,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={600}>
          {params.value as string}
        </Typography>
      ),
    },
    {
      field: 'target_email',
      headerName: 'Alvo',
      flex: 0.7,
      minWidth: 130,
      renderCell: (params) => params.value ?? '-',
    },
    {
      field: 'result',
      headerName: 'Resultado',
      width: 120,
      renderCell: (params) => {
        const r = params.value as string;
        const cfg = RESULT_CONFIG[r] || { label: r, color: 'default' as const };
        return <Chip label={cfg.label} color={cfg.color} size="small" variant="outlined" />;
      },
    },
    {
      field: 'details',
      headerName: 'Detalhes',
      flex: 1,
      minWidth: 200,
      renderCell: (params: GridRenderCellParams<AuditLog>) => {
        const details = params.value as Record<string, unknown> | null;
        const text = formatDetails(details);
        if (!text) return '-';
        return (
          <Tooltip title={text}>
            <Typography variant="body2" noWrap sx={{ fontSize: '0.8rem' }}>
              {text}
            </Typography>
          </Tooltip>
        );
      },
    },
  ];

  const handlePaginationModelChange = (model: GridPaginationModel) => {
    if (model.page !== page) onPageChange(model.page);
    if (model.pageSize !== pageSize) onPageSizeChange(model.pageSize);
  };

  return (
    <Box>
      <DataGrid
        rows={data?.items ?? []}
        columns={columns}
        rowCount={data?.total ?? 0}
        loading={isLoading}
        paginationMode="server"
        paginationModel={{ page, pageSize }}
        onPaginationModelChange={handlePaginationModelChange}
        pageSizeOptions={[10, 25, 50]}
        disableRowSelectionOnClick
        autoHeight
        sx={{ border: 'none' }}
      />
    </Box>
  );
};
