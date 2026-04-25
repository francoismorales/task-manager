import { useEffect, useState, useCallback } from 'react';

import Modal from '@/components/Modal';
import TaskForm from '@/components/TaskForm';
import { extractApiError } from '@/lib/apiError';
import { taskService } from '@/services/taskService';
import type { ProjectMember } from '@/types/project';
import {
  TASK_PRIORITY_LABELS,
  TASK_STATUSES,
  TASK_STATUS_LABELS,
  type Task,
  type TaskCreatePayload,
  type TaskFilters,
  type TaskStatus,
  type TaskUpdatePayload,
} from '@/types/task';

interface TaskListProps {
  projectId: number;
  members: ProjectMember[];
}

const STATUS_BADGE_CLASS: Record<TaskStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
};

const PRIORITY_BADGE_CLASS = {
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-indigo-100 text-indigo-700',
  high: 'bg-red-100 text-red-700',
} as const;

export default function TaskList({ projectId, members }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<TaskStatus | 'all'>('all');

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const filters: TaskFilters = {};
      if (filterStatus !== 'all') filters.status = filterStatus;
      const data = await taskService.list(projectId, filters);
      setTasks(data);
    } catch (err) {
      setError(extractApiError(err, 'No se pudieron cargar las tareas'));
    } finally {
      setIsLoading(false);
    }
  }, [projectId, filterStatus]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  async function handleCreate(payload: TaskCreatePayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      await taskService.create(projectId, payload);
      setIsCreateOpen(false);
      await fetchTasks();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo crear la tarea'));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(payload: TaskUpdatePayload) {
    if (!editingTask) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await taskService.update(projectId, editingTask.id, payload);
      setEditingTask(null);
      await fetchTasks();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo actualizar la tarea'));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(task: Task) {
    const confirmed = window.confirm(
      `¿Eliminar la tarea "${task.title}"? Esta acción no se puede deshacer.`,
    );
    if (!confirmed) return;
    try {
      await taskService.remove(projectId, task.id);
      await fetchTasks();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo eliminar la tarea'));
    }
  }

  /** Quick-toggle status from the card without opening the modal. */
  async function handleStatusChange(task: Task, status: TaskStatus) {
    try {
      await taskService.update(projectId, task.id, { status });
      await fetchTasks();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo actualizar el estado'));
    }
  }

  return (
    <section className="bg-white border border-slate-200 rounded-lg p-5">
      <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
        <div>
          <h2 className="font-semibold text-slate-800">Tareas</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {tasks.length} {tasks.length === 1 ? 'tarea' : 'tareas'}
            {filterStatus !== 'all'
              ? ` filtradas por "${TASK_STATUS_LABELS[filterStatus]}"`
              : ''}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 transition"
        >
          Nueva tarea
        </button>
      </div>

      {/* Filtros por estado */}
      <div className="flex items-center gap-1 mb-4 border-b border-slate-200">
        {(['all', ...TASK_STATUSES] as const).map((value) => {
          const isActive = filterStatus === value;
          const label =
            value === 'all' ? 'Todas' : TASK_STATUS_LABELS[value];
          return (
            <button
              key={value}
              type="button"
              onClick={() => setFilterStatus(value)}
              className={
                'px-3 py-1.5 text-sm transition border-b-2 -mb-px ' +
                (isActive
                  ? 'border-brand-600 text-brand-700 font-medium'
                  : 'border-transparent text-slate-600 hover:text-slate-900')
              }
            >
              {label}
            </button>
          );
        })}
      </div>

      {error && (
        <div
          role="alert"
          className="mb-3 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-sm text-slate-500 py-6 text-center">Cargando…</div>
      ) : tasks.length === 0 ? (
        <div className="text-sm text-slate-500 py-6 text-center border border-dashed border-slate-300 rounded-md">
          {filterStatus === 'all'
            ? 'Aún no hay tareas. Crea la primera para empezar.'
            : 'Sin tareas en este estado.'}
        </div>
      ) : (
        <ul className="divide-y divide-slate-100">
          {tasks.map((task) => (
            <li key={task.id} className="py-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-slate-900 truncate">
                    {task.title}
                  </h3>
                  {task.description && (
                    <p className="text-sm text-slate-600 mt-0.5 line-clamp-2">
                      {task.description}
                    </p>
                  )}

                  <div className="flex items-center flex-wrap gap-2 mt-2">
                    <span
                      className={
                        'inline-block rounded-full px-2 py-0.5 text-xs font-medium ' +
                        STATUS_BADGE_CLASS[task.status]
                      }
                    >
                      {TASK_STATUS_LABELS[task.status]}
                    </span>
                    <span
                      className={
                        'inline-block rounded-full px-2 py-0.5 text-xs font-medium ' +
                        PRIORITY_BADGE_CLASS[task.priority]
                      }
                    >
                      Prioridad: {TASK_PRIORITY_LABELS[task.priority]}
                    </span>
                    {task.assignee ? (
                      <span className="text-xs text-slate-500">
                        Asignada a <strong>{task.assignee.full_name}</strong>
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400 italic">
                        Sin asignar
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  {/* Quick status change */}
                  <select
                    aria-label={`Cambiar estado de ${task.title}`}
                    value={task.status}
                    onChange={(e) =>
                      handleStatusChange(task, e.target.value as TaskStatus)
                    }
                    className="rounded-md border border-slate-300 px-2 py-1 text-xs focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  >
                    {TASK_STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {TASK_STATUS_LABELS[s]}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setEditingTask(task)}
                    className="rounded-md border border-slate-300 px-2 py-1 text-xs text-slate-700 hover:bg-slate-100 transition"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(task)}
                    className="rounded-md border border-red-200 bg-red-50 px-2 py-1 text-xs text-red-700 hover:bg-red-100 transition"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <Modal
        isOpen={isCreateOpen}
        onClose={() => !isSubmitting && setIsCreateOpen(false)}
        title="Nueva tarea"
      >
        <TaskForm
          members={members}
          isSubmitting={isSubmitting}
          submitLabel="Crear tarea"
          onSubmit={handleCreate}
          onCancel={() => setIsCreateOpen(false)}
        />
      </Modal>

      <Modal
        isOpen={editingTask !== null}
        onClose={() => !isSubmitting && setEditingTask(null)}
        title="Editar tarea"
      >
        {editingTask && (
          <TaskForm
            initialValue={editingTask}
            members={members}
            isSubmitting={isSubmitting}
            submitLabel="Guardar cambios"
            onSubmit={handleUpdate}
            onCancel={() => setEditingTask(null)}
          />
        )}
      </Modal>
    </section>
  );
}