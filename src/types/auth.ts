
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  dairy_name: string;
  dairy_id: string;
  expires_in: number;
}

export interface AuthUser {
  token: string;
  dairy_name: string;
  dairy_id: string;
  expires_at: number;
}
