import { User } from './user';
import { Position } from './position';

export interface Staff {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string | null;
  email?: string | null;
  phone?: string | null;
  hire_date?: string | null; // ISO формат даты
  user_id?: number | null;
  photo_path?: string | null;
  document_paths?: Record<string, string> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user?: User;
  staff_positions?: StaffPosition[];
  organization_name?: string | null; // Название организации
}

export interface StaffPosition {
  id: number;
  staff_id: number;
  position_id: number;
  is_primary: boolean;
  start_date?: string | null;
  end_date?: string | null;
  created_at: string;
  updated_at: string;
  position?: Position;
}

export interface StaffCreate {
  first_name: string;
  last_name: string;
  middle_name?: string;
  email?: string;
  phone?: string;
  hire_date?: string;
  user_id?: number;
  photo_path?: string;
  document_paths?: Record<string, string>;
  is_active?: boolean;
  create_user?: boolean; // Флаг для создания связанного пользователя
  position_id?: number;  // ID должности
  organization_id?: number;  // ID организации (юрлица)
  location_id?: number;  // ID локации
  is_primary_position?: boolean;  // Является ли должность основной
}

export interface StaffCreateResponse extends Staff {
  activation_code?: string | null;
}

export interface StaffUpdate {
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  email?: string;
  phone?: string;
  hire_date?: string;
  user_id?: number;
  photo_path?: string;
  document_paths?: Record<string, string>;
  is_active?: boolean;
  create_user?: boolean;
  position_id?: number;  // ID должности
  organization_id?: number;  // ID организации (юрлица)
  location_id?: number;  // ID локации
  is_primary_position?: boolean;  // Является ли должность основной
}

export interface StaffWithPositions extends Staff {
  positions: Position[];
}

// Интерфейс для RocketChat данных сотрудника
export interface StaffRocketChat {
  username: string; // Обычно email или другой уникальный идентификатор
  email: string;
  name: string; // Полное имя
  password?: string; // Опционально, для создания
  roles?: string[]; // Роли в Rocket.Chat
  active?: boolean;
} 