import { createTheme, alpha } from '@mui/material/styles';

const BRAND_BLUE = '#00a8ff';
const BRAND_BLUE_LIGHT = '#4dc3ff';
const BRAND_BLUE_DARK = '#0080cc';

const SURFACE_DARK = '#121820';
const SURFACE_CARD = '#1a2332';
const SURFACE_ELEVATED = '#1e2a3a';
const BORDER_COLOR = '#2a3a4e';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: BRAND_BLUE,
      light: BRAND_BLUE_LIGHT,
      dark: BRAND_BLUE_DARK,
      contrastText: '#fff',
    },
    secondary: {
      main: '#ffb300',
      light: '#ffc946',
      dark: '#c68400',
    },
    error: {
      main: '#ff5252',
    },
    warning: {
      main: '#ffb300',
    },
    success: {
      main: '#4caf50',
    },
    background: {
      default: SURFACE_DARK,
      paper: SURFACE_CARD,
    },
    divider: BORDER_COLOR,
    text: {
      primary: '#e8edf3',
      secondary: '#8899aa',
    },
  },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(
      ', ',
    ),
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: `radial-gradient(ellipse at 50% 0%, ${alpha(BRAND_BLUE, 0.08)} 0%, transparent 60%)`,
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          textTransform: 'none' as const,
          fontWeight: 600,
          borderRadius: 8,
        },
        contained: {
          boxShadow: `0 0 20px ${alpha(BRAND_BLUE, 0.3)}`,
          '&:hover': {
            boxShadow: `0 0 30px ${alpha(BRAND_BLUE, 0.5)}`,
          },
        },
        outlined: {
          borderColor: BORDER_COLOR,
          '&:hover': {
            borderColor: BRAND_BLUE,
            backgroundColor: alpha(BRAND_BLUE, 0.08),
          },
        },
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          border: `1px solid ${BORDER_COLOR}`,
          backgroundColor: SURFACE_CARD,
          backgroundImage: 'none',
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          '&:hover': {
            borderColor: alpha(BRAND_BLUE, 0.4),
            boxShadow: `0 0 20px ${alpha(BRAND_BLUE, 0.1)}`,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: SURFACE_CARD,
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: SURFACE_CARD,
          backgroundImage: 'none',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&:hover': {
            backgroundColor: alpha(BRAND_BLUE, 0.08),
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
        outlined: {
          borderColor: BORDER_COLOR,
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: BORDER_COLOR,
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: `1px solid ${BORDER_COLOR}`,
          borderRadius: 12,
          '& .MuiDataGrid-cell': {
            borderColor: BORDER_COLOR,
          },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: SURFACE_ELEVATED,
            borderColor: BORDER_COLOR,
          },
          '& .MuiDataGrid-row:hover': {
            backgroundColor: alpha(BRAND_BLUE, 0.06),
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: BORDER_COLOR,
            },
            '&:hover fieldset': {
              borderColor: BRAND_BLUE,
            },
            '&.Mui-focused fieldset': {
              boxShadow: `0 0 8px ${alpha(BRAND_BLUE, 0.3)}`,
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: BORDER_COLOR,
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: BRAND_BLUE,
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: SURFACE_ELEVATED,
          border: `1px solid ${BORDER_COLOR}`,
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: BRAND_BLUE_DARK,
        },
      },
    },
  },
});

export default theme;
