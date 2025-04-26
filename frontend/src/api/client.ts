import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getToken, removeToken } from './auth';
import { notifications } from '@mantine/notifications';

// Настройки API клиента
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 15000; // Увеличиваем таймаут до 15 секунд

console.log("API клиент настроен на URL:", API_URL);

// Создание экземпляра Axios с базовыми настройками
export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерсептор для добавления токена в заголовок запросов
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      console.log(`API запрос [${config.method?.toUpperCase()}] ${config.url} с токеном`);
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log(`API запрос [${config.method?.toUpperCase()}] ${config.url} без токена`);
    }
    return config;
  },
  (error) => {
    console.error('Ошибка запроса:', error);
    return Promise.reject(error);
  }
);

// Интерсептор для обработки ответов и ошибок
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API ответ [${response.status}] ${response.config.url}`, response.data);
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      console.error(`API ошибка [${error.response.status}] ${error.config?.url}:`, error.response.data);
      
      // Если ошибка 401 и это не запрос аутентификации - токен устарел или недействителен
      if (error.response.status === 401 && !error.config?.url?.includes('/auth/login')) {
        console.warn('Токен недействителен. Очищаем данные авторизации.');
        removeToken();
        
        // Перенаправляем на страницу логина, если это не страница логина и не запрос авторизации
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    } else {
      console.error('API ошибка без ответа сервера:', error.message, error);
    }
    
    handleApiError(error);
    return Promise.reject(error);
  }
);

// Функция для обработки ошибок API
const handleApiError = (error: AxiosError) => {
  if (error.code === 'ECONNABORTED') {
    notifications.show({
      title: 'Ошибка',
      message: 'Превышено время ожидания запроса. Попробуйте еще раз.',
      color: 'red',
    });
    return;
  }

  if (!error.response) {
    notifications.show({
      title: 'Ошибка соединения',
      message: 'Не удалось подключиться к серверу. Проверьте подключение к интернету.',
      color: 'red',
    });
    return;
  }

  const status = error.response.status;
  let message = 'Произошла неизвестная ошибка';

  switch (status) {
    case 401:
      message = 'Необходима авторизация. Пожалуйста, войдите в систему.';
      // НЕ показываем уведомление для 401, т.к. мы уже обрабатываем это в интерсепторе
      return;
    case 403:
      message = 'Доступ запрещен. У вас нет прав для выполнения этого действия.';
      break;
    case 404:
      message = 'Запрашиваемый ресурс не найден.';
      break;
    case 422:
      const validationErrors = (error.response.data as any)?.detail;
      if (validationErrors) {
        if (Array.isArray(validationErrors)) {
          message = validationErrors.map((err: any) => err.msg).join('\n');
        } else {
          message = String(validationErrors);
        }
      } else {
        message = 'Ошибка валидации данных.';
      }
      break;
    case 500:
      message = 'Внутренняя ошибка сервера. Попробуйте позже.';
      break;
    default:
      if ((error.response.data as any)?.detail) {
        message = (error.response.data as any).detail;
      }
  }

  notifications.show({
    title: `Ошибка ${status}`,
    message: message,
    color: 'red',
  });
};

// Вспомогательные функции для работы с API

/**
 * Создает GET запрос с обработкой ошибок
 */
export const apiGet = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.get<T>(url, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Создает POST запрос с обработкой ошибок
 */
export const apiPost = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.post<T>(url, data, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Создает PUT запрос с обработкой ошибок
 */
export const apiPut = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.put<T>(url, data, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Создает DELETE запрос с обработкой ошибок
 */
export const apiDelete = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.delete<T>(url, config);
    return response.data;
  } catch (error) {
    throw error;
  }
}; 