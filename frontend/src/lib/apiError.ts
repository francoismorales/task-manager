import { AxiosError } from 'axios';
import type { ApiErrorResponse } from '@/types/auth';

/**
 * Extracts a human-readable message from a FastAPI error response.
 *
 * FastAPI returns:
 *  - `{ detail: "string" }` for HTTPException (400/401/404/409/...)
 *  - `{ detail: [{ msg, loc, type }] }` for 422 validation errors
 */
export function extractApiError(error: unknown, fallback = 'Error inesperado'): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    if (data?.detail) {
      if (typeof data.detail === 'string') return data.detail;
      if (Array.isArray(data.detail)) {
        return data.detail.map((d) => d.msg).join('. ');
      }
    }
    if (error.message) return error.message;
  }

  if (error instanceof Error) return error.message;
  return fallback;
}