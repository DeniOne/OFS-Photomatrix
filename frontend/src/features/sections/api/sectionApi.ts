import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../api/client'; // Исправленный импорт axios instance
// import { useNotificationStore } from '@/stores/notifications'; // Закомментировано, т.к. не найден
import { Section, SectionCreate, SectionUpdate } from '../../../types/section';
// import { IconCheck, IconX } from '@tabler/icons-react'; // Закомментировано, т.к. уведомления отключены

// const SECTIONS_QUERY_KEY = ['sections']; // Не используется, удалено или закомментировано
const API_URL_SECTIONS = '/api/v1/sections/'; // URL со слешем!

// --- Функции для вызова API ---

// Возвращаем параметр division_id для фильтрации
const fetchSections = async (division_id?: number | null): Promise<Section[]> => {
  let url = API_URL_SECTIONS;
  // Добавляем параметр запроса, если division_id передан
  if (division_id) {
    url += `?division_id=${division_id}`;
  }
  console.log(`Запрос секций: ${url}`); // Добавим лог для отладки
  const response = await api.get<Section[]>(url); 
  return response.data;
};

const createSection = async (data: SectionCreate): Promise<Section> => {
  const response = await api.post<Section>(API_URL_SECTIONS, data); // Используем api
  return response.data;
};

// Принимает один объект { id, data }
const updateSection = async ({ id, data }: { id: number; data: SectionUpdate }): Promise<Section> => {
  // БЕЗ слеша для ID!
  const response = await api.put<Section>(`/api/v1/sections/${id}`, data); // Используем api
  return response.data;
};

const deleteSection = async (id: number): Promise<void> => {
  // БЕЗ слеша для ID!
  await api.delete(`/api/v1/sections/${id}`); // Используем api
};

// --- Хуки React Query (v5 синтаксис) ---

// Хук для получения списка секций (опционально фильтр по division_id)
// Принимает divisionId как аргумент
export const useSections = (divisionId?: number | null) => {
  return useQuery<Section[], Error>({
    // Ключ запроса теперь включает divisionId, чтобы кэшировать результаты для каждого департамента
    queryKey: ['sections', 'byDivision', divisionId],
    // Вызываем fetchSections с переданным divisionId
    queryFn: () => fetchSections(divisionId),
    // Убираем enabled чтобы хук всегда выполнял запрос, даже с null
    // enabled: !!divisionId, 
    // Можно добавить retry: 1 или другие опции по желанию
    // onError обработка убрана в v5 из опций useQuery
  });
};

// Хук для создания секции
export const useCreateSection = () => {
  const queryClient = useQueryClient();
  // const { addNotification } = useNotificationStore(); // Закомментировано

  return useMutation<Section, Error, SectionCreate>({ // Добавлен тип Error
    mutationFn: createSection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections'] });
      console.log('Отдел создан');
      // addNotification({ // Закомментировано
      //   type: 'success',
      //   title: 'Отдел создан',
      //   message: 'Новый отдел успешно добавлен.',
      // });
    },
    onError: (error: Error) => { // Добавлен тип Error
      console.error('Ошибка создания отдела:', error);
      // addNotification({ // Закомментировано
      //   type: 'error',
      //   title: 'Ошибка создания отдела',
      //   message: error.message,
      // });
    },
  });
};

// Хук для обновления секции
export const useUpdateSection = () => {
  const queryClient = useQueryClient();
  // const { addNotification } = useNotificationStore(); // Закомментировано

  return useMutation<Section, Error, { id: number; data: SectionUpdate }>({ // Добавлен тип Error
    mutationFn: updateSection, // Передаем функцию напрямую
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['sections'] });
      queryClient.invalidateQueries({ queryKey: ['section', data.id] }); // Оставляем инвалидацию по ID
      console.log('Отдел обновлен:', data);
      // addNotification({ // Закомментировано
      //   type: 'success',
      //   title: 'Отдел обновлен',
      //   message: 'Данные отдела успешно обновлены.',
      // });
    },
    onError: (error: Error) => { // Добавлен тип Error
      console.error('Ошибка обновления отдела:', error);
      // addNotification({ // Закомментировано
      //   type: 'error',
      //   title: 'Ошибка обновления отдела',
      //   message: error.message,
      // });
    },
  });
};

// Хук для удаления секции
export const useDeleteSection = () => {
  const queryClient = useQueryClient();
  // const { addNotification } = useNotificationStore(); // Закомментировано

  return useMutation<void, Error, number>({ // Добавлен тип Error
    mutationFn: deleteSection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections'] });
      console.log('Отдел удален');
      // addNotification({ // Закомментировано
      //   type: 'success',
      //   title: 'Отдел удален',
      //   message: 'Отдел успешно удален.',
      // });
    },
    onError: (error: Error) => { // Добавлен тип Error
      console.error('Ошибка удаления отдела:', error);
      // addNotification({ // Закомментировано
      //   type: 'error',
      //   title: 'Ошибка удаления отдела',
      //   message: error.message,
      // });
    },
  });
}; 