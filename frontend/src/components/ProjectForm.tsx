import { useState, type FormEvent } from 'react';

import type {
  Project,
  ProjectCreatePayload,
} from '@/types/project';

interface ProjectFormProps {
  /** When provided, the form is in "edit" mode and pre-fills values. */
  initialValue?: Project;
  isSubmitting: boolean;
  submitLabel: string;
  onSubmit: (payload: ProjectCreatePayload) => void;
  onCancel: () => void;
}

/**
 * Single source of truth for create + edit project forms.
 * Stays presentational: receives data in, emits a payload out.
 */
export default function ProjectForm({
  initialValue,
  isSubmitting,
  submitLabel,
  onSubmit,
  onCancel,
}: ProjectFormProps) {
  const [name, setName] = useState(initialValue?.name ?? '');
  const [description, setDescription] = useState(
    initialValue?.description ?? '',
  );
  const [deadline, setDeadline] = useState(initialValue?.deadline ?? '');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      deadline: deadline || null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-slate-700 mb-1"
        >
          Nombre <span className="text-red-500">*</span>
        </label>
        <input
          id="name"
          type="text"
          required
          maxLength={120}
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </div>

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-slate-700 mb-1"
        >
          Descripción
        </label>
        <textarea
          id="description"
          rows={3}
          maxLength={2000}
          value={description ?? ''}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </div>

      <div>
        <label
          htmlFor="deadline"
          className="block text-sm font-medium text-slate-700 mb-1"
        >
          Fecha límite
        </label>
        <input
          id="deadline"
          type="date"
          value={deadline ?? ''}
          onChange={(e) => setDeadline(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </div>

      <div className="flex items-center justify-end gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 disabled:opacity-50 transition"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting || !name.trim()}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {isSubmitting ? 'Guardando…' : submitLabel}
        </button>
      </div>
    </form>
  );
}