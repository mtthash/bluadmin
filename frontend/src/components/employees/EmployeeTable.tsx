import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Chip, Stack } from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel } from '@mui/x-data-grid';
import { EmployeeStatusChip } from './EmployeeStatusChip';
import { useEmployees } from '../../hooks/useEmployees';
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

export const EmployeeTable: React.FC<EmployeeTableProps> = ({
  status,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onStatusFilter,
}) => {
  const navigate = useNavigate();
  const { data, isLoading } = useEmployees(page, pageSize, status);

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
      minWidth: 220,
    },
    {
      field: 'user_principal_name',
      headerName: 'UPN',
      flex: 1,
      minWidth: 220,
    },
    {
      field: 'department',
      headerName: 'Departamento',
      flex: 0.8,
      minWidth: 150,
      renderCell: (params) => params.value ?? '-',
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => (
        <EmployeeStatusChip status={params.value as 'active' | 'disabled'} />
      ),
    },
    {
      field: 'created_at',
      headerName: 'Criado em',
      width: 120,
      renderCell: (params) => formatDate(params.value as string),
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
    </Box>
  );
};
