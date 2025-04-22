import { api } from './client'; // Правильный импорт базового API клиента
import { Function, FunctionCreate, FunctionUpdate } from '../types/function';

// Константа с префиксом API
const API_URL_FUNCTIONS = '/api/v1/functions/'; // URL со слешем!

export const functionApi = {
  getAll: async (params: { skip?: number; limit?: number } = {}): Promise<Function[]> => {
    const response = await api.get<Function[]>(API_URL_FUNCTIONS, { params });
    return response.data;
  },

  getById: async (id: number): Promise<Function> => {
    // БЕЗ слеша для ID!
    const response = await api.get<Function>(`/api/v1/functions/${id}`);
    return response.data;
  },

  create: async (functionData: FunctionCreate): Promise<Function> => {
    const response = await api.post<Function>(API_URL_FUNCTIONS, functionData);
    return response.data;
  },

  update: async (id: number, functionData: FunctionUpdate): Promise<Function> => {
    // БЕЗ слеша для ID!
    const response = await api.put<Function>(`/api/v1/functions/${id}`, functionData);
    return response.data;
  },

  delete: async (id: number): Promise<Function> => {
    // БЕЗ слеша для ID!
    const response = await api.delete<Function>(`/api/v1/functions/${id}`);
    return response.data;
  },
}; 