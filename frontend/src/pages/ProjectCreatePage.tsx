import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import ProjectForm from '@/components/ProjectForm';
import { extractApiError } from '@/lib/apiError';
import { projectService } from '@/services/projectService';
import type { ProjectCreatePayload } from '@/types/project';

export default function ProjectCreatePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(payload: ProjectCreatePayload) {
    setError(null);
    setIsSubmitting(true);
    try {
      const created = await projectService.create(payload);
      navigate(`/projects/${created.id}`, { replace: true });
    } catch (err) {
      setError(extractApiError(err, 'No se pudo crear el proyecto'));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-4 text-sm">
        <Link to="/projects" className="text-brand-600 hover:underline">
          ← Volver a proyectos
        </Link>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900 mb-1">
          Nuevo proyecto
        </h1>
        <p className="text-sm text-slate-500 mb-5">
          Serás el propietario y miembro inicial del proyecto.
        </p>

        {error && (
          <div
            role="alert"
            className="mb-4 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        <ProjectForm
          isSubmitting={isSubmitting}
          submitLabel="Crear proyecto"
          onSubmit={handleSubmit}
          onCancel={() => navigate('/projects')}
        />
      </div>
    </div>
  );
}