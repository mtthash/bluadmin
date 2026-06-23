import React from 'react';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from '../config/authConfig';

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
};
