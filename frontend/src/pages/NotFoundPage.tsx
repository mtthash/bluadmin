import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Paper } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';

export const NotFoundPage: React.FC = () => {
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
        <SearchOffIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h4" fontWeight={600} gutterBottom>
          404
        </Typography>
        <Typography variant="h6" gutterBottom>
          Pagina nao encontrada
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          A pagina que voce esta procurando nao existe ou foi removida.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/')}>
          Ir para o Dashboard
        </Button>
      </Paper>
    </Box>
  );
};
