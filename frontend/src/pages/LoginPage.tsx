import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import LoginIcon from '@mui/icons-material/Login';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import logoBlumenau from '../assets/logo-blumenau.png';

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha na autenticacao');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        backgroundImage: 'radial-gradient(ellipse at 50% 30%, rgba(0,168,255,0.12) 0%, transparent 60%)',
      }}
    >
      <Paper
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 5,
          maxWidth: 420,
          width: '100%',
          textAlign: 'center',
          border: '1px solid rgba(0,168,255,0.2)',
          boxShadow: '0 0 40px rgba(0,168,255,0.1)',
        }}
      >
        <LightbulbIcon sx={{ fontSize: 48, color: '#ffb300', filter: 'drop-shadow(0 0 10px rgba(255,179,0,0.6))', mb: 1 }} />
        <Typography variant="h4" fontWeight={700} color="primary.main" gutterBottom>
          BluAdmin
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Gestao de Colaboradores
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2, textAlign: 'left' }}>
            {error}
          </Alert>
        )}

        <TextField
          label="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
          autoFocus
          autoComplete="username"
          sx={{ mb: 2 }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <PersonIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            },
          }}
        />

        <TextField
          label="Senha"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
          autoComplete="current-password"
          sx={{ mb: 3 }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
        />

        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          disabled={isSubmitting || !username || !password}
          startIcon={<LoginIcon />}
          sx={{ py: 1.5, mb: 3 }}
        >
          {isSubmitting ? 'Entrando...' : 'Entrar'}
        </Button>

        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
          Uma solução
        </Typography>
        <Box
          component="img"
          src={logoBlumenau}
          alt="Blumenau Iluminação"
          sx={{ width: '50%', maxWidth: 160, opacity: 0.85 }}
        />
      </Paper>
    </Box>
  );
};
