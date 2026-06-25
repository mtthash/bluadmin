export interface FolderMapping {
  id: string;
  folder_name: string;
  drive_letter: string;
  unc_path: string;
  is_default: boolean;
  created_at: string;
}

export interface FolderMappingCreate {
  folder_name: string;
  drive_letter: string;
}
