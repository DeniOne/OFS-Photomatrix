import React from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Box, Text } from '@mantine/core';

export const DashboardPage = () => {
  return (
    <DashboardLayout>
      <Box>
        <Text size="xl" fw={700} mb="lg">Добро пожаловать на дашборд!</Text>
        <Text>Здесь будет основное содержимое вашей панели управления.</Text>
        {/* Добавьте сюда компоненты для дашборда: карточки, графики и т.д. */}
      </Box>
    </DashboardLayout>
  );
};

// Не используем default экспорт, чтобы соответствовать DashboardLayout
// export default DashboardPage; 