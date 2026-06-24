import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { hasAllPermissions } from './roleGuard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions,
}) => {
  const { isAuthenticated, isLoading, permissions } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredPermissions && requiredPermissions.length > 0) {
    if (!hasAllPermissions(permissions, requiredPermissions)) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};
