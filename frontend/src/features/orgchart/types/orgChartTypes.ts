// Импортируем типы настроек из нового файла
import { OrgChartSettingsValues } from './orgChartSettingsTypes';

// Типы организаций 
export type OrganizationType = 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION';

// Расширенные типы узлов
export type NodeType = 'department' | 'division' | 'section' | 'position' | 'function' | 'board';

// Возможные типы визуализации
export type OrgChartViewType = 'business' | 'legal' | 'location';

// Тип для данных узла, используемый D3 и компонентом узла
export interface OrgChartNodeData {
  id: string; // Уникальный ID (с префиксом типа)
  name: string; // Отображаемое имя
  title?: string; // Должность или доп. информация
  type?: NodeType; // Тип узла
  code?: string; // Код подразделения
  level?: number; // Уровень должности или подразделения
  position_level?: number; // Уровень должности для бизнес-иерархии
  
  // Поля для организаций
  org_type?: OrganizationType; // Тип организации (HOLDING, LEGAL_ENTITY, LOCATION)
  
  // Поля для должностей и сотрудников
  staffId?: number | string; // ID сотрудника, если узел - должность с привязанным сотрудником
  staffName?: string; // Имя сотрудника, если должность занята
  positionId?: number; // ID должности
  
  // Дополнительные бизнес-поля
  has_ckp?: boolean; // Наличие ценного конечного продукта
  organization_id?: number | string; // Связь с организацией
  parent_id?: number | string; // Родительская сущность
  
  // Структура дерева
  children?: OrgChartNodeData[]; // Видимые дети
  _children?: OrgChartNodeData[]; // Скрытые дети (для D3)
  
  // Специфичные поля
  division_id?: number | string;
  section_id?: number | string;
  
  // Флаги
  is_vacant?: boolean;
}

// Тип для ref handle компонента OrgChart
export interface OrgChartHandle {
  // Метод для центрирования на узле
  zoomToNode: (nodeId: string) => void;
  // Метод для сброса масштаба
  resetZoom: () => void;
  // Метод для увеличения масштаба
  zoomIn: () => void;
  // Метод для уменьшения масштаба
  zoomOut: () => void;
  // Метод для экспорта в изображение
  exportAsImage: () => Promise<string | null>;
}

// Тип для пропсов компонента OrgChart
export interface OrgChartProps {
  // Обязательно передаем данные или null
  data: OrgChartNodeData | null; 
  // Настройки визуализации
  settings?: Record<string, any>;
  // Ширина контейнера (для расчетов D3)
  width?: number;
  // Высота контейнера (для расчетов D3)
  height?: number;
  // Обработчик клика по узлу
  onNodeClick?: (nodeId: string) => void;
  // Поисковый запрос для подсветки узлов
  searchTerm?: string;
  viewType?: OrgChartViewType; // Тип визуализации
} 