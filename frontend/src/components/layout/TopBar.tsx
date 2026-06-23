import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Avatar,
  Box,
  IconButton,
  Chip,
  Tooltip,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../../hooks/useAuth';

export const TopBar: React.FC = () => {
  const { user, roles, logout } = useAuth();

  const initials = user?.name
    ? user.name
        .split(' ')
        .map((part) => part[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : '?';

  return (
    <AppBar
      position="sticky"
      color="inherit"
      elevation={0}
      sx={{ borderBottom: '1px solid', borderColor: 'divider' }}
    >
      <Toolbar>
        <Box sx={{ flexGrow: 1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {roles.map((role) => (
            <Chip
              key={role}
              label={role}
              size="small"
              color="primary"
              variant="outlined"
            />
          ))}

          <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
            <Typography variant="body2">{initials}</Typography>
          </Avatar>

          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Typography variant="body2" fontWeight={600}>
              {user?.name ?? ''}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.email ?? ''}
            </Typography>
          </Box>

          <Tooltip title="Sair">
            <IconButton onClick={logout} size="small" color="default">
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};
