import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  TextField,
  MenuItem,
  Box,
} from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import GroupRemoveIcon from '@mui/icons-material/GroupRemove';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import TimerIcon from '@mui/icons-material/Timer';
import type { Employee } from '../../types/employee';

const RETENTION_OPTIONS = [
  { label: '5 minutos (teste)', value: 5 },
  { label: '30 minutos', value: 30 },
  { label: '1 hora', value: 60 },
  { label: '24 horas', value: 1440 },
  { label: '7 dias', value: 10080 },
  { label: '15 dias', value: 21600 },
  { label: '30 dias', value: 43200 },
  { label: '60 dias', value: 86400 },
  { label: '90 dias', value: 129600 },
];

interface OffboardDialogProps {
  open: boolean;
  employee: Employee | null;
  loading: boolean;
  onConfirm: (retentionMinutes: number) => void;
  onCancel: () => void;
}

export const OffboardDialog: React.FC<OffboardDialogProps> = ({
  open,
  employee,
  loading,
  onConfirm,
  onCancel,
}) => {
  const [retentionMinutes, setRetentionMinutes] = useState(43200);

  if (!employee) return null;

  const selectedOption = RETENTION_OPTIONS.find((o) => o.value === retentionMinutes);

  return (
    <Dialog open={open} onClose={loading ? undefined : onCancel} maxWidth="sm" fullWidth>
      <DialogTitle>Desativar Colaborador</DialogTitle>
      <DialogContent>
        <Typography variant="body1" gutterBottom>
          Voce esta prestes a desativar o colaborador:
        </Typography>
        <Typography variant="subtitle1" fontWeight={600}>
          {employee.display_name}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {employee.email}
        </Typography>

        <Typography variant="body2" sx={{ mb: 1 }}>
          As seguintes acoes serao executadas:
        </Typography>

        <List dense>
          <ListItem>
            <ListItemIcon>
              <BlockIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Bloquear login no Active Directory" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <GroupRemoveIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Remover de todos os grupos" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <DeleteForeverIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Agendar exclusao definitiva do AD" />
          </ListItem>
        </List>

        <Box sx={{ mt: 2, mb: 1 }}>
          <TextField
            select
            label="Prazo para exclusao definitiva"
            value={retentionMinutes}
            onChange={(e) => setRetentionMinutes(Number(e.target.value))}
            fullWidth
            slotProps={{
              input: {
                startAdornment: <TimerIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              },
            }}
          >
            {RETENTION_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
        </Box>

        <Alert severity="warning" sx={{ mt: 2 }}>
          Apos {selectedOption?.label ?? `${retentionMinutes} minutos`}, o colaborador sera
          removido permanentemente do Active Directory.
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} disabled={loading} color="inherit">
          Cancelar
        </Button>
        <Button
          onClick={() => onConfirm(retentionMinutes)}
          disabled={loading}
          variant="contained"
          color="error"
          startIcon={loading ? <CircularProgress size={18} /> : undefined}
        >
          {loading ? 'Processando...' : 'Desativar Colaborador'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
