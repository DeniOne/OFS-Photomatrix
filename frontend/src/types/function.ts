import { Section } from './section'; // Импортируем тип Section

export interface Function {
  id: number;
  name: string;
  code: string;
  section_id: number;
  description: string | null;
  is_active: boolean;
  created_at: string; // Или Date
  updated_at: string; // Или Date
  section?: Section; // Опционально, если нужна информация о секции
}

export interface FunctionCreate {
  name: string;
  code: string;
  section_id: number;
  description?: string | null;
  is_active?: boolean;
}

export type FunctionUpdate = Partial<FunctionCreate>; 