export interface ApiError {
  detail: string;
  error_code?: string;
}

export interface PaginationParams {
  page: number;
  size: number;
}
