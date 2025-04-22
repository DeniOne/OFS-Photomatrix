import { Division } from './division'; // Импортируем тип Division, если нужно

export interface Section {
  id: number;
  name: string;
  code: string;
  division_id: number;
  description: string | null;
  is_active: boolean;
  created_at: string; // Или Date
  updated_at: string; // Или Date
  division?: Division; // Опционально, если нужна информация о подразделении
}

export interface SectionCreate {
  name: string;
  code: string;
  division_id: number;
  description?: string | null;
  is_active?: boolean;
}

export type SectionUpdate = Partial<SectionCreate>; 