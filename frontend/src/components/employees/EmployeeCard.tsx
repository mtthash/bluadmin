import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Avatar,
  Typography,
  Divider,
  Grid,
} from '@mui/material';
import { EmployeeStatusChip } from './EmployeeStatusChip';
import type { Employee } from '../../types/employee';

interface EmployeeCardProps {
  employee: Employee;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((p) => p[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({ employee }) => {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar
            sx={{
              width: 64,
              height: 64,
              bgcolor: 'primary.main',
              fontSize: '1.5rem',
            }}
          >
            {getInitials(employee.display_name)}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" fontWeight={600}>
              {employee.display_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {employee.email}
            </Typography>
          </Box>
          <EmployeeStatusChip status={employee.status} />
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              Nome Principal (UPN)
            </Typography>
            <Typography variant="body2">
              {employee.user_principal_name}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              Cargo
            </Typography>
            <Typography variant="body2">
              {employee.job_title ?? 'Nao informado'}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              Departamento
            </Typography>
            <Typography variant="body2">
              {employee.department ?? 'Nao informado'}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              ID Entra
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              {employee.entra_id}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              Criado em
            </Typography>
            <Typography variant="body2">
              {formatDate(employee.created_at)}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="caption" color="text.secondary">
              Desabilitado em
            </Typography>
            <Typography variant="body2">
              {formatDate(employee.disabled_at)}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};
