export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const backendClientId = import.meta.env.VITE_AZURE_BACKEND_CLIENT_ID;

export const defaultScopes = [
  `api://${backendClientId}/access_as_user`,
];
