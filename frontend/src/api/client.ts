import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getToken } from './auth';
import { notifications } from '@mantine/notifications';

// Настройки API клиента
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 10000; // 10 секунд для таймаута

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
      config.headers.Authorization = `Bearer ${token}`;
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
    return response;
  },
  (error: AxiosError) => {
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
      // При необходимости можно добавить перенаправление на страницу входа
      break;
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