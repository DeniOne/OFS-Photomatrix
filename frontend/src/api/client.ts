import axios from 'axios';

// Определяем базовый URL для API
// Vite использует import.meta.env для переменных окружения
// Переменные должны начинаться с VITE_
// Значение по умолчанию - http://localhost:8000/api/v1
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

console.log(`API Base URL: ${API_BASE_URL}`); // Добавим лог для проверки

// Создаем экземпляр axios с базовой конфигурацией
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Здесь можно будет добавить заголовок авторизации (Bearer token),
    // когда сделаем получение токена при логине
    // 'Authorization': `Bearer ${token}`
  },
});

// Интерцептор запросов для добавления токена
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Можно добавить интерцепторы для обработки ошибок или токенов
// apiClient.interceptors.response.use(...);

// Тип для данных нового пользователя
interface NewUserPayload {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

// Функция для создания пользователя
export const createUser = async (userData: NewUserPayload): Promise<any> => {
  try {
    // Убедись, что путь /users правильный
    const response = await apiClient.post('/users/', userData);
    return response.data; // Возвращаем данные созданного пользователя
  } catch (error) {
    console.error("Ошибка при создании пользователя:", error);
    // Лучше пробросить ошибку, чтобы react-query мог ее обработать
    if (axios.isAxiosError(error)) {
      // Доступ к деталям ошибки axios
      throw new Error(error.response?.data?.detail || error.message);
    } else {
      throw error; // Пробрасываем неизвестную ошибку
    }
  }
};

// Тип для данных логина
interface LoginPayload {
  username: string; // FastAPI Users обычно использует 'username', даже если это email
  password: string;
}

// Тип ответа при успешном логине (с токеном)
interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Функция для входа пользователя
export const loginUser = async (credentials: LoginPayload): Promise<LoginResponse> => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    // Отправляем POST-запрос на правильный эндпоинт
    const response = await apiClient.post<LoginResponse>(
      '/auth/login',
      formData, 
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Ошибка при входе в систему:", error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Неверный email или пароль');
    } else {
      throw error;
    }
  }
};

export default apiClient; 