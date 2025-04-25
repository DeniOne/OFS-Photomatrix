import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../api/client';
import { Staff, StaffCreate, StaffUpdate } from '../../../types/staff';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';

const API_URL_STAFF = '/api/v1/staff/';

// --- Функции для вызова API ---

// Получение списка сотрудников
const fetchStaffList = async (params?: { skip?: number; limit?: number }): Promise<Staff[]> => {
  let url = API_URL_STAFF;
  const queryParams = new URLSearchParams();
  
  if (params?.skip !== undefined) {
    queryParams.append('skip', params.skip.toString());
  }
  
  if (params?.limit !== undefined) {
    queryParams.append('limit', params.limit.toString());
  }
  
  const queryString = queryParams.toString();
  if (queryString) {
    url += `?${queryString}`;
  }
  
  console.log(`Запрос сотрудников: ${url}`);
  const response = await api.get<Staff[]>(url);
  return response.data;
};

// Получение одного сотрудника по ID
const fetchStaff = async (id: number): Promise<Staff> => {
  const response = await api.get<Staff>(`${API_URL_STAFF}${id}`);
  return response.data;
};

// Создание нового сотрудника
const createStaff = async (data: StaffCreate): Promise<Staff> => {
  const response = await api.post<Staff>(API_URL_STAFF, data);
  return response.data;
};

// Обновление сотрудника
const updateStaff = async ({ id, data }: { id: number; data: StaffUpdate }): Promise<Staff> => {
  const response = await api.put<Staff>(`${API_URL_STAFF}${id}`, data);
  return response.data;
};

// Удаление сотрудника
const deleteStaff = async (id: number): Promise<void> => {
  await api.delete(`${API_URL_STAFF}${id}`);
};

// --- Хуки React Query ---

// Хук для получения списка сотрудников
export const useStaffList = (params?: { skip?: number; limit?: number }) => {
  return useQuery<Staff[], Error>({
    queryKey: ['staff', 'list', params],
    queryFn: () => fetchStaffList(params),
  });
};

// Хук для получения одного сотрудника по ID
export const useStaff = (id: number) => {
  return useQuery<Staff, Error>({
    queryKey: ['staff', id],
    queryFn: () => fetchStaff(id),
    enabled: !!id,
  });
};

// Хук для создания сотрудника
export const useCreateStaff = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Staff, Error, StaffCreate>({
    mutationFn: createStaff,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      notifications.show({
        title: 'Успешно',
        message: 'Сотрудник успешно создан',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось создать сотрудника: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для обновления сотрудника
export const useUpdateStaff = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Staff, Error, { id: number; data: StaffUpdate }>({
    mutationFn: updateStaff,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      queryClient.invalidateQueries({ queryKey: ['staff', data.id] });
      notifications.show({
        title: 'Успешно',
        message: 'Данные сотрудника успешно обновлены',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось обновить данные сотрудника: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для удаления сотрудника
export const useDeleteStaff = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, number>({
    mutationFn: deleteStaff,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      notifications.show({
        title: 'Успешно',
        message: 'Сотрудник успешно удален',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось удалить сотрудника: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
}; 