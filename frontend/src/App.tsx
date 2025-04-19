import React from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import '@mantine/core/styles.css';
import { Notifications } from '@mantine/notifications';
import './App.css';
import theme from './styles/theme'; // Подключаем нашу тему

// Импортируем реальные страницы и лейаут
import LoginPage from './pages/LoginPage'; 
import { DashboardPage } from './pages/DashboardPage'; // Используем именованный импорт
// DashboardLayout будет использоваться внутри DashboardPage, отдельно импортировать не нужно

function App() {
  // Пока хардкодим авторизацию для теста
  const isAuthenticated = true;

  return (
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
          
          {/* Редирект с корня */}
          <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />}
          />

          {/* Маршрут для несуществующих страниц (пока редирект на дашборд) */}
          <Route 
            path="*" 
            element={<Navigate to="/dashboard" replace />}
          />
        </Routes>
      </MantineProvider>
    </BrowserRouter>
  );
}

export default App;
