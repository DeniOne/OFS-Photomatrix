import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../api/client';
import { Position, PositionCreate, PositionUpdate } from '../../../types/position';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';

const API_URL_POSITIONS = '/api/v1/positions/';

// --- Функции для вызова API ---

// Получение списка должностей с опциональной фильтрацией по отделу
const fetchPositions = async (section_id?: number | null): Promise<Position[]> => {
  let url = API_URL_POSITIONS;
  if (section_id) {
    url += `?section_id=${section_id}`;
  }
  console.log(`Запрос должностей: ${url}`);
  const response = await api.get<Position[]>(url);
  return response.data;
};

// Получение одной должности по ID
const fetchPosition = async (id: number): Promise<Position> => {
  const response = await api.get<Position>(`/api/v1/positions/${id}`);
  return response.data;
};

// Создание новой должности
const createPosition = async (data: PositionCreate): Promise<Position> => {
  const response = await api.post<Position>(API_URL_POSITIONS, data);
  return response.data;
};

// Обновление должности
const updatePosition = async ({ id, data }: { id: number; data: PositionUpdate }): Promise<Position> => {
  const response = await api.put<Position>(`/api/v1/positions/${id}`, data);
  return response.data;
};

// Удаление должности
const deletePosition = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/positions/${id}`);
};

// --- Хуки React Query ---

// Хук для получения списка должностей с опциональной фильтрацией по отделу
export const usePositions = (section_id?: number | null) => {
  return useQuery<Position[], Error>({
    queryKey: ['positions', 'bySection', section_id],
    queryFn: () => fetchPositions(section_id),
    // Всегда выполняем запрос независимо от section_id
  });
};

// Хук для получения одной должности по ID
export const usePosition = (id: number) => {
  return useQuery<Position, Error>({
    queryKey: ['position', id],
    queryFn: () => fetchPosition(id),
    enabled: !!id,
  });
};

// Хук для создания должности
export const useCreatePosition = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Position, Error, PositionCreate>({
    mutationFn: createPosition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      notifications.show({
        title: 'Успешно',
        message: 'Должность успешно создана',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось создать должность: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для обновления должности
export const useUpdatePosition = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Position, Error, { id: number; data: PositionUpdate }>({
    mutationFn: updatePosition,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      queryClient.invalidateQueries({ queryKey: ['position', data.id] });
      notifications.show({
        title: 'Успешно',
        message: 'Должность успешно обновлена',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось обновить должность: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для удаления должности
export const useDeletePosition = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, number>({
    mutationFn: deletePosition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      notifications.show({
        title: 'Успешно',
        message: 'Должность успешно удалена',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось удалить должность: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
}; 