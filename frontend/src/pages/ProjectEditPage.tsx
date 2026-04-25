import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import ProjectForm from '@/components/ProjectForm';
import { extractApiError } from '@/lib/apiError';
import { projectService } from '@/services/projectService';
import type {
  Project,
  ProjectCreatePayload,
} from '@/types/project';

export default function ProjectEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const projectId = Number(id);

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (Number.isNaN(projectId)) {
      setError('ID de proyecto inválido');
      setIsLoading(false);
      return;
    }
    let active = true;
    projectService
      .get(projectId)
      .then((data) => {
        if (active) setProject(data);
      })
      .catch((err) => {
        if (active) setError(extractApiError(err, 'No se pudo cargar el proyecto'));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  async function handleSubmit(payload: ProjectCreatePayload) {
    setError(null);
    setIsSubmitting(true);
    try {
      await projectService.update(projectId, payload);
      navigate(`/projects/${projectId}`, { replace: true });
    } catch (err) {
      setError(extractApiError(err, 'No se pudo guardar el proyecto'));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-4 text-sm">
        <Link to={`/projects/${projectId}`} className="text-brand-600 hover:underline">
          ← Volver al proyecto
        </Link>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900 mb-1">
          Editar proyecto
        </h1>

        {error && (
          <div
            role="alert"
            className="mb-4 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-sm text-slate-500">Cargando…</div>
        ) : project ? (
          <ProjectForm
            initialValue={project}
            isSubmitting={isSubmitting}
            submitLabel="Guardar cambios"
            onSubmit={handleSubmit}
            onCancel={() => navigate(`/projects/${projectId}`)}
          />
        ) : null}
      </div>
    </div>
  );
}