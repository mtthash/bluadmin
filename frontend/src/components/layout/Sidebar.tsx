import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PeopleIcon from '@mui/icons-material/People';
import HistoryIcon from '@mui/icons-material/History';
import { useAuth } from '../../hooks/useAuth';
import { hasAnyRole, canViewAudit } from '../../auth/roleGuard';

interface SidebarProps {
  width: number;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  visible: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ width }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { roles } = useAuth();

  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      path: '/',
      icon: <DashboardIcon />,
      visible: true,
    },
    {
      label: 'Onboarding',
      path: '/onboarding',
      icon: <PersonAddIcon />,
      visible: hasAnyRole(roles, ['HR', 'IT', 'Admin']),
    },
    {
      label: 'Colaboradores',
      path: '/employees',
      icon: <PeopleIcon />,
      visible: hasAnyRole(roles, ['HR', 'IT', 'Admin']),
    },
    {
      label: 'Logs de Auditoria',
      path: '/audit',
      icon: <HistoryIcon />,
      visible: canViewAudit(roles),
    },
  ];

  const isActive = (path: string): boolean => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography
          variant="h5"
          component="div"
          sx={{ fontWeight: 700, color: 'primary.main' }}
        >
          BluAdmin
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Gestao de Colaboradores
        </Typography>
      </Box>

      <Divider />

      <List sx={{ px: 1, pt: 1 }}>
        {navItems
          .filter((item) => item.visible)
          .map((item) => (
            <ListItemButton
              key={item.path}
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 1,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
      </List>
    </Drawer>
  );
};
