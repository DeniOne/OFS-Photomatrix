// import React from 'react'; // Убираем неиспользуемый импорт
import { Box, Title } from '@mantine/core';
import { DashboardLayout } from '../layouts/DashboardLayout'; // Используем именованный импорт

export const DashboardPage = () => { // Экспортируем именованно, как в App.tsx
  return (
    <DashboardLayout>
      <Box p="md">
        <Title order={2}>Главная страница</Title>
        {/* Здесь будет содержимое дашборда */}
        <p>Добро пожаловать в систему OFS Photomatrix!</p>
      </Box>
    </DashboardLayout>
  );
};

// Не используем default экспорт, чтобы соответствовать DashboardLayout
// export default DashboardPage; 