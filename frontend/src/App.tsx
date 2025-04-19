import { useState, useEffect } from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import '@mantine/core/styles.css';
import { Notifications } from '@mantine/notifications';
import './App.css';
import theme from './styles/theme'; // Подключаем нашу тему

// Импортируем реальные страницы и лейаут
import LoginPage from './pages/LoginPage'; 
import { DashboardPage } from './pages/DashboardPage'; // Используем именованный импорт
import UsersPage from './pages/UsersPage'; // Импортируем UsersPage
import OrganizationsPage from './pages/OrganizationsPage'; // Импорт новой страницы
// DashboardLayout будет использоваться внутри DashboardPage, отдельно импортировать не нужно

// Создаем клиент React Query
const queryClient = new QueryClient();

function App() {
  // Состояние для статуса аутентификации
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true); // Состояние для начальной проверки

  useEffect(() => {
    // Проверяем наличие токена при загрузке приложения
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token); // !! преобразует строку/null в boolean
    setIsLoading(false); // Проверка завершена
  }, []);

  // Пока идет проверка токена, можно показать заглушку или лоадер
  if (isLoading) {
    return <div>Загрузка...</div>; // Или <LoadingOverlay visible />
  }

  return (
    // Оборачиваем все в QueryClientProvider
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MantineProvider theme={theme} defaultColorScheme="dark">
          <Notifications position="top-right" />
          <Routes>
            {/* Основные маршруты */}
            <Route path="/login" element={<LoginPage />} />
            <Route 
              path="/dashboard" 
              element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />}
            />
            {/* Добавляем маршрут для пользователей */}
            <Route 
              path="/users" 
              element={isAuthenticated ? <UsersPage /> : <Navigate to="/login" replace />}
            />
            {/* Добавляем маршрут для организаций (теперь на верхнем уровне) */}
            <Route 
              path="/organizations" // Убираем /dashboard
              element={isAuthenticated ? <OrganizationsPage /> : <Navigate to="/login" replace />}
            />
            
            {/* Редирект с корня */}
            <Route 
              path="/" 
              element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
            />

            {/* Маршрут для несуществующих страниц (пока редирект на дашборд) */}
            <Route 
              path="*" 
              element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
            />
          </Routes>
        </MantineProvider>
      </BrowserRouter>
      {/* Добавляем DevTools */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
