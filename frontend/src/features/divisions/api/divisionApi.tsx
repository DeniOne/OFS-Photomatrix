import axios from 'axios';
import { Division, DivisionCreate, DivisionUpdate, DivisionType } from '../../../types/division';
import { useAuth } from '../../../hooks/useAuth';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';
import { api } from '../../../api/client';

// --- API Функции ---

// Обработчик ошибок API
const handleApiError = (error: any, actionName: string): never => {
  console.error(`Ошибка при ${actionName}:`, error);
  
  let errorMessage = 'Произошла неизвестная ошибка';
  
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Ошибка с ответом от сервера
      errorMessage = error.response.data?.detail || `Ошибка ${error.response.status}: ${error.message}`;
      console.error('Ответ сервера:', error.response.data);
    } else if (error.request) {
      // Ошибка без ответа от сервера (нет соединения)
      errorMessage = 'Нет соединения с сервером. Пожалуйста, проверьте подключение к интернету.';
    } else {
      // Что-то пошло не так при настройке запроса
      errorMessage = `Ошибка запроса: ${error.message}`;
    }
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }
  
  throw new Error(errorMessage);
};

// Получение списка подразделений
export const fetchDivisions = async (): Promise<Division[]> => {
  console.log('Запрос списка всех подразделений');
  try {
    const response = await api.get<Division[]>('/api/v1/divisions/');
    console.log('Получены подразделения:', response.data.length);
    return response.data;
  } catch (error) {
    return handleApiError(error, 'получении списка подразделений');
  }
};

// Получение подразделений по организации
export const fetchDivisionsByOrganization = async (organizationId: number): Promise<Division[]> => {
  console.log(`Запрос подразделений для организации ${organizationId}`);
  try {
    const response = await api.get<Division[]>(`/api/v1/divisions/by-organization/${organizationId}`);
    console.log(`Получены подразделения для организации ${organizationId}:`, response.data.length);
    return response.data;
  } catch (error) {
    return handleApiError(error, `получении подразделений для организации ${organizationId}`);
  }
};

// Получение корневых подразделений для организации
export const fetchRootDivisions = async (organizationId: number): Promise<Division[]> => {
  console.log(`Запрос корневых подразделений для организации ${organizationId}`);
  try {
    const response = await api.get<Division[]>(`/api/v1/divisions/root/${organizationId}`);
    console.log('Получены корневые подразделения:', response.data);
    return response.data;
  } catch (error) {
    return handleApiError(error, `получении корневых подразделений для организации ${organizationId}`);
  }
};

// Получение подразделения по ID
export const fetchDivision = async (id: number): Promise<Division> => {
  console.log(`Запрос подразделения с ID ${id}`);
  try {
    const response = await api.get<Division>(`/api/v1/divisions/${id}`);
    console.log(`Получено подразделение с ID ${id}:`, response.data);
    return response.data;
  } catch (error) {
    return handleApiError(error, `получении подразделения с ID ${id}`);
  }
};

// Создание подразделения
export const createDivision = async (division: DivisionCreate): Promise<Division> => {
  console.log('Создание нового подразделения:', division);
  try {
    // Проверяем обязательные поля
    if (!division.name || !division.code || !division.organization_id || !division.type) {
      console.error('Не заполнены обязательные поля:', division);
      throw new Error('Не заполнены обязательные поля (название, код, ID организации, тип)');
    }
    
    // Проверка на наличие родительского департамента для отдела
    if (division.type === DivisionType.DIVISION && !division.parent_id) {
      console.error('Для отдела нужно указать родительский департамент');
      throw new Error('Для отдела необходимо указать родительский департамент');
    }
    
    // Увеличиваем таймаут для операции создания
    const response = await api.post<Division>('/api/v1/divisions/', division, {
      timeout: 10000, // 10 секунд
    });
    
    console.log('Создано новое подразделение:', response.data);
    return response.data;
  } catch (error) {
    // Расширенная обработка ошибок
    console.error('API Error creating division:', error);
    
    if (axios.isAxiosError(error)) {
      // Если есть ответ с сервера
      if (error.response) {
        const serverError = error.response.data?.detail || 
                           JSON.stringify(error.response.data) || 
                           `Ошибка сервера: ${error.response.status}`;
        console.error('Server error details:', serverError);
        throw new Error(serverError);
      }
      
      // Ошибка запроса (нет соединения, CORS и т.д.)
      if (error.request) {
        console.error('Request error (no response):', error.request);
        throw new Error('Нет ответа от сервера. Проверьте соединение или перезапустите сервер');
      }
      
      // Ошибка таймаута
      if (error.code === 'ECONNABORTED') {
        throw new Error('Превышено время ожидания ответа от сервера');
      }
      
      // Другие ошибки axios
      throw new Error(`Ошибка запроса: ${error.message}`);
    }
    
    // Неизвестная ошибка
    throw new Error(`Неизвестная ошибка: ${error instanceof Error ? error.message : 'Ошибка создания подразделения'}`);
  }
};

