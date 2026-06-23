import React from 'react';
import { Chip } from '@mui/material';

interface EmployeeStatusChipProps {
  status: 'active' | 'disabled';
}

export const EmployeeStatusChip: React.FC<EmployeeStatusChipProps> = ({
  status,
}) => {
  const isActive = status === 'active';

  return (
    <Chip
      label={isActive ? 'Ativo' : 'Desabilitado'}
      color={isActive ? 'success' : 'error'}
      size="small"
      variant="outlined"
    />
  );
};
