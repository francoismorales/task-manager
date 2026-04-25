import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

import {
  TOKEN_STORAGE_KEY,
  UNAUTHORIZED_EVENT,
} from '@/lib/apiClient';
import { authService } from '@/services/authService';
import type { LoginPayload, RegisterPayload, User } from '@/types/auth';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  // Start in loading state if there's a token to validate. If there's no token,
  // we already know the user is anonymous, so skip the loading flicker.
  const [isLoading, setIsLoading] = useState<boolean>(
    () => localStorage.getItem(TOKEN_STORAGE_KEY) !== null,
  );

  const handleLogout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setUser(null);
  }, []);

  /** Bootstrap: if we have a token in storage, fetch the current user. */
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }

    authService
      .getCurrentUser()
      .then(setUser)
      .catch(() => handleLogout())
      .finally(() => setIsLoading(false));
  }, [handleLogout]);

  /** React to 401s emitted by the apiClient interceptor. */
  useEffect(() => {
    const onUnauthorized = () => setUser(null);
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const { access_token } = await authService.login(payload);
    localStorage.setItem(TOKEN_STORAGE_KEY, access_token);
    const me = await authService.getCurrentUser();
    setUser(me);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const { access_token } = await authService.register(payload);
    localStorage.setItem(TOKEN_STORAGE_KEY, access_token);
    const me = await authService.getCurrentUser();
    setUser(me);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout: handleLogout,
    }),
    [user, isLoading, login, register, handleLogout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}