// Обновление подразделения
export const updateDivision = async (division: DivisionUpdate): Promise<Division> => {
  console.log(`Обновление подразделения с ID ${division.id}:`, division);
  try {
    const response = await api.put<Division>(`/api/v1/divisions/${division.id}`, division);
    console.log(`Обновлено подразделение с ID ${division.id}:`, response.data);
    return response.data;
  } catch (error) {
    return handleApiError(error, `обновлении подразделения с ID ${division.id}`);
  }
};

// Удаление подразделения
export const deleteDivision = async (id: number): Promise<void> => {
  console.log(`Удаление подразделения с ID ${id}`);
  try {
    await api.delete(`/api/v1/divisions/${id}`);
    console.log(`Подразделение с ID ${id} успешно удалено`);
  } catch (error) {
    return handleApiError(error, `удалении подразделения с ID ${id}`);
  }
};

// --- React Query Хуки ---

// Константа для ключа запроса
const DIVISIONS_QUERY_KEY = ['divisions'];

// Хуки для использования API
export const useDivisions = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: DIVISIONS_QUERY_KEY,
    queryFn: fetchDivisions,
    enabled: isAuthenticated,
    retry: 1,
  });
};

export const useDivisionsByOrganization = (organizationId: number | null) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['divisions', 'organization', organizationId],
    queryFn: () => organizationId ? fetchDivisionsByOrganization(organizationId) : Promise.resolve([]),
    enabled: isAuthenticated && !!organizationId,
    retry: 1,
  });
};

export const useRootDivisions = (organizationId: number) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['divisions', 'root', organizationId],
    queryFn: () => fetchRootDivisions(organizationId),
    enabled: isAuthenticated && !!organizationId,
    retry: 1,
  });
};

export const useDivision = (id: number) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['divisions', id],
    queryFn: () => fetchDivision(id),
    enabled: isAuthenticated && !!id,
    retry: 1,
  });
};

export const useCreateDivision = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createDivision,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: DIVISIONS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['divisions', 'organization', data.organization_id] });
      notifications.show({
        title: 'Успех!',
        message: `${data.type === DivisionType.DEPARTMENT ? 'Департамент' : 'Отдел'} "${data.name}" успешно создан.`,
        color: 'green',
        icon: <IconCheck size="1.1rem" />
      });
    },
    onError: (error: Error) => {
      notifications.show({
        title: 'Ошибка!',
        message: error.message || 'Не удалось создать подразделение',
        color: 'red',
        icon: <IconX size="1.1rem" />
      });
    }
  });
};

export const useUpdateDivision = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: updateDivision,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: DIVISIONS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['divisions', 'organization', data.organization_id] });
      notifications.show({
        title: 'Успех!',
        message: `${data.type === DivisionType.DEPARTMENT ? 'Департамент' : 'Отдел'} "${data.name}" успешно обновлен.`,
        color: 'green',
        icon: <IconCheck size="1.1rem" />
      });
    },
    onError: (error: Error) => {
      notifications.show({
        title: 'Ошибка!',
        message: error.message || 'Не удалось обновить подразделение',
        color: 'red',
        icon: <IconX size="1.1rem" />
      });
    }
  });
};

export const useDeleteDivision = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteDivision,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DIVISIONS_QUERY_KEY });
      notifications.show({
        title: 'Успех!',
        message: 'Подразделение успешно удалено.',
        color: 'green',
        icon: <IconCheck size="1.1rem" />
      });
    },
    onError: (error: Error) => {
      notifications.show({
        title: 'Ошибка!',
        message: error.message || 'Не удалось удалить подразделение',
        color: 'red',
        icon: <IconX size="1.1rem" />
      });
    }
  });
};

// Для поддержания совместимости с кодом, добавленным в будущем
export const useGetDivisions = useDivisions;
export const useGetDivisionsByOrganization = useDivisionsByOrganization;
export const useGetDivision = useDivision;
export const useDeleteDivisionMutation = useDeleteDivision; 