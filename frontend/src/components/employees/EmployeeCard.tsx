import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Box,
  Avatar,
  Typography,
  Divider,
  Grid,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { EmployeeStatusChip } from './EmployeeStatusChip';
import { folderMappingService } from '../../services/folderMappingService';
import type { Employee } from '../../types/employee';
import type { FolderMapping } from '../../types/folderMapping';

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
  const [mappings, setMappings] = useState<FolderMapping[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [driveLetter, setDriveLetter] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const fetchMappings = async () => {
    try {
      const data = await folderMappingService.list(employee.id);
      setMappings(data);
    } catch {
      // silently fail
    }
  };

  useEffect(() => {
    fetchMappings();
  }, [employee.id]);

  const handleAdd = async () => {
    if (!folderName.trim() || !driveLetter.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await folderMappingService.create(employee.id, {
        folder_name: folderName.trim(),
        drive_letter: driveLetter.trim().toUpperCase(),
      });
      setDialogOpen(false);
      setFolderName('');
      setDriveLetter('');
      fetchMappings();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao adicionar mapeamento');
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (mappingId: string) => {
    try {
      await folderMappingService.remove(employee.id, mappingId);
      fetchMappings();
    } catch {
      // silently fail
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
                Usuario AD
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                {employee.ad_username}
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

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FolderIcon color="primary" />
              <Typography variant="h6">Pastas Mapeadas</Typography>
            </Box>
            <Button
              size="small"
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => { setError(null); setDialogOpen(true); }}
            >
              Adicionar
            </Button>
          </Box>

          {mappings.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
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
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleRemove(m.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Adicionar Mapeamento de Pasta</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {error && <Alert severity="error">{error}</Alert>}
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
          <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleAdd}
            disabled={!folderName.trim() || !driveLetter.trim() || saving}
          >
            {saving ? 'Adicionando...' : 'Adicionar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
