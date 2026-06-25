import api from './api';
import type { FolderMapping, FolderMappingCreate } from '../types/folderMapping';

export const folderMappingService = {
  list: async (employeeId: string): Promise<FolderMapping[]> => {
    const response = await api.get<FolderMapping[]>(
      `/employees/${employeeId}/folder-mappings`
    );
    return response.data;
  },

  create: async (
    employeeId: string,
    data: FolderMappingCreate
  ): Promise<FolderMapping> => {
    const response = await api.post<FolderMapping>(
      `/employees/${employeeId}/folder-mappings`,
      data
    );
    return response.data;
  },

  remove: async (employeeId: string, mappingId: string): Promise<void> => {
    await api.delete(`/employees/${employeeId}/folder-mappings/${mappingId}`);
  },
};
