import React, { ReactNode, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Text, 
  ActionIcon, 
  Avatar, 
  useMantineTheme, 
  AppShell, 
  Group,
  Button,
} from '@mantine/core';
import {
  IconLayoutDashboard,
  IconPackage,
  IconUsers,
  IconFileAnalytics,
  IconSettings,
  IconLogout,
  IconMenu2,
  IconBuildingSkyscraper,
  IconBuildingCommunity,
  IconBuildingPavilion,
  IconFunction,
  IconUserShield,
  IconSearch,
  IconUserCheck,
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useAuth } from '../hooks/useAuth';
import { logoutUser } from '../api/auth';

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
export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const theme = useMantineTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { isAuthenticated } = useAuth();
  const [opened, setOpened] = useState(false);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  
  // Обработчик выхода из системы
  const handleLogout = () => {
    logoutUser();
    notifications.show({
      title: 'Выход из системы',
      message: 'Вы успешно вышли из системы',
      color: 'blue',
    });
    navigate('/login');
  };
  
  // Получаем заголовок страницы на основе пути
  const getPageTitle = () => {
    // ... (логика как раньше)
    switch (location.pathname) {
      case '/dashboard': return 'Обзор системы';
      case '/products': return 'Управление продуктами';
      case '/organizations': return 'Управление организациями';
      case '/departments': return 'Управление департаментами';
      case '/divisions': return 'Управление отделами';
      case '/functions': return 'Управление функциями';
      case '/positions': return 'Управление должностями';
      case '/staff': return 'Управление сотрудниками';
      case '/users': return 'Пользователи';
      case '/reports': return 'Отчеты и аналитика';
      case '/settings': return 'Настройки';
      default: return 'Photomatrix ERP';
    }
  };

  return (
    <AppShell
      padding="md"
      navbar={{
        width: isSidebarOpen ? 250 : 70,
        breakpoint: 'sm',
      }}
      header={{ height: 60 }}
    >
      <AppShell.Header>
        <Group p="md" justify="space-between" style={{ height: '100%' }}>
          <Text fw={700} size="lg">{getPageTitle()}</Text>
          <Group>
            <ActionIcon variant="default" onClick={() => console.log('Действие')} size={30}>
              <IconSettings size={20} stroke={1.5} />
            </ActionIcon>
            <ActionIcon variant="default" onClick={() => console.log('Действие')} size={30}>
              <IconSearch size={20} stroke={1.5} />
            </ActionIcon>
          </Group>
        </Group>
      </AppShell.Header>
      
      <AppShell.Navbar p="md">
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
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            variant="subtle"
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
            to="/organizations"
            label="Организации"
            icon={<IconBuildingSkyscraper size={20} />}
            active={location.pathname.startsWith('/organizations')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/departments"
            label="Департаменты"
            icon={<IconBuildingCommunity size={20} />}
            active={location.pathname.startsWith('/departments')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/divisions"
            label="Отделы"
            icon={<IconBuildingPavilion size={20} />}
            active={location.pathname.startsWith('/divisions')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/functions"
            label="Функции"
            icon={<IconFunction size={20} />}
            active={location.pathname.startsWith('/functions')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/positions"
            label="Должности"
            icon={<IconUserShield size={20} />}
            active={location.pathname.startsWith('/positions')}
            isSidebarOpen={isSidebarOpen}
          />
          <NavLink
            to="/staff"
            label="Сотрудники"
            icon={<IconUserCheck size={20} />}
            active={location.pathname.startsWith('/staff')}
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
            <ActionIcon variant="subtle" color="gray" onClick={handleLogout}>
              <IconLogout size={18} />
            </ActionIcon>
          </Box>
        </Box>
      </AppShell.Navbar>
      
      <AppShell.Main>
        {children}
      </AppShell.Main>
    </AppShell>
  );
};

export default DashboardLayout; 