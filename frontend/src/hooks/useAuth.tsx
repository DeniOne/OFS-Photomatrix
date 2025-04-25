import { useState, useEffect } from 'react';
import { logoutUser } from '../api/auth';

interface AuthHook {
  isAuthenticated: boolean;
  logout: () => void;
}

/**
 * Хук для проверки аутентификации пользователя
 * Предоставляет статус аутентификации и функцию выхода
 */
export const useAuth = (): AuthHook => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Проверяем токен при загрузке и при каждом действии с localStorage
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      setIsAuthenticated(!!token);
    };

    // Проверяем при первой загрузке
    checkAuth();

    // Создаем слушателя для изменений в localStorage (например, другая вкладка)
    const handleStorageChange = () => {
      checkAuth();
    };

    // Добавляем слушатель события изменения localStorage
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-changed', handleStorageChange);

    // Очистка слушателя при размонтировании
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-changed', handleStorageChange);
    };
  }, []);

  // Функция выхода из системы
  const logout = () => {
    logoutUser();
    setIsAuthenticated(false);
  };

  return {
    isAuthenticated,
    logout,
  };
};

export default useAuth; 