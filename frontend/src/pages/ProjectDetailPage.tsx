import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import MembersSection from '@/components/MembersSection';
import TaskList from '@/components/TaskList';
import { useAuth } from '@/hooks/useAuth';
import { extractApiError } from '@/lib/apiError';
import { formatDate, isOverdue } from '@/lib/formatters';
import { projectService } from '@/services/projectService';
import type { ProjectDetail } from '@/types/project';

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const projectId = Number(id);

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadProject = useCallback(async () => {
    setError(null);
    try {
      const data = await projectService.get(projectId);
      setProject(data);
    } catch (err) {
      setError(extractApiError(err, 'No se pudo cargar el proyecto'));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (Number.isNaN(projectId)) {
      setError('ID de proyecto inválido');
      setIsLoading(false);
      return;
    }
    loadProject();
  }, [projectId, loadProject]);

  const isOwner = project !== null && user !== null && project.owner_id === user.id;

  async function handleDelete() {
    if (!project) return;
    const confirmed = window.confirm(
      `¿Eliminar el proyecto "${project.name}"? Esta acción no se puede deshacer.`,
    );
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await projectService.remove(project.id);
      navigate('/projects', { replace: true });
    } catch (err) {
      setError(extractApiError(err, 'No se pudo eliminar el proyecto'));
      setIsDeleting(false);
    }
  }

  if (isLoading) {
    return <div className="text-sm text-slate-500">Cargando…</div>;
  }

  if (error || !project) {
    return (
      <div className="max-w-xl mx-auto space-y-4">
        <Link to="/projects" className="text-sm text-brand-600 hover:underline">
          ← Volver a proyectos
        </Link>
        <div
          role="alert"
          className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
        >
          {error ?? 'Proyecto no encontrado'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-sm">
        <Link to="/projects" className="text-brand-600 hover:underline">
          ← Volver a proyectos
        </Link>
      </div>

      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{project.name}</h1>
          <p
            className={
              'text-sm mt-1 ' +
              (isOverdue(project.deadline)
                ? 'text-red-600 font-medium'
                : 'text-slate-500')
            }
          >
            Fecha límite: {formatDate(project.deadline)}
          </p>
        </div>

        {isOwner && (
          <div className="flex items-center gap-2">
            <Link
              to={`/projects/${project.id}/edit`}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100 transition"
            >
              Editar
            </Link>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-sm text-red-700 hover:bg-red-100 disabled:opacity-50 transition"
            >
              {isDeleting ? 'Eliminando…' : 'Eliminar'}
            </button>
          </div>
        )}
      </header>

      {project.description && (
        <section className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="font-semibold text-slate-800 mb-2">Descripción</h2>
          <p className="text-sm text-slate-700 whitespace-pre-wrap">
            {project.description}
          </p>
        </section>
      )}

      <TaskList projectId={project.id} members={project.members} />

      <MembersSection
        projectId={project.id}
        ownerId={project.owner_id}
        members={project.members}
        isOwner={isOwner}
        onChange={loadProject}
      />
    </div>
  );
}