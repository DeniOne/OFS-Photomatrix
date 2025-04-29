import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { api } from '@/api/client'; // Импортируем api вместо axiosInstance
import { User, UserCreate, UserUpdate, UsersPublic } from '@/types/user'; // Используем алиас @/types/
import { notifications } from '@mantine/notifications'; // Для уведомлений

const USERS_QUERY_KEY = 'users';
const CURRENT_USER_QUERY_KEY = 'currentUser';
const API_URL_USERS = '/api/v1/users/';

// Тип для параметров useUsers
interface UseUsersParams {
  page?: number;
  limit?: number;
  // Добавить другие параметры фильтрации/сортировки по необходимости
}

// Функция для получения пользователей
const fetchUsers = async (params: UseUsersParams): Promise<UsersPublic> => {
  const queryParams = new URLSearchParams();
  if (params.page) queryParams.append('skip', ((params.page - 1) * (params.limit ?? 10)).toString());
  if (params.limit) queryParams.append('limit', params.limit.toString());

  const { data } = await api.get<User[]>(`${API_URL_USERS}?${queryParams.toString()}`);
  
  // Преобразуем массив пользователей в объект UsersPublic
  return {
    data: data || [],
    total: data?.length || 0
  };
};

// Хук для получения списка пользователей
export const useUsers = (params: UseUsersParams = {}) => {
  return useQuery<UsersPublic, Error>({
    queryKey: [USERS_QUERY_KEY, params], // Ключ включает параметры для кеширования
    queryFn: () => fetchUsers(params),
    placeholderData: keepPreviousData, // Используем placeholderData вместо keepPreviousData
    // keepPreviousData: true, // Старый вариант
  });
};

// Функция для получения одного пользователя
const fetchUser = async (id: number): Promise<User> => {
  const { data } = await api.get(`${API_URL_USERS}${id}`);
  return data;
};

// Хук для получения одного пользователя
export const useUser = (id: number | null) => {
  return useQuery<User, Error>({
    queryKey: [USERS_QUERY_KEY, id],
    queryFn: () => fetchUser(id!),
    enabled: !!id, // Запрос выполняется только если id не null
  });
};

// Функция для создания пользователя
const createUser = async (userData: UserCreate): Promise<User> => {
  const { data } = await api.post(API_URL_USERS, userData);
  return data;
};

// Хук для создания пользователя
export const useCreateUser = () => {
  const queryClient = useQueryClient();
  return useMutation<User, Error, UserCreate>({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] }); // Инвалидация кеша списка
      notifications.show({ 
        title: 'Успех', 
        message: 'Пользователь успешно создан', 
        color: 'green' 
      });
    },
    onError: (error) => {
       notifications.show({ 
         title: 'Ошибка', 
         message: error.message || 'Не удалось создать пользователя', 
         color: 'red' 
       });
    }
  });
};

// Функция для обновления пользователя
const updateUser = async ({ id, userData }: { id: number; userData: UserUpdate }): Promise<User> => {
  const { data } = await api.put(`${API_URL_USERS}${id}`, userData);
  return data;
};

// Хук для обновления пользователя
export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  return useMutation<User, Error, { id: number; userData: UserUpdate }>({
    mutationFn: updateUser,
    onSuccess: (updatedUser) => {
      // Обновляем кеш списка и конкретного пользователя
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] }); 
      queryClient.setQueryData([USERS_QUERY_KEY, updatedUser.id], updatedUser);
      notifications.show({ 
        title: 'Успех', 
        message: 'Пользователь успешно обновлен', 
        color: 'green' 
      });
    },
     onError: (error) => {
       notifications.show({ 
         title: 'Ошибка', 
         message: error.message || 'Не удалось обновить пользователя', 
         color: 'red' 
       });
    }
  });
};

// Функция для удаления пользователя
const deleteUser = async (id: number): Promise<User> => {
  const { data } = await api.delete(`${API_URL_USERS}${id}`);
  return data;
};

// Хук для удаления пользователя
export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  return useMutation<User, Error, number>({
    mutationFn: deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] }); // Инвалидация кеша списка
      notifications.show({ 
        title: 'Успех', 
        message: 'Пользователь успешно удален', 
        color: 'green' 
      });
    },
     onError: (error) => {
       notifications.show({ 
         title: 'Ошибка', 
         message: error.message || 'Не удалось удалить пользователя', 
         color: 'red' 
       });
    }
  });
};

// === Хуки для текущего пользователя (/me) ===

// Функция для получения текущего пользователя
const fetchCurrentUser = async (): Promise<User> => {
    const { data } = await api.get(`${API_URL_USERS}me`);
    return data;
};

// Хук для получения текущего пользователя
export const useCurrentUser = () => {
    return useQuery<User, Error>({
        queryKey: [CURRENT_USER_QUERY_KEY],
        queryFn: fetchCurrentUser,
        retry: false, // Не повторять запрос при ошибке (например, 401)
        staleTime: Infinity, // Данные считаются свежими всегда (обновляются при логине/логауте)
    });
};

// Функция для обновления текущего пользователя
const updateCurrentUser = async (userData: UserUpdate): Promise<User> => {
    const { data } = await api.put(`${API_URL_USERS}me`, userData);
    return data;
};

// Хук для обновления текущего пользователя
export const useUpdateCurrentUser = () => {
    const queryClient = useQueryClient();
    return useMutation<User, Error, UserUpdate>({
        mutationFn: updateCurrentUser,
        onSuccess: (updatedUser) => {
            queryClient.setQueryData([CURRENT_USER_QUERY_KEY], updatedUser); // Обновляем кеш текущего пользователя
            notifications.show({
                title: 'Успех',
                message: 'Ваш профиль обновлен',
                color: 'green',
            });
        },
        onError: (error) => {
            notifications.show({
                title: 'Ошибка',
                message: error.message || 'Не удалось обновить профиль',
                color: 'red',
            });
        },
    });
}; 