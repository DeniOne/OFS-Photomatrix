import React, { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Box, Text, ActionIcon, Avatar, useMantineTheme } from '@mantine/core';
import {
  IconLayoutDashboard,
  IconPackage,
  IconUsers,
  IconFileAnalytics,
  IconSettings,
  IconLogout,
  IconMenu2,
  IconBell,
  IconAdjustments
} from '@tabler/icons-react';

// Тип для ссылок навигации
type NavLinkProps = {
  to: string;
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  isSidebarOpen: boolean; // Добавлено для скрытия текста
};

// Компонент ссылки навигации
const NavLink = ({ to, label, icon, active, isSidebarOpen }: NavLinkProps) => {
  const theme = useMantineTheme();
  return (
    <Link to={to} style={{ textDecoration: 'none', color: 'inherit' }}>
      <Box
        style={{
          display: 'flex',
          alignItems: 'center',
          padding: '10px 15px',
          borderRadius: theme.radius.sm,
          backgroundColor: active ? theme.colors.primary[8] : 'transparent',
          color: active ? theme.white : theme.colors.dark[1],
          transition: 'background-color 0.2s ease, color 0.2s ease',
          marginBottom: '8px',
          cursor: 'pointer',
          gap: '12px',
          overflow: 'hidden',
          whiteSpace: 'nowrap',
          '&:hover': {
            backgroundColor: active ? theme.colors.primary[8] : theme.colors.dark[6],
            color: theme.white,
          }
        }}
      >
        {icon}
        {isSidebarOpen && <Text size="sm">{label}</Text>}
      </Box>
    </Link>
  );
};

// Тип для пропсов лейаута
type DashboardLayoutProps = {
  children: ReactNode;
};

// Основной компонент лейаута
const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
  const location = useLocation();
  const theme = useMantineTheme();
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  
  // Получаем заголовок страницы на основе пути
  const getPageTitle = () => {
    // ... (логика как раньше)
    switch (location.pathname) {
      case '/dashboard': return 'Обзор системы';
      case '/products': return 'Управление продуктами';
      case '/users': return 'Пользователи';
      case '/reports': return 'Отчеты и аналитика';
      case '/settings': return 'Настройки';
      default: return 'Photomatrix ERP';
    }
  };

  const sidebarWidth = isSidebarOpen ? '250px' : '70px';
  
  return (
    <Box
      style={{
        display: 'flex',
        minHeight: '100vh',
        // Используем основной фон из темы
        backgroundColor: theme.colors.dark[7],
      }}
    >
      {/* Боковое меню */}
      <Box
        component="aside"
        style={{
          width: sidebarWidth,
          backgroundColor: theme.colors.dark[8], // Фон сайдбара чуть светлее
          borderRight: `1px solid ${theme.colors.dark[6]}`,
          padding: '15px',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width 0.3s ease',
          boxShadow: '2px 0 5px rgba(0, 0, 0, 0.2)',
          overflow: 'hidden'
        }}
      >
        {/* Логотип и кнопка сворачивания */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: isSidebarOpen ? 'space-between' : 'center',
            marginBottom: '30px',
            padding: '5px 0',
          }}
        >
          {isSidebarOpen && (
            <Text size="xl" fw={700} c="white">
              Photomatrix
            </Text>
          )}
          <ActionIcon
            onClick={toggleSidebar}
            variant="subtle" // Используем subtle для лучшей интеграции
            color="gray"
            size="lg"
          >
            <IconMenu2 />
          </ActionIcon>
        </Box>
        
        {/* Навигация */}
        <Box component="nav" style={{ flex: 1 }}>
          <NavLink
            to="/dashboard"
            label="Обзор"
            icon={<IconLayoutDashboard size={20} />}
            active={location.pathname === '/dashboard'}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/products"
            label="Продукты"
            icon={<IconPackage size={20} />}
            active={location.pathname.startsWith('/products')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/users"
            label="Пользователи"
            icon={<IconUsers size={20} />}
            active={location.pathname.startsWith('/users')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/reports"
            label="Отчеты"
            icon={<IconFileAnalytics size={20} />}
            active={location.pathname.startsWith('/reports')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/settings"
            label="Настройки"
            icon={<IconSettings size={20} />}
            active={location.pathname.startsWith('/settings')}
            isSidebarOpen={isSidebarOpen}
          />
        </Box>
        
        {/* Профиль пользователя */}
        <Box
          style={{
            marginTop: 'auto',
            paddingTop: '15px',
            borderTop: `1px solid ${theme.colors.dark[6]}`,
          }}
        >
           <Box
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '10px',
              borderRadius: theme.radius.sm,
              backgroundColor: theme.colors.dark[7],
              gap: '10px'
            }}
          >
            <Avatar radius="xl" size="md" src="https://i.pravatar.cc/150?img=13" />
            {isSidebarOpen && (
              <Box style={{ flex: 1, overflow: 'hidden' }}>
                <Text size="sm" c="white" truncate>Иван Петров</Text>
                <Text size="xs" c="dimmed" truncate>Администратор</Text>
              </Box>
            )}
             {/* Иконка выхода видна всегда, если сайдбар открыт */}
            {isSidebarOpen && (
              <ActionIcon variant="subtle" color="gray">
                <IconLogout size={18} />
              </ActionIcon>
            )}
          </Box>
        </Box>
      </Box>
      
      {/* Основной контент */}
      <Box component="main" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Верхняя панель */}
        <Box
          component="header"
          style={{
            height: '60px', // Чуть ниже
            borderBottom: `1px solid ${theme.colors.dark[6]}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 25px',
            backgroundColor: theme.colors.dark[8], // Как у сайдбара
            boxShadow: '0 2px 5px rgba(0, 0, 0, 0.15)'
          }}
        >
          <Text size="lg" fw={600} c="white">
            {getPageTitle()}
          </Text>
          <Box style={{ display: 'flex', gap: '15px' }}>
            <ActionIcon variant="subtle" color="gray" size="lg">
              <IconBell size={20} />
            </ActionIcon>
            <ActionIcon variant="subtle" color="gray" size="lg">
              <IconAdjustments size={20} />
            </ActionIcon>
          </Box>
        </Box>
        
        {/* Область для контента страницы */}
        <Box style={{ flex: 1, overflowY: 'auto', padding: '25px' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export { DashboardLayout }; // Именованный экспорт 