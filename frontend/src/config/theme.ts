import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1565C0',
    },
    secondary: {
      main: '#00838F',
    },
    error: {
      main: '#C62828',
    },
    warning: {
      main: '#F57F17',
    },
    success: {
      main: '#2E7D32',
    },
    background: {
      default: '#F5F5F5',
    },
  },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(
      ', ',
    ),
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          border: '1px solid #E0E0E0',
        },
      },
    },
  },
});

export default theme;
