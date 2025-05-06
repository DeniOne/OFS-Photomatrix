import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { OrgChartNodeData, OrgChartViewType } from '../types/orgChartTypes';
import { mockOrgChartData } from '../mockData';

// Базовый URL API
const API_BASE = '/api/v1';

/**
 * Хук для загрузки данных организационной структуры с бэкенда
 * в зависимости от выбранного типа схемы
 */
export function useOrgChartData(viewType: OrgChartViewType = 'business') {
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const [data, setData] = useState<OrgChartNodeData|null>(null);

  // Получаем URL API в зависимости от типа схемы
  const getApiUrl = useCallback((type: OrgChartViewType): string => {
    switch (type) {
      case 'business':
        return `${API_BASE}/orgchart`;
      case 'legal':
        return `${API_BASE}/orgchart/legal`;
      case 'location':
        return `${API_BASE}/orgchart/location`;
      default:
        return `${API_BASE}/orgchart`;
    }
  }, []);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const apiUrl = getApiUrl(viewType);
      console.log(`Загрузка данных (${viewType}) с:`, apiUrl);
      
      // Запрос к API
      const response = await axios.get(apiUrl, {
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache'
        }
      });
      
      if (response && response.data) {
        console.log(`Данные (${viewType}) получены:`, response.data);
        console.log('Количество детей верхнего уровня:', response.data.children?.length || 0);
        
        // Проверяем структуру данных
        if (response.data.children) {
          console.log('Типы узлов верхнего уровня:', 
            response.data.children.map((child: any) => 
              `${child.name} (${child.type}${child.org_type ? ', ' + child.org_type : ''})`
            )
          );
        }
        
        // Устанавливаем данные
        setData(response.data as OrgChartNodeData);
      } else {
        throw new Error('Получен пустой ответ от сервера');
      }
    } catch (e: any) {
      console.error(`Ошибка загрузки данных (${viewType}):`, e);
      
      // Подробное логирование ошибки
      if (e.response) {
        console.error('Ошибка API:', {
          status: e.response.status,
          statusText: e.response.statusText,
          data: e.response.data
        });
        setError(`Ошибка API ${e.response.status}: ${e.response.statusText}`);
      } else if (e.request) {
        console.error('Нет ответа от сервера:', e.request);
        setError('Сервер не отвечает. Проверь запущен ли бэкенд.');
      } else {
        console.error('Неизвестная ошибка:', e.message);
        setError(`Ошибка: ${e.message}`);
      }
      
      // Загружаем тестовые данные для отображения
      console.log(`Загружаем тестовые данные (${viewType}) как запасной вариант`);
      setData(mockOrgChartData);
    } finally {
      setLoading(false);
    }
  }, [viewType, getApiUrl]);

  // Загружаем данные при монтировании компонента или смене типа
  useEffect(() => { 
    fetchData();
  }, [fetchData, viewType]);

  return { 
    isLoading, 
    error, 
    data, 
    refetch: fetchData 
  };
} 