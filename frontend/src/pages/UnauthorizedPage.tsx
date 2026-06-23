import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Paper } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';

export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Paper sx={{ p: 5, textAlign: 'center', maxWidth: 480 }}>
        <LockIcon sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
        <Typography variant="h4" fontWeight={600} gutterBottom>
          403
        </Typography>
        <Typography variant="h6" gutterBottom>
          Acesso nao autorizado
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Voce nao tem permissao para acessar esta pagina. Entre em contato com
          o administrador caso acredite que isso seja um erro.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/')}>
          Ir para o Dashboard
        </Button>
      </Paper>
    </Box>
  );
};
