import { User } from './user';
import { Position } from './position';

// Интерфейс, описывающий данные должности, возвращаемые API в массиве positions
export interface StaffPositionInfo {
  id: number;
  staff_id: number;
  position_id: number;
  is_primary: boolean;
  position_name: string | null; // Используем это поле
  // start_date, end_date, created_at, updated_at можно добавить, если они нужны на фронте
}

export interface Staff {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string | null;
  email?: string | null;
  phone?: string | null;
  hire_date?: string | null; // ISO формат даты
  user_id?: number | null;
  organization_id?: number | null; // Добавляем organization_id
  photo_path?: string | null;
  document_paths?: Record<string, string> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user?: User | null; // Пользователь может быть null
  positions?: StaffPositionInfo[]; // Меняем staff_positions на positions и используем новый тип
  organization_name?: string | null; 
}

// Интерфейс для создания должности при создании/обновлении сотрудника
export interface StaffPositionCreateData {
  position_id: number;
  is_primary: boolean;
}

export interface StaffCreate {
  first_name: string;
  last_name: string;
  middle_name?: string;
  email?: string;
  phone?: string;
  hire_date?: string;
  organization_id?: number;
  is_active?: boolean;
  positions?: StaffPositionCreateData[]; // Используем массив должностей
  create_user?: boolean; 
  password?: string; // Пароль опционален, только если create_user=true
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
  organization_id?: number; // Можно обновлять организацию
  is_active?: boolean;
  positions?: StaffPositionCreateData[]; // Можно обновлять должности
  // user_id, create_user, password обычно не обновляются этим методом
  // Если нужно обновить user_id или создать/изменить пользователя, нужны отдельные поля/логика
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