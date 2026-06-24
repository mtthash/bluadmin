import React from 'react';
import { Box, Button, Chip, Stack, Typography } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import type { AuditLogFilter } from '../../types/auditLog';

interface AuditLogFiltersProps {
  onApply: (filters: AuditLogFilter) => void;
  onClear: () => void;
  liveMode?: boolean;
  onToggleLive?: () => void;
}

const PERIOD_OPTIONS = [
  { label: '5 min', minutes: 5 },
  { label: '15 min', minutes: 15 },
  { label: '30 min', minutes: 30 },
  { label: '1 hora', minutes: 60 },
  { label: '6 horas', minutes: 360 },
  { label: '24 horas', minutes: 1440 },
  { label: '7 dias', minutes: 10080 },
  { label: '30 dias', minutes: 43200 },
];

export const AuditLogFilters: React.FC<AuditLogFiltersProps> = ({
  onApply,
  onClear,
  liveMode = false,
  onToggleLive,
}) => {
  const handlePeriod = (minutes: number) => {
    const from = new Date(Date.now() - minutes * 60 * 1000).toISOString();
    onApply({ date_from: from });
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
        <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
          Coletar:
        </Typography>
        {PERIOD_OPTIONS.map((opt) => (
          <Chip
            key={opt.minutes}
            label={opt.label}
            variant="outlined"
            onClick={() => handlePeriod(opt.minutes)}
            sx={{ cursor: 'pointer' }}
          />
        ))}
        <Chip label="Tudo" variant="outlined" onClick={onClear} sx={{ cursor: 'pointer' }} />

        <Box sx={{ flexGrow: 1 }} />

        {onToggleLive && (
          <Button
            variant={liveMode ? 'contained' : 'outlined'}
            color={liveMode ? 'error' : 'primary'}
            size="small"
            startIcon={liveMode ? <StopIcon /> : <PlayArrowIcon />}
            onClick={onToggleLive}
            sx={{
              animation: liveMode ? 'pulse 2s infinite' : 'none',
              '@keyframes pulse': {
                '0%, 100%': { boxShadow: '0 0 0 0 rgba(255,82,82,0.4)' },
                '50%': { boxShadow: '0 0 12px 4px rgba(255,82,82,0.3)' },
              },
            }}
          >
            {liveMode ? 'Parar' : 'Tempo Real'}
          </Button>
        )}
      </Stack>
    </Box>
  );
};
