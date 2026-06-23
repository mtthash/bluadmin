import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  MenuItem,
  Stack,
} from '@mui/material';
import type { AuditLogFilter } from '../../types/auditLog';

interface AuditLogFiltersProps {
  onApply: (filters: AuditLogFilter) => void;
  onClear: () => void;
}

const ACTION_OPTIONS = [
  { value: '', label: 'Todas as acoes' },
  { value: 'onboard', label: 'Onboarding' },
  { value: 'offboard', label: 'Offboarding' },
  { value: 'disable', label: 'Desabilitar' },
  { value: 'enable', label: 'Habilitar' },
  { value: 'update', label: 'Atualizar' },
];

export const AuditLogFilters: React.FC<AuditLogFiltersProps> = ({
  onApply,
  onClear,
}) => {
  const [action, setAction] = useState('');
  const [actorEmail, setActorEmail] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const handleApply = () => {
    const filters: AuditLogFilter = {};
    if (action) filters.action = action;
    if (actorEmail.trim()) filters.actor_email = actorEmail.trim();
    if (dateFrom) filters.date_from = dateFrom;
    if (dateTo) filters.date_to = dateTo;
    onApply(filters);
  };

  const handleClear = () => {
    setAction('');
    setActorEmail('');
    setDateFrom('');
    setDateTo('');
    onClear();
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="flex-end">
        <TextField
          select
          label="Tipo de acao"
          value={action}
          onChange={(e) => setAction(e.target.value)}
          size="small"
          sx={{ minWidth: 180 }}
        >
          {ACTION_OPTIONS.map((opt) => (
            <MenuItem key={opt.value} value={opt.value}>
              {opt.label}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          label="E-mail do executor"
          value={actorEmail}
          onChange={(e) => setActorEmail(e.target.value)}
          size="small"
          sx={{ minWidth: 220 }}
        />

        <TextField
          label="Data inicial"
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
          sx={{ minWidth: 160 }}
        />

        <TextField
          label="Data final"
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
          sx={{ minWidth: 160 }}
        />

        <Stack direction="row" spacing={1}>
          <Button variant="contained" onClick={handleApply} size="medium">
            Aplicar
          </Button>
          <Button variant="outlined" onClick={handleClear} size="medium">
            Limpar
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
};
