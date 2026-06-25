import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Typography,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Alert,
} from '@mui/material';
import { DataGrid, GridColDef, GridPaginationModel, GridRenderCellParams } from '@mui/x-data-grid';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import BlockIcon from '@mui/icons-material/Block';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import FolderIcon from '@mui/icons-material/Folder';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import TimerIcon from '@mui/icons-material/Timer';
import { EmployeeStatusChip } from './EmployeeStatusChip';
import { OffboardDialog } from './OffboardDialog';
import { useEmployees, useOffboardEmployee } from '../../hooks/useEmployees';
import { employeeService } from '../../services/employeeService';
import { folderMappingService } from '../../services/folderMappingService';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { useQueryClient } from '@tanstack/react-query';
import type { Employee } from '../../types/employee';
import type { FolderMapping } from '../../types/folderMapping';

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

  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [menuEmployee, setMenuEmployee] = useState<Employee | null>(null);

  const [folderDialogOpen, setFolderDialogOpen] = useState(false);
  const [folderEmployee, setFolderEmployee] = useState<Employee | null>(null);
  const [mappings, setMappings] = useState<FolderMapping[]>([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [driveLetter, setDriveLetter] = useState('');
  const [folderError, setFolderError] = useState<string | null>(null);
  const [folderSaving, setFolderSaving] = useState(false);

  const fetchMappings = async (employeeId: string) => {
    try {
      const data = await folderMappingService.list(employeeId);
      setMappings(data);
    } catch {
      setMappings([]);
    }
  };

  useEffect(() => {
    if (folderEmployee) {
      fetchMappings(folderEmployee.id);
    }
  }, [folderEmployee]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, emp: Employee) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setMenuEmployee(emp);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuEmployee(null);
  };

  const handleOpenFolders = () => {
    setFolderEmployee(menuEmployee);
    setFolderDialogOpen(true);
    handleMenuClose();
  };

  const handleOffboardFromMenu = () => {
    setOffboardTarget(menuEmployee);
    handleMenuClose();
  };

  const handleDeleteFromMenu = () => {
    setDeleteTarget(menuEmployee);
    handleMenuClose();
  };

  const handleAddMapping = async () => {
    if (!folderEmployee || !folderName.trim() || !driveLetter.trim()) return;
    setFolderSaving(true);
    setFolderError(null);
    try {
      await folderMappingService.create(folderEmployee.id, {
        folder_name: folderName.trim(),
        drive_letter: driveLetter.trim().toUpperCase(),
      });
      setAddDialogOpen(false);
      setFolderName('');
      setDriveLetter('');
      fetchMappings(folderEmployee.id);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { message?: string } } };
      const msg = axiosErr?.response?.data?.message || (err instanceof Error ? err.message : 'Erro ao adicionar mapeamento');
      setFolderError(msg);
    } finally {
      setFolderSaving(false);
    }
  };

  const handleRemoveMapping = async (mappingId: string) => {
    if (!folderEmployee) return;
    try {
      await folderMappingService.remove(folderEmployee.id, mappingId);
      fetchMappings(folderEmployee.id);
    } catch {
      // silently fail
    }
  };

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
      width: 60,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams<Employee>) => (
        <Box onClick={(e) => e.stopPropagation()}>
          <IconButton size="small" onClick={(e) => handleMenuOpen(e, params.row)}>
            <MoreVertIcon fontSize="small" />
          </IconButton>
        </Box>
      ),
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

      {/* Menu dropdown de acoes */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={handleOpenFolders}>
          <ListItemIcon><FolderIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Pastas Mapeadas</ListItemText>
        </MenuItem>
        {menuEmployee?.status === 'active' && (
          <MenuItem onClick={handleOffboardFromMenu}>
            <ListItemIcon><BlockIcon fontSize="small" color="warning" /></ListItemIcon>
            <ListItemText>Desativar</ListItemText>
          </MenuItem>
        )}
        {menuEmployee?.status === 'disabled' && (
          <MenuItem onClick={handleDeleteFromMenu}>
            <ListItemIcon><DeleteForeverIcon fontSize="small" color="error" /></ListItemIcon>
            <ListItemText>Excluir Definitivamente</ListItemText>
          </MenuItem>
        )}
      </Menu>

      {/* Dialog de pastas mapeadas */}
      <Dialog
        open={folderDialogOpen}
        onClose={() => { setFolderDialogOpen(false); setFolderEmployee(null); }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FolderIcon color="primary" />
            Pastas Mapeadas — {folderEmployee?.display_name}
          </Box>
        </DialogTitle>
        <DialogContent>
          {mappings.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
              Nenhuma pasta mapeada para este colaborador.
            </Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Drive</TableCell>
                    <TableCell>Pasta</TableCell>
                    <TableCell>Caminho UNC</TableCell>
                    <TableCell>Tipo</TableCell>
                    <TableCell align="right">Acao</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mappings.map((m) => (
                    <TableRow key={m.id}>
                      <TableCell>
                        <Typography fontWeight={600} sx={{ fontFamily: 'monospace' }}>
                          {m.drive_letter}
                        </Typography>
                      </TableCell>
                      <TableCell>{m.folder_name}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                          {m.unc_path}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={m.is_default ? 'Padrao' : 'Manual'}
                          size="small"
                          color={m.is_default ? 'primary' : 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" color="error" onClick={() => handleRemoveMapping(m.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            startIcon={<AddIcon />}
            onClick={() => { setFolderError(null); setAddDialogOpen(true); }}
          >
            Adicionar Mapeamento
          </Button>
          <Button
            variant="contained"
            onClick={() => { setFolderDialogOpen(false); setFolderEmployee(null); }}
          >
            Fechar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de adicionar mapeamento */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Adicionar Mapeamento de Pasta</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {folderError && <Alert severity="error">{folderError}</Alert>}
            <TextField
              label="Nome da Pasta"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              fullWidth
              autoFocus
              placeholder="Ex: TI, Financeiro, Diretoria"
            />
            <TextField
              label="Letra do Drive"
              value={driveLetter}
              onChange={(e) => setDriveLetter(e.target.value)}
              fullWidth
              placeholder="Ex: Y:"
              inputProps={{ maxLength: 3 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleAddMapping}
            disabled={!folderName.trim() || !driveLetter.trim() || folderSaving}
          >
            {folderSaving ? 'Adicionando...' : 'Adicionar'}
          </Button>
        </DialogActions>
      </Dialog>

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
