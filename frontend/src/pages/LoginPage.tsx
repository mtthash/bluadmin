import React from 'react';
import { Box, Paper, Typography, Button } from '@mui/material';
import MicrosoftIcon from '@mui/icons-material/Microsoft';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();

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
      <Paper
        sx={{
          p: 5,
          maxWidth: 420,
          width: '100%',
          textAlign: 'center',
        }}
      >
        <Typography
          variant="h4"
          fontWeight={700}
          color="primary.main"
          gutterBottom
        >
          BluAdmin
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Gestao de Colaboradores
        </Typography>

        <Button
          variant="contained"
          size="large"
          startIcon={<MicrosoftIcon />}
          onClick={login}
          fullWidth
          sx={{ textTransform: 'none', py: 1.5 }}
        >
          Entrar com Microsoft
        </Button>
      </Paper>
    </Box>
  );
};
