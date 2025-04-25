import React, { useState, useEffect } from 'react';
import { Button, Loader } from '@mantine/core';
import { autoLogin, isAuthenticated } from '../api/auth';
import { useLocation, useNavigate } from 'react-router-dom';

interface AutoLoginButtonProps {
  position?: string;
  bottom?: number;
  right?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

const AutoLoginButton: React.FC<AutoLoginButtonProps> = ({
  position = 'fixed',
  bottom = 20,
  right = 20,
  size = 'md'
}) => {
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Функция проверки авторизации
  const checkAuth = () => {
    const authenticated = isAuthenticated();
    console.log("AutoLoginButton: Проверка авторизации:", authenticated);
    setVisible(!authenticated);
  };

  useEffect(() => {
    // Проверяем авторизацию и показываем кнопку только если пользователь не авторизован
    checkAuth();
    
    // Слушаем изменения авторизации
    const handleAuthChange = () => {
      console.log("AutoLoginButton: Обработка события изменения авторизации");
      checkAuth();
    };

    window.addEventListener('auth-changed', handleAuthChange);
    window.addEventListener('storage', handleAuthChange);
    
    return () => {
      window.removeEventListener('auth-changed', handleAuthChange);
      window.removeEventListener('storage', handleAuthChange);
    };
  }, [location.pathname]);

  const handleAutoLogin = async () => {
    try {
      setLoading(true);
      console.log("AutoLoginButton: Начинаем автологин");
      await autoLogin();
      console.log("AutoLoginButton: Автологин успешен");
      
      // Явно проверяем статус авторизации после успешного входа
      checkAuth();
      
      // Перенаправляем на главную страницу после успешного входа
      navigate('/');
    } catch (error) {
      console.error("AutoLoginButton: Ошибка автологина", error);
    } finally {
      setLoading(false);
    }
  };

  if (!visible) {
    return null;
  }

  return (
    <div style={{
      position: position as any,
      bottom: bottom,
      right: right,
      zIndex: 1000,
      backgroundColor: '#fff',
      borderRadius: '4px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
      padding: '5px'
    }}>
      <Button
        color="green"
        onClick={handleAutoLogin}
        disabled={loading}
        size={size}
      >
        {loading ? <Loader size="sm" color="white" /> : 'Автовход'}
      </Button>
    </div>
  );
};

export default AutoLoginButton; 