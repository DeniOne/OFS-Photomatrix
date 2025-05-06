import { OrgChartSettingsValues } from '../types/orgChartSettingsTypes';

/**
 * Определяет размеры узла на основе настроек визуализации.
 * @param settings - Текущие настройки диаграммы.
 * @returns Объект с шириной и высотой узла.
 */
export const getNodeDimensions = (settings: OrgChartSettingsValues): { width: number; height: number } => {
  // Увеличиваем ширину блоков, чтобы текст лучше помещался
  const width = settings.compactView ? 160 : 220;
  const height = settings.compactView ? 70 : 90;
  return { width, height };
}; 