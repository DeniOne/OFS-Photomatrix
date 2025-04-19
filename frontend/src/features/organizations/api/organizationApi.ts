import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../api/client.ts'; // Пробуем три уровня вверх + расширение
import { Organization, OrganizationCreateDto, OrganizationUpdateDto } from '../types/organizationTypes';
import { notifications } from '@mantine/notifications';

const ORGANIZATIONS_QUERY_KEY = ['organizations'];

// --- API Функции ---

// Получение списка организаций
const fetchOrganizations = async (): Promise<Organization[]> => {
  const response = await apiClient.get<Organization[]>('/organizations');
  return response.data;
};

// Создание организации
const createOrganization = async (organizationData: OrganizationCreateDto): Promise<Organization> => {
  // API для организаций не возвращает activation_code, ожидаем просто Organization
  const response = await apiClient.post<Organization>('/organizations', organizationData);
  return response.data;
};

// Обновление организации (пока не используется, но добавим для полноты)
const updateOrganization = async ({ id, data }: { id: number; data: OrganizationUpdateDto }): Promise<Organization> => {
  const response = await apiClient.put<Organization>(`/organizations/${id}`, data);
  return response.data;
};

// Удаление организации (пока не используется)
const deleteOrganization = async (id: number): Promise<void> => {
  await apiClient.delete(`/organizations/${id}`);
};

// --- React Query Хуки ---

// Хук для получения списка организаций
export const useOrganizations = () => {
  return useQuery<Organization[], Error>({
    queryKey: ORGANIZATIONS_QUERY_KEY,
    queryFn: fetchOrganizations,
    // опционально: staleTime, cacheTime и т.д.
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

// Хук для мутации обновления организации (пока не используется)
export const useUpdateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<Organization, Error, { id: number; data: OrganizationUpdateDto }>({
    mutationFn: updateOrganization,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      // Можно обновлять конкретный элемент в кэше для оптимизации
      // queryClient.setQueryData(ORGANIZATIONS_QUERY_KEY, (oldData) => ...);
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

// Хук для мутации удаления организации (пока не используется)
export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: deleteOrganization,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ORGANIZATIONS_QUERY_KEY });
      // Можно удалить элемент из кэша
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