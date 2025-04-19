// Типы данных для Организаций на фронтенде

// Базовый тип организации (совпадает с Organization из схемы)
export interface Organization {
  id: number;
  name: string;
  code: string;
  description: string | null;
  org_type: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION'; // Уточняем возможные типы
  parent_id: number | null;
  is_active: boolean;
  created_at: string; // Даты приходят как строки
  updated_at: string;
  // Поля, которых нет в базовой схеме, но могут прийти (например, из OrganizationWithChildren)
  children?: Organization[]; 
}

// Тип для создания организации (совпадает с OrganizationCreate)
export interface OrganizationCreateDto {
  name: string;
  code: string;
  description?: string | null;
  org_type: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION'; 
  parent_id?: number | null;
  is_active?: boolean;
}

// Тип для обновления организации (совпадает с OrganizationUpdate)
export interface OrganizationUpdateDto {
  name?: string;
  code?: string;
  description?: string | null;
  org_type?: 'HOLDING' | 'LEGAL_ENTITY' | 'LOCATION'; 
  parent_id?: number | null;
  is_active?: boolean;
}

// Тип ответа от API при создании (добавили activation_code для staff)
// Для организаций он не нужен, но оставим общую структуру ответа
export interface ApiResponse<T> {
    data: T;
    message?: string;
    // Можно добавить другие поля ответа API при необходимости
}

// Тип ответа для создания организации (сейчас совпадает с Organization)
// Используем общий тип Organization, т.к. activation_code нерелевантен
// export interface OrganizationCreateResponse extends Organization {} 