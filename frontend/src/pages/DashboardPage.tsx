import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import HistoryIcon from '@mui/icons-material/History';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  LineChart, Line,
} from 'recharts';
import { useAuth } from '../hooks/useAuth';
import { useEmployees } from '../hooks/useEmployees';
import { useAuditLogs } from '../hooks/useAuditLogs';
import { canCreateEmployee } from '../auth/roleGuard';
import { dashboardService } from '../services/dashboardService';
import type { DashboardStats } from '../services/dashboardService';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const CHART_COLORS = ['#00a8ff', '#4caf50', '#ff5252', '#ffb300', '#ab47bc', '#26c6da', '#ff7043', '#66bb6a'];
const STATUS_COLORS: Record<string, string> = {
  'Ativos': '#4caf50',
  'Desabilitados': '#ff5252',
};

interface SummaryCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, value, icon, color }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: `${color}15`, color, display: 'flex' }}>
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">{title}</Typography>
          <Typography variant="h5" fontWeight={700}>{value}</Typography>
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const ACTION_LABELS: Record<string, string> = {
  'user.onboard': 'Onboarding',
  'user.offboard': 'Offboarding',
  'user.delete': 'Exclusao',
  'platform_user.create': 'Usuario criado',
  'platform_user.update': 'Usuario atualizado',
  'platform_user.delete': 'Usuario removido',
};

const RESULT_COLORS: Record<string, 'success' | 'error' | 'warning' | 'default'> = {
  'success': 'success',
  'failure': 'error',
  'partial': 'warning',
};

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function formatMonth(month: string): string {
  const [year, m] = month.split('-');
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  return `${months[parseInt(m, 10) - 1]}/${year.slice(2)}`;
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, permissions } = useAuth();
  const { data: allEmployees, isLoading: loadingAll } = useEmployees(0, 1);
  const { data: activeEmployees, isLoading: loadingActive } = useEmployees(0, 1, 'active');
  const { data: disabledEmployees, isLoading: loadingDisabled } = useEmployees(0, 1, 'disabled');
  const { data: recentAudit, isLoading: loadingAudit } = useAuditLogs(0, 1);

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    dashboardService.getStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoadingStats(false));
  }, []);

  const isLoading = loadingAll || loadingActive || loadingDisabled || loadingAudit || loadingStats;

  if (isLoading) {
    return <LoadingSpinner message="Carregando dashboard..." />;
  }

  return (
    <Box>
      <PageHeader
        title={`Bem-vindo, ${user?.name ?? 'Usuario'}!`}
        subtitle="Painel de gestao de colaboradores"
      />

      {/* Summary cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard title="Total de Colaboradores" value={allEmployees?.total ?? 0} icon={<PeopleIcon />} color="#00a8ff" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard title="Ativos" value={activeEmployees?.total ?? 0} icon={<CheckCircleIcon />} color="#4caf50" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard title="Desabilitados" value={disabledEmployees?.total ?? 0} icon={<BlockIcon />} color="#ff5252" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <SummaryCard title="Acoes Recentes" value={recentAudit?.total ?? 0} icon={<HistoryIcon />} color="#ffb300" />
        </Grid>
      </Grid>

      {/* Charts row 1 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Colaboradores por departamento */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Colaboradores por Departamento</Typography>
              {stats && stats.employees_by_department.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={stats.employees_by_department} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a3a4e" />
                    <XAxis dataKey="name" tick={{ fill: '#8899aa', fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fill: '#8899aa', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a2332', border: '1px solid #2a3a4e', borderRadius: 8 }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="count" name="Colaboradores" radius={[4, 4, 0, 0]}>
                      {stats.employees_by_department.map((_, i) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  Sem dados de departamentos
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Status dos colaboradores */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Status dos Colaboradores</Typography>
              {stats && stats.status_counts.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={stats.status_counts}
                      dataKey="count"
                      nameKey="status"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      innerRadius={55}
                      paddingAngle={3}
                      label={({ status, count }) => `${status}: ${count}`}
                    >
                      {stats.status_counts.map((entry, i) => (
                        <Cell key={i} fill={STATUS_COLORS[entry.status] ?? '#ffb300'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a2332', border: '1px solid #2a3a4e', borderRadius: 8 }}
                    />
                    <Legend wrapperStyle={{ color: '#8899aa' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  Sem dados
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts row 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Onboards/Offboards por mes */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Movimentacoes por Mes</Typography>
              {stats && stats.monthly_activity.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={stats.monthly_activity} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a3a4e" />
                    <XAxis dataKey="month" tickFormatter={formatMonth} tick={{ fill: '#8899aa', fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fill: '#8899aa', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a2332', border: '1px solid #2a3a4e', borderRadius: 8 }}
                      labelFormatter={formatMonth}
                    />
                    <Legend wrapperStyle={{ color: '#8899aa' }} />
                    <Line type="monotone" dataKey="onboards" name="Onboards" stroke="#4caf50" strokeWidth={2} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="offboards" name="Offboards" stroke="#ff5252" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  Sem movimentacoes nos ultimos 6 meses
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Atividade recente */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Atividade Recente</Typography>
              {stats && stats.recent_actions.length > 0 ? (
                <TableContainer sx={{ maxHeight: 300 }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>Acao</TableCell>
                        <TableCell>Alvo</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Data</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {stats.recent_actions.map((a, i) => (
                        <TableRow key={i}>
                          <TableCell>
                            <Typography variant="body2" fontSize="0.8rem">
                              {ACTION_LABELS[a.action] ?? a.action}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                              {a.target_email ?? '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={a.result ?? '-'}
                              size="small"
                              color={RESULT_COLORS[a.result ?? ''] ?? 'default'}
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontSize="0.75rem" color="text.secondary">
                              {formatDateTime(a.created_at)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  Sem atividades recentes
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action buttons */}
      <Stack direction="row" spacing={2}>
        {canCreateEmployee(permissions) && (
          <Button variant="contained" startIcon={<PersonAddIcon />} onClick={() => navigate('/onboarding')}>
            Novo Onboarding
          </Button>
        )}
        <Button variant="outlined" startIcon={<PeopleIcon />} onClick={() => navigate('/employees')}>
          Ver Colaboradores
        </Button>
      </Stack>
    </Box>
  );
};
