import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { extractApiError } from '@/lib/apiError';
import { formatDate, isOverdue } from '@/lib/formatters';
import { projectService } from '@/services/projectService';
import type { Project } from '@/types/project';

export default function ProjectsListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    projectService
      .list()
      .then((data) => {
        if (active) setProjects(data);
      })
      .catch((err) => {
        if (active) setError(extractApiError(err, 'No se pudieron cargar los proyectos'));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mis proyectos</h1>
          <p className="text-slate-600 mt-1 text-sm">
            Proyectos en los que participas como miembro o propietario.
          </p>
        </div>
        <Link
          to="/projects/new"
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 transition"
        >
          Nuevo proyecto
        </Link>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-sm text-slate-500">Cargando…</div>
      ) : projects.length === 0 ? (
        <div className="bg-white border border-dashed border-slate-300 rounded-lg p-10 text-center">
          <p className="text-slate-700 font-medium">Aún no tienes proyectos.</p>
          <p className="text-slate-500 text-sm mt-1">
            Crea tu primer proyecto para empezar a organizar tareas.
          </p>
          <Link
            to="/projects/new"
            className="inline-block mt-4 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 transition"
          >
            Crear proyecto
          </Link>
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <li key={project.id}>
              <Link
                to={`/projects/${project.id}`}
                className="block bg-white border border-slate-200 rounded-lg p-5 hover:border-brand-500 hover:shadow-sm transition"
              >
                <h2 className="font-semibold text-slate-900 truncate">
                  {project.name}
                </h2>
                <p className="text-sm text-slate-600 mt-1 line-clamp-2 min-h-[2.5rem]">
                  {project.description ?? 'Sin descripción'}
                </p>
                <p
                  className={
                    'text-xs mt-3 ' +
                    (isOverdue(project.deadline)
                      ? 'text-red-600 font-medium'
                      : 'text-slate-500')
                  }
                >
                  Fecha límite: {formatDate(project.deadline)}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}