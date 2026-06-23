import React from 'react';
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
} from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import VpnKeyOffIcon from '@mui/icons-material/VpnKeyOff';
import GroupRemoveIcon from '@mui/icons-material/GroupRemove';
import CardMembershipIcon from '@mui/icons-material/CardMembership';
import type { Employee } from '../../types/employee';

interface OffboardDialogProps {
  open: boolean;
  employee: Employee | null;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const OffboardDialog: React.FC<OffboardDialogProps> = ({
  open,
  employee,
  loading,
  onConfirm,
  onCancel,
}) => {
  if (!employee) return null;

  return (
    <Dialog open={open} onClose={loading ? undefined : onCancel} maxWidth="sm" fullWidth>
      <DialogTitle>Desligar Colaborador</DialogTitle>
      <DialogContent>
        <Typography variant="body1" gutterBottom>
          Voce esta prestes a desligar o colaborador:
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
            <ListItemText primary="Bloquear login" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <VpnKeyOffIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Revogar sessoes ativas" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <GroupRemoveIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Remover de todos os grupos" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CardMembershipIcon color="error" />
            </ListItemIcon>
            <ListItemText primary="Remover todas as licencas" />
          </ListItem>
        </List>

        <Alert severity="warning" sx={{ mt: 2 }}>
          Esta acao nao pode ser facilmente revertida.
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} disabled={loading} color="inherit">
          Cancelar
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          variant="contained"
          color="error"
          startIcon={loading ? <CircularProgress size={18} /> : undefined}
        >
          {loading ? 'Processando...' : 'Desligar Colaborador'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
