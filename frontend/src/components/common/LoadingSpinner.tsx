import React from 'react';
import { Box, Typography } from '@mui/material';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined';
import { keyframes } from '@mui/material/styles';

const pulse = keyframes`
  0%, 100% {
    opacity: 0.15;
    filter: drop-shadow(0 0 2px rgba(255,179,0,0.1));
  }
  50% {
    opacity: 1;
    filter: drop-shadow(0 0 16px rgba(255,179,0,0.7)) drop-shadow(0 0 40px rgba(255,179,0,0.3));
  }
`;

const glowRing = keyframes`
  0%, 100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
`;

interface LoadingSpinnerProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        gap: 2,
      }}
    >
      <Box sx={{ position: 'relative', width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,179,0,0.15) 0%, transparent 70%)',
            animation: `${glowRing} 1.8s ease-in-out infinite`,
          }}
        />
        <LightbulbOutlinedIcon
          sx={{
            fontSize: 52,
            color: '#ffb300',
            position: 'absolute',
            opacity: 0.2,
          }}
        />
        <LightbulbIcon
          sx={{
            fontSize: 52,
            color: '#ffb300',
            animation: `${pulse} 1.8s ease-in-out infinite`,
          }}
        />
      </Box>
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );
};
