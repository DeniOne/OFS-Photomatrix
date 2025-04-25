import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../api/client';
import { Staff, StaffCreate, StaffUpdate } from '../../../types/staff';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX } from '@tabler/icons-react';
import { Position } from '../../../types/position';
import { Organization } from '../../../types/organization';

const API_URL_STAFF = '/api/v1/staff/';
const API_URL_POSITIONS = '/api/v1/positions/';
const API_URL_ORGANIZATIONS = '/api/v1/organizations/';

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

// Загрузка фотографии сотрудника
const uploadStaffPhoto = async ({ staffId, photo }: { staffId: number; photo: File }): Promise<Staff> => {
  const formData = new FormData();
  formData.append('photo', photo);
  
  const response = await api.post<Staff>(
    `${API_URL_STAFF}${staffId}/photo`, 
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

// Загрузка документа сотрудника
const uploadStaffDocument = async ({ 
  staffId, 
  document, 
  docType 
}: { 
  staffId: number; 
  document: File; 
  docType: string 
}): Promise<Staff> => {
  const formData = new FormData();
  formData.append('document', document);
  formData.append('doc_type', docType);
  
  const response = await api.post<Staff>(
    `${API_URL_STAFF}${staffId}/document`, 
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

// Удаление документа сотрудника
const deleteStaffDocument = async ({ staffId, docType }: { staffId: number; docType: string }): Promise<Staff> => {
  const response = await api.delete<Staff>(`${API_URL_STAFF}${staffId}/document/${docType}`);
  return response.data;
};

// Получение списка должностей
const fetchPositions = async (): Promise<Position[]> => {
  const response = await api.get<Position[]>(API_URL_POSITIONS);
  return response.data;
};

// Получение списка организаций
const fetchOrganizations = async (): Promise<Organization[]> => {
  const response = await api.get<Organization[]>(API_URL_ORGANIZATIONS);
  return response.data;
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

// Хук для загрузки фотографии сотрудника
export const useUploadStaffPhoto = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Staff, Error, { staffId: number; photo: File }>({
    mutationFn: uploadStaffPhoto,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      queryClient.invalidateQueries({ queryKey: ['staff', data.id] });

      // Добавляем небольшую задержку и обновляем страницу
      setTimeout(() => {
        window.location.reload();
      }, 500);

      notifications.show({
        title: 'Успешно',
        message: 'Фотография сотрудника успешно загружена',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось загрузить фотографию: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для загрузки документа сотрудника
export const useUploadStaffDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Staff, Error, { staffId: number; document: File; docType: string }>({
    mutationFn: uploadStaffDocument,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      queryClient.invalidateQueries({ queryKey: ['staff', data.id] });
      notifications.show({
        title: 'Успешно',
        message: 'Документ сотрудника успешно загружен',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось загрузить документ: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для удаления документа сотрудника
export const useDeleteStaffDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Staff, Error, { staffId: number; docType: string }>({
    mutationFn: deleteStaffDocument,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      queryClient.invalidateQueries({ queryKey: ['staff', data.id] });
      notifications.show({
        title: 'Успешно',
        message: 'Документ сотрудника успешно удален',
        color: 'green',
        icon: <IconCheck />,
      });
    },
    onError: (error) => {
      notifications.show({
        title: 'Ошибка',
        message: `Не удалось удалить документ: ${error.message}`,
        color: 'red',
        icon: <IconX />,
      });
    },
  });
};

// Хук для получения списка должностей
export const usePositionsList = () => {
  return useQuery<Position[], Error>({
    queryKey: ['positions', 'list'],
    queryFn: () => fetchPositions(),
  });
};

// Хук для получения списка организаций
export const useOrganizationsList = () => {
  return useQuery<Organization[], Error>({
    queryKey: ['organizations', 'list'],
    queryFn: () => fetchOrganizations(),
  });
}; 