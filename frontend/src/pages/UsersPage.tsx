import { Box, Title } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { DashboardLayout } from '@/layouts/DashboardLayout';

// Определим тип пользователя (если еще не определен глобально)
interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

const UsersPage = () => {
  // Заглушка для получения пользователей (замените на реальный запрос)
  const { data: users, isLoading, error } = useQuery<User[], Error>({
      queryKey: ['users'], 
      queryFn: async () => { 
          // TODO: Замените на реальный вызов API 
          // const response = await apiClient.get('/users');
          // return response.data;
          await new Promise(resolve => setTimeout(resolve, 1000)); // Имитация задержки
          return [
              { id: 1, email: 'admin@example.com', full_name: 'Admin User', is_active: true, is_superuser: true },
              { id: 2, email: 'user@example.com', full_name: 'Regular User', is_active: true, is_superuser: false },
          ]; 
      }
  });

  return (
    <DashboardLayout>
      <Box p="md">
        <Title order={2} mb="lg">Управление Пользователями</Title>
        {/* TODO: Добавить таблицу пользователей, кнопки и т.д. */}
        {isLoading && <p>Загрузка пользователей...</p>}
        {error && <p style={{ color: 'red' }}>Ошибка загрузки: {error.message}</p>}
        {users && (
          <ul>
            {users.map(user => (
              <li key={user.id}>{user.email} ({user.full_name || '-'})</li>
            ))}
          </ul>
        )}
      </Box>
    </DashboardLayout>
  );
};

export default UsersPage; 