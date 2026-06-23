import React from 'react';
import { Box } from '@mui/material';
import { PageHeader } from '../components/common/PageHeader';
import { OnboardingForm } from '../components/employees/OnboardingForm';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';

export const OnboardingPage: React.FC = () => {
  return (
    <Box>
      <Breadcrumbs />
      <PageHeader
        title="Onboarding de Colaborador"
        subtitle="Cadastre um novo colaborador no sistema"
      />
      <OnboardingForm />
    </Box>
  );
};
