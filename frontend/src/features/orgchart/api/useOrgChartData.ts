import { useQuery } from '@tanstack/react-query';
import { getOrgChartStructure } from './orgchartApi';
import { OrgChartNode } from '../components/OrgChart';
import { transformBackendData } from '../utils/orgChartUtils';
import { BackendOrgChartData } from '../utils/orgChartUtils';

// Ключ запроса для react-query
const ORG_CHART_QUERY_KEY = ['orgChart', 'structure'];

/**
 * Хук для загрузки и преобразования данных организационной структуры.
 */
export const useOrgChartData = () => {
  return useQuery<BackendOrgChartData, Error, OrgChartNode | null>({
    queryKey: ORG_CHART_QUERY_KEY,
    queryFn: getOrgChartStructure,
    select: transformBackendData,
    // Дополнительные опции react-query по необходимости:
    // staleTime: 5 * 60 * 1000, // 5 минут
    // gcTime: 30 * 60 * 1000, // 30 минут
    // refetchOnWindowFocus: false,
  });
}; 