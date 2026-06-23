import { useQuery } from '@tanstack/react-query';
import { departmentService } from '../services/departmentService';

export function useDepartments() {
  return useQuery({
    queryKey: ['departments'],
    queryFn: departmentService.list,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
