import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  Grid,
  CircularProgress,
} from '@mui/material';
import WallpaperIcon from '@mui/icons-material/Wallpaper';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import api from '../services/api';

interface PolicyStatus {
  policy: string;
  status: string;
  detail: string | null;
}

export const PoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const response = await api.get<PolicyStatus[]>('/policies/');
      setPolicies(response.data);
    } catch {
      setPolicies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Selecione um arquivo de imagem (JPG, PNG, BMP)' });
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'A imagem deve ter no maximo 10MB' });
      return;
    }

    setSelectedFile(file);
    setMessage(null);

    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await api.post<PolicyStatus>('/policies/wallpaper', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000,
      });
      setMessage({ type: 'success', text: response.data.detail || 'Wallpaper aplicado com sucesso!' });
      setSelectedFile(null);
      setPreview(null);
      fetchPolicies();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setMessage({
        type: 'error',
        text: axiosErr?.response?.data?.detail || 'Erro ao aplicar wallpaper',
      });
    } finally {
      setUploading(false);
    }
  };

  const wallpaperPolicy = policies.find((p) => p.policy === 'wallpaper');

  if (loading) return <LoadingSpinner message="Carregando politicas..." />;

  return (
    <Box>
      <PageHeader
        title="Politicas (GPO)"
        subtitle="Gerencie politicas aplicadas as maquinas do dominio"
      />

      <Grid container spacing={3}>
        {/* Wallpaper */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <WallpaperIcon color="primary" />
                <Typography variant="h6">Wallpaper Corporativo</Typography>
                {wallpaperPolicy && (
                  <Chip
                    label={wallpaperPolicy.status === 'active' ? 'Ativo' : 'Inativo'}
                    size="small"
                    color={wallpaperPolicy.status === 'active' ? 'success' : 'default'}
                    variant="outlined"
                    sx={{ ml: 'auto' }}
                  />
                )}
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Envie uma imagem para definir o wallpaper de todas as maquinas do dominio.
                A alteracao sera aplicada no proximo logon dos usuarios.
              </Typography>

              {message && (
                <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage(null)}>
                  {message.text}
                </Alert>
              )}

              {wallpaperPolicy?.detail && wallpaperPolicy.status === 'active' && (
                <Alert severity="info" variant="outlined" sx={{ mb: 2 }}>
                  Wallpaper atual: {wallpaperPolicy.detail}
                </Alert>
              )}

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {preview && (
                  <Box
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      overflow: 'hidden',
                      maxHeight: 300,
                    }}
                  >
                    <Box
                      component="img"
                      src={preview}
                      alt="Preview do wallpaper"
                      sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </Box>
                )}

                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<CloudUploadIcon />}
                  >
                    Selecionar Imagem
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </Button>

                  {selectedFile && (
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={uploading ? <CircularProgress size={18} color="inherit" /> : <CheckCircleIcon />}
                        onClick={handleUpload}
                        disabled={uploading}
                      >
                        {uploading ? 'Aplicando...' : 'Aplicar Wallpaper'}
                      </Button>
                    </>
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Futuras politicas */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Politicas Disponiveis</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1.5, borderRadius: 1, bgcolor: 'action.hover' }}>
                  <WallpaperIcon fontSize="small" color="primary" />
                  <Typography variant="body2">Wallpaper Corporativo</Typography>
                  <Chip label="Disponivel" size="small" color="success" variant="outlined" sx={{ ml: 'auto' }} />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1.5, borderRadius: 1, opacity: 0.5 }}>
                  <WallpaperIcon fontSize="small" />
                  <Typography variant="body2">Tela de Bloqueio</Typography>
                  <Chip label="Em breve" size="small" variant="outlined" sx={{ ml: 'auto' }} />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1.5, borderRadius: 1, opacity: 0.5 }}>
                  <WallpaperIcon fontSize="small" />
                  <Typography variant="body2">Pagina Inicial do Navegador</Typography>
                  <Chip label="Em breve" size="small" variant="outlined" sx={{ ml: 'auto' }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
