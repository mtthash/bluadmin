import React from 'react';
import { Box, Chip } from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel } from '@mui/x-data-grid';
import type { AuditLog, AuditLogFilter } from '../../types/auditLog';
import { useAuditLogs } from '../../hooks/useAuditLogs';

interface AuditLogTableProps {
  page: number;
  pageSize: number;
  filters?: AuditLogFilter;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

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

function getResultColor(
  result: string,
): 'success' | 'error' | 'warning' | 'default' {
  switch (result) {
    case 'success':
      return 'success';
    case 'failure':
      return 'error';
    case 'partial':
      return 'warning';
    default:
      return 'default';
  }
}

function getResultLabel(result: string): string {
  switch (result) {
    case 'success':
      return 'Sucesso';
    case 'failure':
      return 'Falha';
    case 'partial':
      return 'Parcial';
    default:
      return result;
  }
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
      width: 180,
      renderCell: (params) => formatDateTime(params.value as string),
    },
    {
      field: 'action',
      headerName: 'Acao',
      width: 160,
    },
    {
      field: 'actor_email',
      headerName: 'Executado por',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'target_email',
      headerName: 'Alvo',
      flex: 1,
      minWidth: 200,
      renderCell: (params) => params.value ?? '-',
    },
    {
      field: 'result',
      headerName: 'Resultado',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={getResultLabel(params.value as string)}
          color={getResultColor(params.value as string)}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'details',
      headerName: 'Detalhes',
      flex: 0.8,
      minWidth: 150,
      renderCell: (params) => {
        const details = params.value as Record<string, unknown> | null;
        if (!details) return '-';
        return JSON.stringify(details);
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
