// Типы для подразделений (департаментов и отделов)

import { Organization } from './organization';

// Константы для типов подразделений
export enum DivisionType {
  DEPARTMENT = 'DEPARTMENT', // Департамент (верхний уровень)
  DIVISION = 'DIVISION'      // Отдел (дочерний уровень)
}

// Базовый тип подразделения
export interface Division {
  id: number;
  name: string;
  code: string;
  description?: string;
  organization_id: number;
  organization?: Organization;
  parent_id: number | null;
  parent?: Division | null;
  is_active: boolean;
  type: DivisionType;         // Тип подразделения: департамент или отдел
  created_at: string;
  updated_at: string;
}

// Тип для создания нового подразделения
export interface DivisionCreate {
  name: string;
  code: string;
  description?: string;
  organization_id: number;
  parent_id?: number | null;
  is_active: boolean;
  type: DivisionType;         // Добавляем тип подразделения
}

// Тип для обновления подразделения
export interface DivisionUpdate extends DivisionCreate {
  id: number;
}

// Тип для подразделения с дочерними подразделениями
export interface DivisionWithChildren extends Division {
  children: DivisionWithChildren[];
} 