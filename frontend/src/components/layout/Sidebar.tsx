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
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import BusinessIcon from '@mui/icons-material/Business';
import { useAuth } from '../../hooks/useAuth';
import { hasPermission } from '../../auth/roleGuard';
import logoBlumenau from '../../assets/logo-blumenau.png';

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
  const { permissions } = useAuth();

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
      visible: hasPermission(permissions, 'employee:create'),
    },
    {
      label: 'Colaboradores',
      path: '/employees',
      icon: <PeopleIcon />,
      visible: hasPermission(permissions, 'employee:list'),
    },
    {
      label: 'Departamentos',
      path: '/departments',
      icon: <BusinessIcon />,
      visible: hasPermission(permissions, 'user:manage'),
    },
    {
      label: 'Atividades',
      path: '/audit',
      icon: <HistoryIcon />,
      visible: hasPermission(permissions, 'user:manage'),
    },
    {
      label: 'Permissoes',
      path: '/permissions',
      icon: <AdminPanelSettingsIcon />,
      visible: hasPermission(permissions, 'user:manage'),
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
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      <Box sx={{ p: 2.5, textAlign: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 0.5 }}>
          <LightbulbIcon sx={{ color: '#ffb300', fontSize: 28, filter: 'drop-shadow(0 0 6px rgba(255,179,0,0.6))' }} />
          <Typography
            variant="h5"
            component="div"
            sx={{ fontWeight: 700, color: 'primary.main' }}
          >
            BluAdmin
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          Gestao de Colaboradores
        </Typography>
      </Box>

      <Divider />

      <List sx={{ px: 1, pt: 1, flexGrow: 1 }}>
        {navItems
          .filter((item) => item.visible)
          .map((item) => (
            <ListItemButton
              key={item.path}
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                transition: 'all 0.2s ease',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 168, 255, 0.15)',
                  color: 'primary.light',
                  boxShadow: '0 0 16px rgba(0, 168, 255, 0.2), inset 0 0 0 1px rgba(0, 168, 255, 0.3)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 168, 255, 0.2)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.light',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
      </List>

      <Divider />
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
          Uma solução
        </Typography>
        <Box
          component="img"
          src={logoBlumenau}
          alt="Blumenau Iluminação"
          sx={{ width: '70%', maxWidth: 150 }}
        />
      </Box>
    </Drawer>
  );
};
