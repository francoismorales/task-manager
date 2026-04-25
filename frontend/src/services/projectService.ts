import { apiClient } from '@/lib/apiClient';
import type {
  Project,
  ProjectCreatePayload,
  ProjectDetail,
  ProjectMember,
  ProjectUpdatePayload,
} from '@/types/project';

/**
 * Project API service. All endpoints require authentication —
 * the apiClient interceptor attaches the JWT automatically.
 */
export const projectService = {
  async list(): Promise<Project[]> {
    const { data } = await apiClient.get<Project[]>('/projects');
    return data;
  },

  async get(id: number): Promise<ProjectDetail> {
    const { data } = await apiClient.get<ProjectDetail>(`/projects/${id}`);
    return data;
  },

  async create(payload: ProjectCreatePayload): Promise<Project> {
    const { data } = await apiClient.post<Project>('/projects', payload);
    return data;
  },

  async update(id: number, payload: ProjectUpdatePayload): Promise<Project> {
    const { data } = await apiClient.put<Project>(`/projects/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/projects/${id}`);
  },

  // --- Team membership ----------------------------------------------------
  async inviteMember(projectId: number, email: string): Promise<ProjectMember> {
    const { data } = await apiClient.post<ProjectMember>(
      `/projects/${projectId}/members`,
      { email },
    );
    return data;
  },

  async removeMember(projectId: number, userId: number): Promise<void> {
    await apiClient.delete(`/projects/${projectId}/members/${userId}`);
  },
};