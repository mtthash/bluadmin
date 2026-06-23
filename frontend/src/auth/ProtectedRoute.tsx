import React from 'react';
import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
} from '@azure/msal-react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { hasAnyRole } from './roleGuard';
import type { AppRole } from '../types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: AppRole[];
}

const RoleGate: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
}) => {
  const { roles } = useAuth();

  if (requiredRoles && requiredRoles.length > 0) {
    if (!hasAnyRole(roles, requiredRoles)) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
}) => {
  return (
    <>
      <AuthenticatedTemplate>
        <RoleGate requiredRoles={requiredRoles}>{children}</RoleGate>
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <Navigate to="/login" replace />
      </UnauthenticatedTemplate>
    </>
  );
};
