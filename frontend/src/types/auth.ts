export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
}

export interface ApiErrorResponse {
  detail:
    | string
    | Array<{ type: string; loc: (string | number)[]; msg: string }>;
}