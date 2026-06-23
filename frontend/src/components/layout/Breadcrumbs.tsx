import React from 'react';
import { useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Breadcrumbs as MuiBreadcrumbs,
  Link,
  Typography,
  Box,
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

const PATH_LABELS: Record<string, string> = {
  '': 'Dashboard',
  onboarding: 'Onboarding',
  employees: 'Colaboradores',
  audit: 'Logs de Auditoria',
  unauthorized: 'Nao Autorizado',
};

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const segments = location.pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <Box sx={{ mb: 2 }}>
      <MuiBreadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
        <Link
          component={RouterLink}
          to="/"
          underline="hover"
          color="inherit"
          variant="body2"
        >
          Dashboard
        </Link>
        {segments.map((segment, index) => {
          const path = '/' + segments.slice(0, index + 1).join('/');
          const isLast = index === segments.length - 1;
          const label = PATH_LABELS[segment] ?? segment;

          if (isLast) {
            return (
              <Typography key={path} variant="body2" color="text.primary">
                {label}
              </Typography>
            );
          }

          return (
            <Link
              key={path}
              component={RouterLink}
              to={path}
              underline="hover"
              color="inherit"
              variant="body2"
            >
              {label}
            </Link>
          );
        })}
      </MuiBreadcrumbs>
    </Box>
  );
};
