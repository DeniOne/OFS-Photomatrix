// Типы данных для Организаций

// Базовый тип организации
export interface Organization {
  id: number;
  name: string;
  code: string;
  description: string | null;
  org_type: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION';
  parent_id: number | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  children?: Organization[];
}

// Тип для создания организации
export interface OrganizationCreateDto {
  name: string;
  code: string;
  description?: string | null;
  org_type: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION';
  parent_id?: number | null;
  is_active?: boolean;
}

// Тип для обновления организации
export interface OrganizationUpdateDto {
  name?: string;
  code?: string;
  description?: string | null;
  org_type?: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION';
  parent_id?: number | null;
  is_active?: boolean;
} 