import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Stack,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import HistoryIcon from '@mui/icons-material/History';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import { useAuth } from '../hooks/useAuth';
import { useEmployees } from '../hooks/useEmployees';
import { useAuditLogs } from '../hooks/useAuditLogs';
import { canCreateEmployee } from '../auth/roleGuard';

import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

interface SummaryCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  icon,
  color,
}) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            bgcolor: `${color}15`,
            color,
            display: 'flex',
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h5" fontWeight={700}>
            {value}
          </Typography>
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, permissions } = useAuth();
  const { data: allEmployees, isLoading: loadingAll } = useEmployees(0, 1);
  const { data: activeEmployees, isLoading: loadingActive } = useEmployees(
    0,
    1,
    'active',
  );
  const { data: disabledEmployees, isLoading: loadingDisabled } = useEmployees(
    0,
    1,
    'disabled',
  );
  const { data: recentAudit, isLoading: loadingAudit } = useAuditLogs(0, 1);

  const isLoading =
    loadingAll || loadingActive || loadingDisabled || loadingAudit;

  if (isLoading) {
    return <LoadingSpinner message="Carregando dashboard..." />;
  }

  return (
    <Box>
      <PageHeader
        title={`Bem-vindo, ${user?.name ?? 'Usuario'}!`}
        subtitle="Painel de gestao de colaboradores"
      />

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard
            title="Total de Colaboradores"
            value={allEmployees?.total ?? 0}
            icon={<PeopleIcon />}
            color="#00a8ff"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard
            title="Ativos"
            value={activeEmployees?.total ?? 0}
            icon={<CheckCircleIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard
            title="Desabilitados"
            value={disabledEmployees?.total ?? 0}
            icon={<BlockIcon />}
            color="#ff5252"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard
            title="Acoes Recentes"
            value={recentAudit?.total ?? 0}
            icon={<HistoryIcon />}
            color="#ffb300"
          />
        </Grid>
      </Grid>

      <Stack direction="row" spacing={2}>
        {canCreateEmployee(permissions) && (
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={() => navigate('/onboarding')}
          >
            Novo Onboarding
          </Button>
        )}
        <Button
          variant="outlined"
          startIcon={<PeopleIcon />}
          onClick={() => navigate('/employees')}
        >
          Ver Colaboradores
        </Button>
      </Stack>
    </Box>
  );
};
