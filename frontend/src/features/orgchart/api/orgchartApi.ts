// Закомментируй или удали этот импорт, если он неправильный
// import { axiosInstance } from '../../../api/client'; 
import { api } from '../../../api/client'; // Используем 'api'
import { OrgChartNode } from '../components/OrgChart'; // Импортируем наш тип
import { BackendOrgChartData } from '../utils/orgChartUtils'; // Импортируем тип бэкенда

// ВРЕМЕННО: Создаем фейковый axiosInstance, чтобы убрать ошибку TS
const axiosInstance = {
  get: async <T>(url: string): Promise<{ data: T }> => {
    console.warn(`FAKE API CALL: GET ${url}`);
    // Возвращаем фейковые данные, чтобы код не падал
    // В идеале, формат должен соответствовать BackendOrgChartData
    return { data: { id: 1, name: 'Fake Root', type: 'DEPARTMENT', children: [] } as any }; 
  }
};
// КОНЕЦ ВРЕМЕННОГО КОДА

// Функция для получения данных оргструктуры
export const getOrgChartStructure = async (): Promise<BackendOrgChartData> => {
  try {
    // Используем 'api' вместо 'axiosInstance'
    const response = await api.get<BackendOrgChartData>('/orgchart/structure'); 
    
    // Проверяем статус ответа (axiosInstance может делать это автоматически)
    // if (!response.ok) { // Для fetch API
    //   throw new Error('Network response was not ok');
    // }
    
    // Возвращаем данные из ответа
    return response.data;
  } catch (error) {
    // Обрабатываем ошибки запроса
    console.error("Error fetching organization chart structure:", error);
    // Перебрасываем ошибку, чтобы react-query мог ее поймать
    throw error; 
  }
}; 