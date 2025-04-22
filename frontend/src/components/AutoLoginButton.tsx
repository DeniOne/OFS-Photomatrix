import { useState } from 'react';
import { Button } from '@mantine/core';
import { IconLogin } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { autoLogin } from '../api/auth';
import { useAuth } from '../hooks/useAuth';

interface AutoLoginButtonProps {
  variant?: 'filled' | 'outline' | 'light' | 'subtle' | 'transparent';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  position?: 'fixed' | 'relative';
  bottom?: number;
  right?: number;
}

/**
 * Компонент кнопки для быстрого входа в систему с предустановленными учетными данными администратора
 */
export const AutoLoginButton = ({ 
  variant = 'outline', 
  size = 'xs',
  position = 'relative',
  bottom = 20,
  right = 20
}: AutoLoginButtonProps) => {
  const [isAutoLogging, setIsAutoLogging] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleAutoLogin = async () => {
    try {
      setIsAutoLogging(true);
      await autoLogin();
      notifications.show({
        title: 'Успешный вход',
        message: 'Вы успешно вошли в систему как администратор',
        color: 'green'
      });
      window.location.reload();
    } catch (error) {
      setIsAutoLogging(false);
      const errorMessage = error instanceof Error ? error.message : 'Ошибка при автоматическом входе';
      notifications.show({
        title: 'Ошибка входа',
        message: errorMessage,
        color: 'red'
      });
    }
  };

  if (isAuthenticated) return null;

  return (
    <Button 
      size={size} 
      variant={variant} 
      color="blue"
      leftSection={<IconLogin size={16} />}
      onClick={handleAutoLogin}
      loading={isAutoLogging}
      style={{
        position: position === 'fixed' ? 'fixed' : 'relative',
        bottom: position === 'fixed' ? bottom : undefined,
        right: position === 'fixed' ? right : undefined,
        zIndex: 1000
      }}
    >
      АвтоЛогин
    </Button>
  );
};

export default AutoLoginButton; 