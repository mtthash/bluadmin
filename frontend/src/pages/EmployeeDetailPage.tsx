import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, Stack, Snackbar, Alert } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PersonOffIcon from '@mui/icons-material/PersonOff';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { EmployeeCard } from '../components/employees/EmployeeCard';
import { OffboardDialog } from '../components/employees/OffboardDialog';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import { useEmployee, useOffboardEmployee } from '../hooks/useEmployees';
import { useAuth } from '../hooks/useAuth';
import { canDisableEmployee } from '../auth/roleGuard';

export const EmployeeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { roles } = useAuth();
  const { data: employee, isLoading, error, refetch } = useEmployee(id ?? '');
  const offboardMutation = useOffboardEmployee();

  const [offboardDialogOpen, setOffboardDialogOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  if (isLoading) {
    return <LoadingSpinner message="Carregando dados do colaborador..." />;
  }

  if (error || !employee) {
    return (
      <ErrorAlert
        message="Nao foi possivel carregar os dados do colaborador."
        onRetry={() => refetch()}
      />
    );
  }

  const handleOffboard = async () => {
    try {
      await offboardMutation.mutateAsync(employee.id);
      setOffboardDialogOpen(false);
      setSuccessMessage('Colaborador desligado com sucesso.');
    } catch {
      // Error handled by mutation state
    }
  };

  const showOffboardButton =
    canDisableEmployee(roles) && employee.status === 'active';

  return (
    <Box>
      <Breadcrumbs />
      <PageHeader
        title={employee.display_name}
        subtitle="Detalhes do colaborador"
        action={
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/employees')}
            >
              Voltar
            </Button>
            {showOffboardButton && (
              <Button
                variant="contained"
                color="error"
                startIcon={<PersonOffIcon />}
                onClick={() => setOffboardDialogOpen(true)}
              >
                Desligar
              </Button>
            )}
          </Stack>
        }
      />

      {offboardMutation.isError && (
        <ErrorAlert message="Erro ao desligar o colaborador. Tente novamente." />
      )}

      <EmployeeCard employee={employee} />

      <OffboardDialog
        open={offboardDialogOpen}
        employee={employee}
        loading={offboardMutation.isPending}
        onConfirm={handleOffboard}
        onCancel={() => setOffboardDialogOpen(false)}
      />

      <Snackbar
        open={!!successMessage}
        autoHideDuration={5000}
        onClose={() => setSuccessMessage('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSuccessMessage('')}
          severity="success"
          variant="filled"
        >
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};
