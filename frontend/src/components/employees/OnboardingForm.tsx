import React, { useState } from 'react';
import {
  Stepper,
  Step,
  StepLabel,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  IconButton,
  InputAdornment,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tooltip,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { useOnboardEmployee } from '../../hooks/useEmployees';
import { DepartmentSelect } from '../departments/DepartmentSelect';
import { ErrorAlert } from '../common/ErrorAlert';
import type { EmployeeCreate } from '../../types/employee';

interface FormData {
  first_name: string;
  last_name: string;
  mail_nickname: string;
  department_group_id: string | null;
  department_name: string | null;
  job_title: string;
  password: string;
}

interface FormErrors {
  first_name?: string;
  last_name?: string;
  mail_nickname?: string;
  job_title?: string;
  password?: string;
}

const STEPS = ['Informacoes Basicas', 'Departamento e Cargo', 'Senha'];

function getPasswordStrength(password: string): {
  score: number;
  label: string;
} {
  let score = 0;
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 2) return { score: 25, label: 'Fraca' };
  if (score <= 3) return { score: 50, label: 'Media' };
  if (score <= 4) return { score: 75, label: 'Forte' };
  return { score: 100, label: 'Muito forte' };
}

function getStrengthColor(
  score: number,
): 'error' | 'warning' | 'info' | 'success' {
  if (score <= 25) return 'error';
  if (score <= 50) return 'warning';
  if (score <= 75) return 'info';
  return 'success';
}

export const OnboardingForm: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [successDialogOpen, setSuccessDialogOpen] = useState(false);

  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    mail_nickname: '',
    department_group_id: null,
    department_name: null,
    job_title: '',
    password: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});

  const onboardMutation = useOnboardEmployee();

  const updateField = (field: keyof FormData, value: string | null) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {};

    if (step === 0) {
      if (!formData.first_name.trim()) {
        newErrors.first_name = 'Nome e obrigatorio';
      }
      if (!formData.last_name.trim()) {
        newErrors.last_name = 'Sobrenome e obrigatorio';
      }
      if (!formData.mail_nickname.trim()) {
        newErrors.mail_nickname = 'Apelido de e-mail e obrigatorio';
      } else if (!/^[a-zA-Z0-9._-]+$/.test(formData.mail_nickname)) {
        newErrors.mail_nickname =
          'Apelido de e-mail deve conter apenas letras, numeros, pontos, hifens e underscores';
      }
    }

    if (step === 2) {
      if (!formData.password) {
        newErrors.password = 'Senha e obrigatoria';
      } else if (formData.password.length < 12) {
        newErrors.password = 'Senha deve ter pelo menos 12 caracteres';
      } else if (
        !/(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])/.test(formData.password)
      ) {
        newErrors.password =
          'Senha deve conter maiusculas, minusculas, numeros e caracteres especiais';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(activeStep)) return;

    const payload: EmployeeCreate = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      mail_nickname: formData.mail_nickname.trim(),
      password: formData.password,
      department_group_id: formData.department_group_id,
      department_name: formData.department_name,
      job_title: formData.job_title.trim() || null,
    };

    try {
      const result = await onboardMutation.mutateAsync(payload);
      setSuccessDialogOpen(true);
    } catch {
      // Error handled by mutation state
    }
  };

  const handleSuccessClose = () => {
    setSuccessDialogOpen(false);
    setTemporaryPassword('');
    setFormData({
      first_name: '',
      last_name: '',
      mail_nickname: '',
      department_group_id: null,
      department_name: null,
      job_title: '',
      password: '',
    });
    setActiveStep(0);
    setCopied(false);
  };

  const passwordStrength = getPasswordStrength(formData.password);

  const apiErrorMessage =
    onboardMutation.error instanceof Error
      ? onboardMutation.error.message
      : (
            onboardMutation.error as {
              response?: { data?: { detail?: string } };
            }
          )?.response?.data?.detail ?? 'Erro ao realizar onboarding';

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Nome"
              value={formData.first_name}
              onChange={(e) => updateField('first_name', e.target.value)}
              error={!!errors.first_name}
              helperText={errors.first_name}
              fullWidth
              required
            />
            <TextField
              label="Sobrenome"
              value={formData.last_name}
              onChange={(e) => updateField('last_name', e.target.value)}
              error={!!errors.last_name}
              helperText={errors.last_name}
              fullWidth
              required
            />
            <TextField
              label="Apelido de E-mail (mail nickname)"
              value={formData.mail_nickname}
              onChange={(e) => updateField('mail_nickname', e.target.value)}
              error={!!errors.mail_nickname}
              helperText={
                errors.mail_nickname ??
                'Sera usado para criar o endereco de e-mail'
              }
              fullWidth
              required
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <DepartmentSelect
              value={
                formData.department_group_id
                  ? {
                      id: formData.department_group_id,
                      display_name: formData.department_name ?? '',
                    }
                  : null
              }
              onChange={(dept) => {
                updateField(
                  'department_group_id',
                  dept ? dept.id : null,
                );
                updateField(
                  'department_name',
                  dept ? dept.display_name : null,
                );
              }}
            />
            <TextField
              label="Cargo"
              value={formData.job_title}
              onChange={(e) => updateField('job_title', e.target.value)}
              error={!!errors.job_title}
              helperText={errors.job_title}
              fullWidth
            />
          </Box>
        );

      case 2:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Senha temporaria"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => updateField('password', e.target.value)}
              error={!!errors.password}
              helperText={errors.password}
              fullWidth
              required
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        aria-label={
                          showPassword ? 'Ocultar senha' : 'Mostrar senha'
                        }
                      >
                        {showPassword ? (
                          <VisibilityOffIcon />
                        ) : (
                          <VisibilityIcon />
                        )}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
            {formData.password && (
              <Box>
                <Box
                  sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Forca da senha
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {passwordStrength.label}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={passwordStrength.score}
                  color={getStrengthColor(passwordStrength.score)}
                />
              </Box>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  const renderReview = () => (
    <Paper variant="outlined" sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Revisao dos dados
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Nome completo
          </Typography>
          <Typography>
            {formData.first_name} {formData.last_name}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Apelido de e-mail
          </Typography>
          <Typography>{formData.mail_nickname}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Departamento
          </Typography>
          <Typography>
            {formData.department_name ?? 'Nao informado'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Cargo
          </Typography>
          <Typography>{formData.job_title || 'Nao informado'}</Typography>
        </Box>
      </Box>
    </Paper>
  );

  return (
    <Box sx={{ maxWidth: 700, mx: 'auto' }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {onboardMutation.isError && <ErrorAlert message={apiErrorMessage} />}

      {activeStep < STEPS.length ? (
        <>
          {renderStepContent(activeStep)}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              variant="outlined"
            >
              Voltar
            </Button>
            <Button variant="contained" onClick={handleNext}>
              Proximo
            </Button>
          </Box>
        </>
      ) : (
        <>
          {renderReview()}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button onClick={handleBack} variant="outlined">
              Voltar
            </Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={onboardMutation.isPending}
            >
              {onboardMutation.isPending
                ? 'Processando...'
                : 'Confirmar Onboarding'}
            </Button>
          </Box>
        </>
      )}

      <Dialog
        open={successDialogOpen}
        onClose={handleSuccessClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Colaborador criado com sucesso!</DialogTitle>
        <DialogContent>
          <Alert severity="success">
            O colaborador foi criado e configurado com sucesso.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSuccessClose} variant="contained">
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
