import React from 'react';
import { Autocomplete, TextField, CircularProgress } from '@mui/material';
import { useDepartments } from '../../hooks/useDepartments';

interface DepartmentValue {
  id: string;
  display_name: string;
}

interface DepartmentSelectProps {
  value: DepartmentValue | null;
  onChange: (dept: DepartmentValue | null) => void;
}

export const DepartmentSelect: React.FC<DepartmentSelectProps> = ({
  value,
  onChange,
}) => {
  const { data: departments, isLoading } = useDepartments();

  const options: DepartmentValue[] = (departments ?? []).map((dept) => ({
    id: dept.id,
    display_name: dept.display_name,
  }));

  return (
    <Autocomplete
      options={options}
      getOptionLabel={(opt) => opt.display_name}
      isOptionEqualToValue={(opt, val) => opt.id === val.id}
      value={value}
      onChange={(_event, newValue) => onChange(newValue)}
      loading={isLoading}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Departamento"
          slotProps={{
            input: {
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoading ? <CircularProgress size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
      noOptionsText="Nenhum departamento encontrado"
      loadingText="Carregando..."
    />
  );
};
