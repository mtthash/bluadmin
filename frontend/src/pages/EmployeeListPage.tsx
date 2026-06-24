import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button } from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import { PageHeader } from '../components/common/PageHeader';
import { EmployeeTable } from '../components/employees/EmployeeTable';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import { useAuth } from '../hooks/useAuth';
import { canCreateEmployee } from '../auth/roleGuard';

export const EmployeeListPage: React.FC = () => {
  const navigate = useNavigate();
  const { permissions } = useAuth();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [status, setStatus] = useState<string | undefined>(undefined);

  return (
    <Box>
      <Breadcrumbs />
      <PageHeader
        title="Colaboradores"
        subtitle="Lista de todos os colaboradores"
        action={
          canCreateEmployee(permissions) ? (
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={() => navigate('/onboarding')}
            >
              Novo Colaborador
            </Button>
          ) : undefined
        }
      />
      <EmployeeTable
        status={status}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        onStatusFilter={setStatus}
      />
    </Box>
  );
};
