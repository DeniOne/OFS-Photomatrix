/**
 * Модуль для работы с токенами авторизации
 */

import axios from 'axios';
import { api } from './client';

// Константа с базовым URL для API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Ключ для хранения токена в localStorage
const TOKEN_KEY = 'access_token';
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
  if (tokenCache) {
    console.log("getToken: Возвращаем токен из кэша");
    return tokenCache;
  }
  
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    console.log("getToken: Токен найден в localStorage, обновляем кэш");
    tokenCache = token;
  } else {
    console.log("getToken: Токен не найден ни в кэше, ни в localStorage");
  }
  return token;
};

/**
 * Сохранить токен в localStorage и кэше
 * @param {string} token - JWT токен для сохранения
 */
export const saveToken = (token: string): void => {
  console.log("saveToken: Сохраняем токен в localStorage и кэш");
  localStorage.setItem(TOKEN_KEY, token);
  tokenCache = token;
  
  // Диспатчим событие для обновления состояния авторизации во всех компонентах
  window.dispatchEvent(new Event('storage'));
  
  // Диспатчим также событие auth-changed для компонентов, которые его слушают
  window.dispatchEvent(new Event('auth-changed'));
};

/**
 * Удалить токен из localStorage и кэша
 */
export const removeToken = (): void => {
  console.log("removeToken: Удаляем токен из localStorage и кэша");
  localStorage.removeItem(TOKEN_KEY);
  tokenCache = null;
  
  // Создаем и диспатчим событие деавторизации
  window.dispatchEvent(new Event('auth-changed'));
  // Диспатчим также событие storage
  window.dispatchEvent(new Event('storage'));
};

/**
 * Проверить, авторизован ли пользователь
 * @returns {boolean} true, если токен существует
 */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  const result = !!token;
  console.log("isAuthenticated: Проверка авторизации:", result);
  return result;
};

/**
 * Выполняет аутентификацию пользователя
 */
export const loginUser = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  // Используем правильный URL с префиксом /api/v1
  const loginUrl = `${API_URL}/api/v1/auth/login`;
  console.log("loginUser: Отправляем запрос на авторизацию", { username: credentials.username, url: loginUrl });
  
  try {
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("loginUser: Ошибка авторизации", errorData);
      throw new Error(errorData.detail || 'Ошибка авторизации');
    }

    const data = await response.json();
    console.log("loginUser: Успешная авторизация", data);
    // Используем функцию saveToken для установки токена
    saveToken(data.access_token);
    return data;
  } catch (error) {
    console.error("loginUser: Ошибка при авторизации", error);
    throw error;
  }
};

/**
 * Автоматический вход в систему с предустановленными учетными данными администратора
 * @returns {Promise<LoginResponse>} Результат авторизации
 */
export const autoLogin = async (): Promise<LoginResponse> => {
  console.log("autoLogin: Запускаем автоматический вход...");
  
  // Используем фиксированные учетные данные администратора
  const credentials: LoginCredentials = {
    username: 'admin@example.com',
    password: 'admin'
  };
  
  try {
    const result = await loginUser(credentials);
    
    console.log("autoLogin: Вход выполнен успешно");
    return result;
  } catch (error) {
    console.error("autoLogin: Ошибка при автоматическом входе:", error);
    throw error;
  }
};

/**
 * Выход из системы
 */
export const logoutUser = (): void => {
  console.log("logoutUser: Выполняем выход из системы");
  removeToken();
};

// Устаревшая функция, сохраняем для обратной совместимости
export const setToken = (token: string): void => {
  console.log("setToken (устаревшая): Делегируем вызов к saveToken");
  saveToken(token);
}; 