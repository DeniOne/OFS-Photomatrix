import { api } from './client'; // Правильный импорт базового API клиента
import { Function, FunctionCreate, FunctionUpdate } from '../types/function';

// Константа с префиксом API
const API_URL_FUNCTIONS = '/functions/'; // Убрал дублирующийся префикс

export const functionApi = {
  getAll: async (params: { skip?: number; limit?: number } = {}): Promise<Function[]> => {
    const response = await api.get<Function[]>(API_URL_FUNCTIONS, { params });
    return response.data;
  },

  getById: async (id: number): Promise<Function> => {
    const response = await api.get<Function>(`/functions/${id}`);
    return response.data;
  },

  create: async (functionData: FunctionCreate): Promise<Function> => {
    const response = await api.post<Function>(API_URL_FUNCTIONS, functionData);
    return response.data;
  },

  update: async (id: number, functionData: FunctionUpdate): Promise<Function> => {
    const response = await api.put<Function>(`/functions/${id}`, functionData);
    return response.data;
  },

  delete: async (id: number): Promise<Function> => {
    const response = await api.delete<Function>(`/functions/${id}`);
    return response.data;
  },
}; 