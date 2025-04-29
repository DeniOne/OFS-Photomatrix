import { OrgChartNode } from '../components/OrgChart';
import { DivisionType } from '../../../types/division'; // Импортируем enum, если он есть

// Типы для примера, замените на реальные типы из бэкенда, если они отличаются
type BackendNode = BackendDivisionNode | BackendStaffNode;

interface BackendDivisionNode {
  id: number;
  name: string;
  type: 'DEPARTMENT' | 'DIVISION';
  code?: string;
  children?: BackendNode[]; 
}

interface BackendStaffNode {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
  position_name?: string;
  type: 'STAFF'; 
}

/**
 * Рекурсивно преобразует данные из формата бэкенда 
 * в формат, необходимый для компонента OrgChart.
 * @param backendNode - Узел данных из бэкенда.
 * @returns Узел в формате OrgChartNode.
 */
export function transformDataForOrgChart(backendNode: BackendNode): OrgChartNode {
  let node: Partial<OrgChartNode> = {
      // Преобразуем ID в строку и добавляем префикс
      id: `${backendNode.type.toLowerCase()}-${backendNode.id}`, 
  };

  if (backendNode.type === 'DEPARTMENT' || backendNode.type === 'DIVISION') {
      const division = backendNode as BackendDivisionNode;
      node.name = division.name;
      node.type = division.type === 'DEPARTMENT' ? 'department' : 'division';
      node.code = division.code;
  } else if (backendNode.type === 'STAFF') {
      const staff = backendNode as BackendStaffNode;
      // Собираем ФИО
      node.name = `${staff.last_name} ${staff.first_name}${staff.middle_name ? ' ' + staff.middle_name : ''}`;
      node.title = staff.position_name; // Используем название должности как title
      node.type = 'position'; // Staff узлы соответствуют типу 'position' в нашей диаграмме
  } else {
      // Обработка неизвестного типа узла, если необходимо
      console.warn("Unknown backend node type:", backendNode);
      node.name = "Неизвестный узел";
      node.type = undefined; // Или какой-то тип по умолчанию
  }

  // Рекурсивно обрабатываем дочерние элементы, если они есть
  if ('children' in backendNode && backendNode.children && backendNode.children.length > 0) {
      node.children = backendNode.children
          .map(child => transformDataForOrgChart(child)) // Рекурсивный вызов
          .filter(child => child !== null); // Фильтруем null, если преобразование не удалось
  } else {
    // Важно установить пустой массив или undefined, чтобы D3 правильно строил дерево
    node.children = undefined; 
  }

  // Проверяем, что все обязательные поля установлены
  if (!node.id || !node.name) {
      console.error("Failed to transform node:", backendNode);
      // В реальном приложении здесь может быть более строгая обработка ошибки
      // Возвращаем "пустой" узел или кидаем ошибку, чтобы избежать проблем в D3
      // Для простоты вернем как есть, но D3 может выдать ошибку позже
  }

  return node as OrgChartNode; // Утверждаем тип, т.к. мы заполнили обязательные поля
}

/**
 * Обертка для преобразования корневого элемента данных.
 * @param backendData - Корневой узел данных из бэкенда.
 * @returns Корневой узел в формате OrgChartNode или null при ошибке.
 */
export function transformBackendData(backendData: BackendOrgChartData | null | undefined): OrgChartNode | null {
    if (!backendData) {
        return null;
    }
    try {
        return transformDataForOrgChart(backendData);
    } catch (error) {
        console.error("Error transforming backend data:", error);
        return null;
    }
}

// Пример типа для корневого элемента с бэкенда
export type BackendOrgChartData = BackendDivisionNode; 