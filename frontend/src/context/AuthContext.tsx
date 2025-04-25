import React, { createContext, useContext, useState, useEffect } from 'react';
import { getToken, removeToken, isAuthenticated } from '../api/auth';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  isAuthenticated: boolean;
  logout: () => void;
  checkAuthStatus: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuth, setIsAuth] = useState<boolean>(false);
  const navigate = useNavigate();

  const checkAuthStatus = () => {
    const authenticated = isAuthenticated();
    console.log('Проверка статуса аутентификации:', authenticated);
    setIsAuth(authenticated);
    return authenticated;
  };

  const logout = () => {
    console.log('Выполняется выход из системы...');
    removeToken();
    setIsAuth(false);
    navigate('/login');
  };

  useEffect(() => {
    checkAuthStatus();
    
    // Обработчик события для localStorage
    const handleStorageChange = () => {
      checkAuthStatus();
    };

    // Обработчик события для кастомного события аутентификации
    const handleAuthEvent = () => {
      checkAuthStatus();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-changed', handleAuthEvent);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-changed', handleAuthEvent);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated: isAuth, logout, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 