import { apiClient } from '@/lib/apiClient';
import type {
  AuthToken,
  LoginPayload,
  RegisterPayload,
  User,
} from '@/types/auth';

/**
 * Auth API service. Components/contexts call these — never axios directly.
 * Keeps endpoints in one place and makes mocking trivial.
 */
export const authService = {
  async register(payload: RegisterPayload): Promise<AuthToken> {
    const { data } = await apiClient.post<AuthToken>('/auth/register', payload);
    return data;
  },

  async login(payload: LoginPayload): Promise<AuthToken> {
    const { data } = await apiClient.post<AuthToken>('/auth/login', payload);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },
};