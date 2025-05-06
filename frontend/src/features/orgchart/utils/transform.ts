import { OrgChartNodeData } from '../types/orgChartTypes';

export type ApiPosition = {
  id: number;
  name: string;
  code?: string;
  description?: string;
  level?: number;
  children?: ApiPosition[];
};

export type ApiOrganization = {
  id: number;
  name: string;
  code?: string;
  description?: string;
  org_type?: string;
  parent_id?: number | null;
  children?: ApiOrganization[];
};

// Сопоставляем org_type из API к типу узла диаграммы
export const mapOrgTypeToNodeType = (orgType?: string): 'department' | 'division' | 'position' => {
  switch (orgType) {
    case 'HOLDING':
    case 'HEAD_OFFICE':
      return 'department';
    case 'LEGAL_ENTITY':
    case 'BRANCH':
      return 'division';
    default:
      return 'position';
  }
};

// Функция создания узла с ошибкой
export const createErrorNode = (id: string, message: string): OrgChartNodeData => {
  return {
    id,
    name: message,
    type: 'position',
  };
};

// Генерация уникального ID для узла
export const generateNodeId = (prefix: string, id: number | string): string => {
  return `${prefix}-${id}`;
};

// Безопасно трансформирует узел организации в узел для оргчарта
export const transformOrganizationNode = (node: any): OrgChartNodeData => {
  if (!node || typeof node !== 'object') {
    console.warn('Некорректный узел данных:', node);
    return createErrorNode(`error-${Math.random().toString(36).substr(2, 9)}`, 'Ошибка данных');
  }

  try {
    // Безопасно проверяем ID
    const nodeId = node.id !== undefined ? node.id : Math.random().toString(36).substr(2, 9);
    
    // Проверяем, имеет ли узел поле level (должность)
    const isPosition = 'level' in node;
    const nodeType: 'department' | 'division' | 'position' = 
      isPosition ? 'position' : mapOrgTypeToNodeType(('org_type' in node) ? node.org_type : undefined);
    
    const result: OrgChartNodeData = {
      id: generateNodeId(isPosition ? 'pos' : 'org', nodeId),
      name: node.name || 'Без названия',
      title: node.description || '',
      type: nodeType,
      code: node.code,
    };

    // Если это должность с уровнем, добавляем поле level
    if (isPosition && node.level !== undefined) {
      result.level = Number(node.level);
    }

    // Безопасно обрабатываем дочерние элементы
    if (node.children) {
      // Проверяем, что children - массив
      if (Array.isArray(node.children)) {
        const validChildren = node.children
          .filter(Boolean) // Отфильтровываем null/undefined
          .map((child: any) => {
            try {
              return transformOrganizationNode(child);
            } catch (err) {
              console.error('Ошибка при трансформации дочернего узла:', err);
              // Возвращаем узел-заглушку вместо падения
              return createErrorNode(
                `error-child-${Math.random().toString(36).substr(2, 9)}`,
                'Ошибка данных дочернего узла'
              );
            }
          });
          
        // Добавляем дочерние элементы только если есть хотя бы один валидный
        if (validChildren.length > 0) {
          result.children = validChildren;
        }
      } else {
        console.warn('Поле children не является массивом:', node.children);
      }
    }
    
    return result;
  } catch (err) {
    console.error('Ошибка при трансформации узла:', err, node);
    // В случае ошибки возвращаем узел-заглушку
    return createErrorNode(
      `error-${Math.random().toString(36).substr(2, 9)}`,
      'Ошибка преобразования данных'
    );
  }
};

// Основная функция трансформации данных API в формат для OrgChart
export const transformOrganizationData = (apiData: any): OrgChartNodeData => {
  // Проверка на пустые данные
  if (!apiData) {
    console.warn('Отсутствуют данные от API');
    return {
      id: 'root',
      name: 'Нет данных',
      type: 'department',
    };
  }

  try {
    // Обработка массива данных
    if (Array.isArray(apiData)) {
      if (apiData.length === 0) {
        return {
          id: 'root',
          name: 'Нет данных',
          type: 'department',
        };
      }
      
      // Фильтруем только валидные элементы
      const validItems = apiData.filter(Boolean);
      
      if (validItems.length === 0) {
        return {
          id: 'root',
          name: 'Пустые данные',
          type: 'department',
        };
      }
      
      if (validItems.length === 1) {
        return transformOrganizationNode(validItems[0]);
      }
      
      // Создаем корневой узел и добавляем все элементы массива как дочерние
      const children = validItems.map(item => transformOrganizationNode(item));
      
      return {
        id: 'root',
        name: 'Организационная структура',
        type: 'department',
        children: children.length > 0 ? children : undefined
      };
    }
    
    // Обработка единичного объекта
    return transformOrganizationNode(apiData);
  } catch (err) {
    console.error('Критическая ошибка при трансформации данных:', err);
    // В случае критической ошибки возвращаем узел-заглушку
    return {
      id: 'root-error',
      name: 'Ошибка загрузки структуры',
      type: 'department',
    };
  }
}; 