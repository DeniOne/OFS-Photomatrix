export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  activation_code?: string | null;
}

export interface UserCreate {
  email: string;
  password?: string;
  full_name: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdate {
  email?: string;
  password?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserActivate {
  activation_code: string;
  password: string;
  password_confirm: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserLogin {
  username: string; // В большинстве случаев это email
  password: string;
} 