import type { User } from '@/types/auth';

export type ProjectRole = 'owner' | 'member';

export interface Project {
  id: number;
  name: string;
  description: string | null;
  deadline: string | null; // ISO date "YYYY-MM-DD"
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: number;
  user: User;
  role: ProjectRole;
  joined_at: string;
}

export interface ProjectDetail extends Project {
  owner: User;
  members: ProjectMember[];
}

export interface ProjectCreatePayload {
  name: string;
  description?: string | null;
  deadline?: string | null;
}

export type ProjectUpdatePayload = Partial<ProjectCreatePayload>;