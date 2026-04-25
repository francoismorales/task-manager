import { apiClient } from '@/lib/apiClient';
import type {
  Task,
  TaskCreatePayload,
  TaskFilters,
  TaskUpdatePayload,
} from '@/types/task';

/**
 * Task API service. All endpoints are nested under a project.
 * Filters are sent as query params; undefined values are stripped by axios.
 */
export const taskService = {
  async list(projectId: number, filters: TaskFilters = {}): Promise<Task[]> {
    const { data } = await apiClient.get<Task[]>(
      `/projects/${projectId}/tasks`,
      { params: filters },
    );
    return data;
  },

  async create(projectId: number, payload: TaskCreatePayload): Promise<Task> {
    const { data } = await apiClient.post<Task>(
      `/projects/${projectId}/tasks`,
      payload,
    );
    return data;
  },

  async update(
    projectId: number,
    taskId: number,
    payload: TaskUpdatePayload,
  ): Promise<Task> {
    const { data } = await apiClient.put<Task>(
      `/projects/${projectId}/tasks/${taskId}`,
      payload,
    );
    return data;
  },

  async remove(projectId: number, taskId: number): Promise<void> {
    await apiClient.delete(`/projects/${projectId}/tasks/${taskId}`);
  },
};