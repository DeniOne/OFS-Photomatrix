// Интерфейс для значений настроек
export interface OrgChartSettingsValues {
  // Основные настройки
  layout: 'horizontal' | 'vertical' | 'radial';
  zoom: number;
  
  // Размеры и отступы
  nodeSizePreset: 'small' | 'medium' | 'large' | 'custom';
  nodeWidth: number;
  nodeHeight: number;
  siblingGap: number;
  levelGap: number;
  nodeBorderRadius: number;
  
  // Внешний вид
  compactView: boolean;
  showTitle: boolean;
  showDepartmentCode: boolean;
  
  // Цвета
  colorByType: boolean;
  departmentColor: string;
  divisionColor: string;
  
  // Ограничения данных
  maxDepth: number | null;
}

// Дефолтные значения настроек
export const defaultOrgChartSettings: OrgChartSettingsValues = {
  layout: 'vertical',
  zoom: 0.8,
  
  nodeSizePreset: 'medium',
  nodeWidth: 220,
  nodeHeight: 90,
  siblingGap: 50,
  levelGap: 100,
  nodeBorderRadius: 8,
  
  compactView: false,
  showTitle: true,
  showDepartmentCode: true,
  
  colorByType: true,
  departmentColor: '#1971c2',
  divisionColor: '#2f9e44',
  
  maxDepth: null,
};

// Пресеты размеров узлов
export const nodeSizePresets = {
  small: { width: 160, height: 70 },
  medium: { width: 220, height: 90 },
  large: { width: 280, height: 120 },
  custom: { width: 0, height: 0 }, // Будет заполнено текущими значениями
}; 