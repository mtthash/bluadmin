import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  platformUserService,
  type PlatformUser,
  type PlatformUserCreate,
  type PlatformUserUpdate,
} from '../services/platformUserService';

const ROLES = [
  { value: 'admin', label: 'Administrador' },
  { value: 'viewer', label: 'Visualizador' },
];

const roleColor = (role: string) => {
  switch (role) {
    case 'admin': return 'error';
    case 'hr': return 'primary';
    case 'it': return 'info';
    default: return 'default';
  }
};

const roleLabel = (role: string) =>
  ROLES.find((r) => r.value === role)?.label ?? role;

export const PlatformUsersPage: React.FC = () => {
  const [users, setUsers] = useState<PlatformUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editUser, setEditUser] = useState<PlatformUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<PlatformUserCreate>({
    username: '',
    password: '',
    display_name: '',
    role: 'viewer',
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await platformUserService.list();
      setUsers(data.items);
    } catch {
      setError('Erro ao carregar usuarios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openCreate = () => {
    setEditUser(null);
    setForm({ username: '', password: '', display_name: '', role: 'viewer' });
    setError(null);
    setDialogOpen(true);
  };

  const openEdit = (user: PlatformUser) => {
    setEditUser(user);
    setForm({
      username: user.username,
      password: '',
      display_name: user.display_name,
      role: user.role,
    });
    setError(null);
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setError(null);
    try {
      if (editUser) {
        const update: PlatformUserUpdate = {
          display_name: form.display_name,
          role: form.role,
        };
        if (form.password) update.password = form.password;
        await platformUserService.update(editUser.id, update);
      } else {
        await platformUserService.create(form);
      }
      setDialogOpen(false);
      fetchUsers();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Erro ao salvar';
      setError(msg);
    }
  };

  const [removeTarget, setRemoveTarget] = useState<PlatformUser | null>(null);

  const toggleActive = async (user: PlatformUser) => {
    try {
      await platformUserService.update(user.id, {
        is_active: !user.is_active,
      });
      fetchUsers();
    } catch {
      setError('Erro ao alterar status');
    }
  };

  const handleRemove = async () => {
    if (!removeTarget) return;
    try {
      await platformUserService.remove(removeTarget.id);
      setRemoveTarget(null);
      fetchUsers();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Erro ao remover';
      setError(msg);
      setRemoveTarget(null);
    }
  };

  if (loading) return <LoadingSpinner message="Carregando usuarios..." />;

  return (
    <Box>
      <PageHeader
        title="Permissoes"
        subtitle="Gerenciar usuarios da plataforma BluAdmin"
        action={
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Novo Usuario
          </Button>
        }
      />

      <TableContainer component={Paper} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Usuario</TableCell>
              <TableCell>Nome</TableCell>
              <TableCell>Perfil</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell sx={{ fontFamily: 'monospace' }}>{user.username}</TableCell>
                <TableCell>{user.display_name}</TableCell>
                <TableCell>
                  <Chip
                    label={roleLabel(user.role)}
                    color={roleColor(user.role) as 'error' | 'primary' | 'info' | 'default'}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.is_active ? 'Ativo' : 'Inativo'}
                    color={user.is_active ? 'success' : 'error'}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton size="small" onClick={() => openEdit(user)}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={user.is_active ? 'Desativar' : 'Ativar'}>
                    <IconButton size="small" onClick={() => toggleActive(user)}>
                      {user.is_active ? (
                        <BlockIcon fontSize="small" />
                      ) : (
                        <CheckCircleIcon fontSize="small" />
                      )}
                    </IconButton>
                  </Tooltip>
                  {user.username !== 'admin' && (
                    <Tooltip title="Remover">
                      <IconButton size="small" color="error" onClick={() => setRemoveTarget(user)}>
                        <DeleteForeverIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editUser ? 'Editar Usuario' : 'Novo Usuario'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Usuario"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              disabled={!!editUser}
              fullWidth
            />
            <TextField
              label={editUser ? 'Nova Senha (deixe vazio para manter)' : 'Senha'}
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              fullWidth
              required={!editUser}
            />
            <TextField
              label="Nome de Exibicao"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Perfil"
              select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              fullWidth
            >
              {ROLES.map((r) => (
                <MenuItem key={r.value} value={r.value}>
                  {r.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={!form.username || !form.display_name || (!editUser && !form.password)}
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={!!removeTarget} onClose={() => setRemoveTarget(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Remover Usuario</DialogTitle>
        <DialogContent>
          Tem certeza que deseja remover permanentemente o usuario{' '}
          <strong>{removeTarget?.display_name}</strong> ({removeTarget?.username})?
          Esta acao nao pode ser desfeita.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveTarget(null)}>Cancelar</Button>
          <Button variant="contained" color="error" onClick={handleRemove}>
            Remover
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
