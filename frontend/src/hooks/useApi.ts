import { useMemo } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useAuth } from './useAuth';

/**
 * Hook que retorna uma instancia axios configurada com interceptor de token.
 * Para a maioria dos casos, importe diretamente de services/api.ts.
 */
export function useApi() {
  const { getAccessToken } = useAuth();

  const apiClient = useMemo(() => {
    const client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    client.interceptors.request.use(async (config) => {
      try {
        const token = await getAccessToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch {
        // Token acquisition failed — request proceeds without auth header
      }
      return config;
    });

    return client;
  }, [getAccessToken]);

  return apiClient;
}
