/**
 * Модуль для работы с токенами авторизации
 */

import axios from 'axios';
import { api } from './client';

// Ключ для хранения токена в localStorage
const TOKEN_KEY = 'auth_token';
let tokenCache: string | null = null;

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Получить токен из localStorage или кэша
 * @returns {string|null} Токен или null, если токен не найден
 */
export const getToken = (): string | null => {
  if (tokenCache) return tokenCache;
  
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    tokenCache = token;
  }
  return token;
};

/**
 * Сохранить токен в localStorage и кэше
 * @param {string} token - JWT токен для сохранения
 */
export const saveToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
  tokenCache = token;
};

/**
 * Удалить токен из localStorage и кэша
 */
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  tokenCache = null;
};

/**
 * Проверить, авторизован ли пользователь
 * @returns {boolean} true, если токен существует
 */
export const isAuthenticated = (): boolean => {
  return !!getToken();
};

/**
 * Выполняет аутентификацию пользователя
 */
export const loginUser = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<LoginResponse>(
      '/api/v1/auth/login',
      formData,
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      }
    );
    
    saveToken(response.data.access_token);
    return response.data;
  } catch (error) {
    console.error("Ошибка при входе в систему:", error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Неверный email или пароль');
    } else {
      throw new Error('Произошла ошибка при попытке входа');
    }
  }
};

/**
 * Выход из системы
 */
export const logoutUser = (): void => {
  removeToken();
}; 