// import React from 'react'; // Убираем неиспользуемый импорт
import { Box, Title } from '@mantine/core';
// Удаляем импорт DashboardLayout - в этом нет необходимости, т.к. App.tsx уже оборачивает компонент в DashboardLayout
// import { DashboardLayout } from '../layouts/DashboardLayout';

export const DashboardPage = () => {
  return (
    // Удаляем обертку DashboardLayout, т.к. App.tsx уже оборачивает компонент в DashboardLayout через WrappedRoute
    <Box p="md">
      <Title order={2}>Главная страница</Title>
      {/* Здесь будет содержимое дашборда */}
      <p>Добро пожаловать в систему OFS Photomatrix!</p>
    </Box>
  );
};

// Не используем default экспорт, чтобы соответствовать соглашениям проекта
// export default DashboardPage; 