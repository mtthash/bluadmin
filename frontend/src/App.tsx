import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './auth/AuthProvider';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import theme from './config/theme';
import { GlowCursor } from './components/effects/GlowCursor';

import { LoginPage } from './pages/LoginPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { DashboardPage } from './pages/DashboardPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { EmployeeListPage } from './pages/EmployeeListPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { PlatformUsersPage } from './pages/PlatformUsersPage';
import { DepartmentsPage } from './pages/DepartmentsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlowCursor />
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/unauthorized" element={<UnauthorizedPage />} />

              <Route
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<DashboardPage />} />
                <Route
                  path="onboarding"
                  element={
                    <ProtectedRoute requiredPermissions={['employee:create']}>
                      <OnboardingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="employees"
                  element={
                    <ProtectedRoute requiredPermissions={['employee:list']}>
                      <EmployeeListPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="employees/:id"
                  element={
                    <ProtectedRoute requiredPermissions={['employee:read']}>
                      <EmployeeDetailPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="audit"
                  element={
                    <ProtectedRoute requiredPermissions={['user:manage']}>
                      <AuditLogPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="departments"
                  element={
                    <ProtectedRoute requiredPermissions={['user:manage']}>
                      <DepartmentsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="permissions"
                  element={
                    <ProtectedRoute requiredPermissions={['user:manage']}>
                      <PlatformUsersPage />
                    </ProtectedRoute>
                  }
                />
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </QueryClientProvider>
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App;
