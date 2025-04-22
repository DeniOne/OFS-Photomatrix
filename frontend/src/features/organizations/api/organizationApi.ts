import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../api/client.ts'; // Используем именованный импорт
import { Organization, OrganizationCreateDto, OrganizationUpdateDto } from '@/types/organization';
import { notifications } from '@mantine/notifications';
import axios from 'axios';

const ORGANIZATIONS_QUERY_KEY = ['organizations'];

// --- API Функции ---

// Получение списка организаций
const fetchOrganizations = async (): Promise<Organization[]> => {
  console.log('Fetching organizations...');
  const response = await api.get<Organization[]>('/api/v1/organizations/');
  console.log('Organizations fetched:', response.data);
  return response.data;
};

// Создание организации
const createOrganization = async (organizationData: OrganizationCreateDto): Promise<Organization> => {
  try {
    console.log('Creating organization:', organizationData);
    
    // Проверка на наличие обязательных полей
    if (!organizationData.name || !organizationData.code || !organizationData.org_type) {
      console.error('Missing required fields for organization creation:', organizationData);
      throw new Error('Не заполнены обязательные поля (название, код, тип организации)');
    }
    
    // Проверяем, есть ли токен
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No auth token found when creating organization');
      throw new Error('Не авторизован. Авторизуйтесь перед созданием организации');
    }
    
    // Отправка запроса с обработкой таймаута
    const response = await api.post<Organization>('/api/v1/organizations/', organizationData, {
      timeout: 10000, // увеличиваем таймаут до 10 секунд
    });
    
    console.log('Organization created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error creating organization:', error);
    
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
    throw new Error(`Неизвестная ошибка: ${error instanceof Error ? error.message : 'Ошибка создания организации'}`);
  }
};

// Обновление организации
const updateOrganization = async ({ id, data }: { id: number; data: OrganizationUpdateDto }): Promise<Organization> => {
  console.log(`Updating organization ${id}:`, data);
  const response = await api.put<Organization>(`/api/v1/organizations/${id}`, data);
  console.log('Organization updated:', response.data);
  return response.data;
};

// Удаление организации
const deleteOrganization = async (id: number): Promise<void> => {
  console.log(`Deleting organization ${id}`);
  await api.delete(`/api/v1/organizations/${id}`);
  console.log(`Organization ${id} deleted`);
};

// --- React Query Хуки ---

// Хук для получения списка организаций
export const useOrganizations = () => {
  return useQuery<Organization[], Error>({
    queryKey: ORGANIZATIONS_QUERY_KEY,
    queryFn: fetchOrganizations,
    retry: 1,
  });
};

// Хук для мутации создания организации
export const useCreateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, OrganizationCreateDto>({
    mutationFn: createOrganization,
    onSuccess: (data) => {
      // При успехе инвалидируем кэш списка организаций, чтобы он обновился
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      notifications.show({
        title: 'Успех!',
        message: `Организация "${data.name}" успешно создана.`,
        color: 'green',
      });
    },
    onError: (error) => {
      console.error("Ошибка создания организации:", error);
      notifications.show({
        title: 'Ошибка!',
        message: `Не удалось создать организацию: ${error.message || 'Неизвестная ошибка'}`, 
        color: 'red',
      });
    },
  });
};

// Хук для мутации обновления организации
export const useUpdateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, { id: number; data: OrganizationUpdateDto }>({
    mutationFn: updateOrganization,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      notifications.show({
        title: 'Успех!',
        message: `Организация "${data.name}" успешно обновлена.`, 
        color: 'green',
      });
    },
    onError: (error) => {
      console.error("Ошибка обновления организации:", error);
      notifications.show({
        title: 'Ошибка!',
        message: `Не удалось обновить организацию: ${error.message || 'Неизвестная ошибка'}`, 
        color: 'red',
      });
    },
  });
};

// Хук для мутации удаления организации
export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: deleteOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      notifications.show({
        title: 'Успех!',
        message: `Организация успешно удалена.`,
        color: 'green',
      });
    },
    onError: (error) => {
      console.error("Ошибка удаления организации:", error);
      notifications.show({
        title: 'Ошибка!',
        message: `Не удалось удалить организацию: ${error.message || 'Неизвестная ошибка'}`, 
        color: 'red',
      });
    },
  });
}; 