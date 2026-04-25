import { useState, type FormEvent } from 'react';

import Modal from '@/components/Modal';
import { extractApiError } from '@/lib/apiError';
import { projectService } from '@/services/projectService';
import type { ProjectMember } from '@/types/project';

interface MembersSectionProps {
  projectId: number;
  ownerId: number;
  members: ProjectMember[];
  /** True if the current user is the project owner. Drives whether
   *  the invite/remove controls are shown. */
  isOwner: boolean;
  /** Called by the section when membership changes; the parent reloads
   *  the project so the rest of the page (e.g. the assignee dropdown in
   *  the task form) reflects the new member list. */
  onChange: () => void;
}

export default function MembersSection({
  projectId,
  ownerId,
  members,
  isOwner,
  onChange,
}: MembersSectionProps) {
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Track which member id is being removed to disable its button only
  const [removingId, setRemovingId] = useState<number | null>(null);

  async function handleInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await projectService.inviteMember(projectId, inviteEmail.trim());
      setInviteEmail('');
      setIsInviteOpen(false);
      onChange();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo invitar al miembro'));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRemove(member: ProjectMember) {
    const confirmed = window.confirm(
      `¿Quitar a ${member.user.full_name} del proyecto? ` +
        'Sus tareas asignadas quedarán sin asignar.',
    );
    if (!confirmed) return;

    setRemovingId(member.user.id);
    setError(null);
    try {
      await projectService.removeMember(projectId, member.user.id);
      onChange();
    } catch (err) {
      setError(extractApiError(err, 'No se pudo quitar al miembro'));
    } finally {
      setRemovingId(null);
    }
  }

  function closeInvite() {
    if (isSubmitting) return;
    setIsInviteOpen(false);
    setInviteEmail('');
    setError(null);
  }

  return (
    <section className="bg-white border border-slate-200 rounded-lg p-5">
      <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
        <h2 className="font-semibold text-slate-800">
          Miembros ({members.length})
        </h2>
        {isOwner && (
          <button
            type="button"
            onClick={() => setIsInviteOpen(true)}
            className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 transition"
          >
            Invitar miembro
          </button>
        )}
      </div>

      {error && (
        <div
          role="alert"
          className="mb-3 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      <ul className="divide-y divide-slate-100">
        {members.map((member) => {
          const isMemberOwner = member.user.id === ownerId;
          const showRemoveButton = isOwner && !isMemberOwner;

          return (
            <li
              key={member.id}
              className="py-2 flex items-center justify-between gap-3"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {member.user.full_name}
                </p>
                <p className="text-xs text-slate-500 truncate">
                  {member.user.email}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span
                  className={
                    'inline-block rounded-full px-2 py-0.5 text-xs font-medium ' +
                    (member.role === 'owner'
                      ? 'bg-brand-100 text-brand-700'
                      : 'bg-slate-100 text-slate-600')
                  }
                >
                  {member.role === 'owner' ? 'Propietario' : 'Miembro'}
                </span>
                {showRemoveButton && (
                  <button
                    type="button"
                    onClick={() => handleRemove(member)}
                    disabled={removingId === member.user.id}
                    className="rounded-md border border-red-200 bg-red-50 px-2 py-1 text-xs text-red-700 hover:bg-red-100 disabled:opacity-50 transition"
                  >
                    {removingId === member.user.id ? 'Quitando…' : 'Quitar'}
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ul>

      <Modal
        isOpen={isInviteOpen}
        onClose={closeInvite}
        title="Invitar miembro"
      >
        <form onSubmit={handleInvite} className="space-y-4">
          <p className="text-sm text-slate-600">
            Ingresa el correo de un usuario registrado. Se agregará como
            miembro del proyecto y podrá ver y gestionar tareas.
          </p>

          <div>
            <label
              htmlFor="invite_email"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Correo del miembro
            </label>
            <input
              id="invite_email"
              type="email"
              required
              autoFocus
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="usuario@example.com"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={closeInvite}
              disabled={isSubmitting}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 disabled:opacity-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !inviteEmail.trim()}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {isSubmitting ? 'Invitando…' : 'Invitar'}
            </button>
          </div>
        </form>
      </Modal>
    </section>
  );
}