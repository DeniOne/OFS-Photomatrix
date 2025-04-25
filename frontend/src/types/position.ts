import { Section } from './section';
import { Division } from './division';

export interface Position {
  id: number;
  name: string;
  code: string;
  division_id: number | null;
  section_id: number | null;
  attribute: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  section?: Section; // Опциональный объект отдела
  division?: Division; // Опциональный объект подразделения
  function_ids?: number[]; // Массив ID связанных функций
}

export interface PositionCreate {
  name: string;
  code: string;
  section_id?: number;
  division_id?: number | null;
  attribute?: string | null;
  description?: string | null;
  is_active?: boolean;
  function_ids?: number[]; // Массив ID связанных функций
}

export type PositionUpdate = Partial<PositionCreate>; 