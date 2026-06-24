import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel, GridRenderCellParams } from '@mui/x-data-grid';
import BlockIcon from '@mui/icons-material/Block';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import TimerIcon from '@mui/icons-material/Timer';
import { EmployeeStatusChip } from './EmployeeStatusChip';
import { OffboardDialog } from './OffboardDialog';
import { useEmployees, useOffboardEmployee } from '../../hooks/useEmployees';
import { employeeService } from '../../services/employeeService';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { useQueryClient } from '@tanstack/react-query';
import type { Employee } from '../../types/employee';

interface EmployeeTableProps {
  status?: string;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onStatusFilter: (status: string | undefined) => void;
}

const STATUS_OPTIONS = [
  { label: 'Todos', value: undefined },
  { label: 'Ativos', value: 'active' },
  { label: 'Desabilitados', value: 'disabled' },
];

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function getDaysRemaining(scheduledDeletion: string | null): number | null {
  if (!scheduledDeletion) return null;
  const now = new Date();
  const deletion = new Date(scheduledDeletion);
  const diff = deletion.getTime() - now.getTime();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

function DeletionCountdown({ scheduledDeletion }: { scheduledDeletion: string | null }) {
  const days = getDaysRemaining(scheduledDeletion);
  if (days === null) return null;

  const color = days <= 5 ? '#ff5252' : days <= 15 ? '#ffb300' : '#8899aa';

  return (
    <Tooltip title={`Exclusao definitiva em ${formatDate(scheduledDeletion!)}`}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <TimerIcon sx={{ fontSize: 16, color }} />
        <Typography variant="caption" sx={{ color, fontWeight: 600 }}>
          {days === 0 ? 'Hoje' : `${days}d`}
        </Typography>
      </Box>
    </Tooltip>
  );
}

export const EmployeeTable: React.FC<EmployeeTableProps> = ({
  status,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onStatusFilter,
}) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading } = useEmployees(page, pageSize, status);
  const offboardMutation = useOffboardEmployee();

  const [offboardTarget, setOffboardTarget] = useState<Employee | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handleOffboard = async (retentionMinutes: number) => {
    if (!offboardTarget) return;
    try {
      await offboardMutation.mutateAsync({ id: offboardTarget.id, retentionMinutes });
      setOffboardTarget(null);
    } catch {
      // handled by mutation
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await employeeService.delete(deleteTarget.id);
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setDeleteTarget(null);
    } catch {
      // error silenced
    } finally {
      setDeleteLoading(false);
    }
  };

  const columns: GridColDef<Employee>[] = [
    {
      field: 'display_name',
      headerName: 'Nome',
      flex: 1,
      minWidth: 180,
    },
    {
      field: 'email',
      headerName: 'E-mail',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'department',
      headerName: 'Departamento',
      flex: 0.7,
      minWidth: 130,
      renderCell: (params) => params.value ?? '-',
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams<Employee>) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <EmployeeStatusChip status={params.value as 'active' | 'disabled'} />
          {params.value === 'disabled' && (
            <DeletionCountdown scheduledDeletion={params.row.scheduled_deletion_at} />
          )}
        </Box>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Criado em',
      width: 110,
      renderCell: (params) => formatDate(params.value as string),
    },
    {
      field: 'actions',
      headerName: 'Acoes',
      width: 100,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams<Employee>) => {
        const emp = params.row;
        return (
          <Box sx={{ display: 'flex', gap: 0.5 }} onClick={(e) => e.stopPropagation()}>
            {emp.status === 'active' && (
              <Tooltip title="Desativar">
                <IconButton
                  size="small"
                  color="warning"
                  onClick={() => setOffboardTarget(emp)}
                >
                  <BlockIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {emp.status === 'disabled' && (
              <Tooltip title="Excluir definitivamente">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => setDeleteTarget(emp)}
                >
                  <DeleteForeverIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
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
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        {STATUS_OPTIONS.map((opt) => (
          <Chip
            key={opt.label}
            label={opt.label}
            variant={status === opt.value ? 'filled' : 'outlined'}
            color={status === opt.value ? 'primary' : 'default'}
            onClick={() => onStatusFilter(opt.value)}
          />
        ))}
      </Stack>

      <DataGrid
        rows={data?.items ?? []}
        columns={columns}
        rowCount={data?.total ?? 0}
        loading={isLoading}
        paginationMode="server"
        paginationModel={{ page, pageSize }}
        onPaginationModelChange={handlePaginationModelChange}
        pageSizeOptions={[10, 25, 50]}
        onRowClick={(params) => navigate(`/employees/${params.id}`)}
        disableRowSelectionOnClick
        autoHeight
        sx={{
          '& .MuiDataGrid-row': { cursor: 'pointer' },
          border: 'none',
        }}
      />

      <OffboardDialog
        open={!!offboardTarget}
        employee={offboardTarget}
        loading={offboardMutation.isPending}
        onConfirm={handleOffboard}
        onCancel={() => setOffboardTarget(null)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir Colaborador Definitivamente"
        message={`Tem certeza que deseja excluir ${deleteTarget?.display_name}? Esta acao removera o usuario do Active Directory e do banco de dados. Nao pode ser desfeita.`}
        confirmLabel="Excluir Definitivamente"
        confirmColor="error"
        loading={deleteLoading}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </Box>
  );
};
