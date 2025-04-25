import { useState, useEffect, Suspense, lazy } from 'react';
import { MantineProvider, LoadingOverlay } from '@mantine/core';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import '@mantine/core/styles.css';
import { Notifications } from '@mantine/notifications';
import './App.css';
import theme from './styles/theme'; // Возвращаем импорт темы
import { DashboardLayout } from './layouts/DashboardLayout';
import AutoLoginButton from './components/AutoLoginButton';
import { isAuthenticated as checkAuthState } from './api/auth';

// --- Ленивая загрузка страниц ---
// Используем динамический импорт с приоритетами
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })));
// Для менее важных страниц не используем предзагрузку
const UsersPage = lazy(() => import('./pages/UsersPage'));
const OrganizationsPage = lazy(() => import('./pages/OrganizationsPage'));
const DivisionsPage = lazy(() => import('./pages/DivisionsPage'));
const DepartmentsPage = lazy(() => import('./pages/DepartmentsPage'));
const FunctionsPage = lazy(() => import('./features/functions/pages/FunctionsPage.tsx'));
const PositionsPage = lazy(() => import('./features/positions/pages/PositionsPage'));
const StaffPage = lazy(() => import('./features/staff/pages/StaffPage'));
const StaffDetailPage = lazy(() => import('./features/staff/pages/StaffDetailPage'));
const TestPage = lazy(() => import('./pages/TestPage'));
// Убираем тестовую страницу
// const TestModalPage = lazy(() => import('./pages/TestModalPage')); 
// --------------------------------

// Создаем клиент React Query с оптимизированными настройками
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // Не обновлять при фокусе окна
      staleTime: 1000 * 60 * 5, // Данные устаревают через 5 минут
      gcTime: 1000 * 60 * 30, // Время сборки мусора (раньше было cacheTime)
      retry: 1, // Только одна повторная попытка при ошибке
    },
  },
});

// Компонент для оборачивания страниц в лейаут
const WrappedRoute = ({ element }: { element: React.ReactNode }) => {
  return <DashboardLayout>{element}</DashboardLayout>;
};

function App() {
  // Состояние для статуса аутентификации
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true); // Состояние для начальной проверки

  useEffect(() => {
    // Проверяем наличие токена при загрузке приложения
    const token = localStorage.getItem('access_token');
    console.log("App: Проверка токена при загрузке:", !!token);
    setIsAuthenticated(!!token); // !! преобразует строку/null в boolean
    setIsLoading(false); // Проверка завершена
  }, []);

  // Добавляем слушатель событий для обновления состояния авторизации
  useEffect(() => {
    const handleStorageChange = () => {
      const isAuth = checkAuthState();
      console.log("App: Обновлено состояние авторизации:", isAuth);
      setIsAuthenticated(isAuth);
    };

    // Добавляем слушатель события storage
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Предзагружаем компоненты на основе аутентификации
  useEffect(() => {
    if (isAuthenticated) {
      // Если пользователь аутентифицирован, предзагружаем нужные компоненты
      const preloadComponents = async () => {
        // Здесь мы загружаем компоненты параллельно для экономии времени
        const imports = [
          import('./pages/DashboardPage'),
          import('./layouts/DashboardLayout')
        ];
        await Promise.all(imports);
      };
      
      preloadComponents().catch(console.error);
    } else {
      // Если пользователь не аутентифицирован, только LoginPage
      import('./pages/LoginPage');
    }
  }, [isAuthenticated]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MantineProvider theme={theme} defaultColorScheme="dark">
          <Notifications position="top-right" />
          {/* Кнопка автологина - видна на всех страницах */}
          <AutoLoginButton 
            position="fixed" 
            bottom={20} 
            right={20} 
            size="sm"
          />
          {/* Показываем начальный лоадер */}
          {isLoading ? (
            <LoadingOverlay visible={true} overlayProps={{ radius: "sm", blur: 2 }} />
          ) : (
            /* Оборачиваем Routes в Suspense */
            <Suspense
              fallback={<LoadingOverlay visible={true} overlayProps={{ radius: "sm", blur: 2 }} />}
            >
              <Routes>
                {/* Маршрут для логина (без лейаута) */}
                <Route path="/login" element={<LoginPage />} />
                
                {/* Маршруты с боковой панелью */}
                <Route 
                  path="/dashboard" 
                  element={isAuthenticated ? 
                    <WrappedRoute element={<DashboardPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/users" 
                  element={isAuthenticated ? 
                    <WrappedRoute element={<UsersPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/organizations"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<OrganizationsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/divisions"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<DivisionsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/divisions/organization/:organizationId"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<DivisionsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/departments"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<DepartmentsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/departments/organization/:organizationId"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<DepartmentsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/functions"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<FunctionsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/positions"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<PositionsPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/staff"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<StaffPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                <Route 
                  path="/staff/:id"
                  element={isAuthenticated ? 
                    <WrappedRoute element={<StaffDetailPage />} /> : 
                    <Navigate to="/login" replace />
                  }
                />
                
                {/* Тестовая страница для отладки API (без лейаута) */}
                <Route 
                  path="/test" 
                  element={<TestPage />}
                />
                
                {/* Редирект с корня */}
                <Route 
                  path="/" 
                  element={isAuthenticated ? 
                    <Navigate to="/dashboard" replace /> : 
                    <Navigate to="/login" replace />
                  }
                />

                {/* Маршрут для несуществующих страниц */}
                <Route 
                  path="*" 
                  element={isAuthenticated ? 
                    <Navigate to="/dashboard" replace /> : 
                    <Navigate to="/login" replace />
                  }
                />
              </Routes>
            </Suspense>
          )}
        </MantineProvider>
      </BrowserRouter>
      {/* Отключаем в продакшене девтулы */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export default App;
