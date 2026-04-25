/**
 * Format an ISO date "YYYY-MM-DD" or full ISO datetime to a readable string.
 * Returns an em-dash for null/undefined to keep tables visually consistent.
 */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  // Treat date-only strings as local to avoid TZ-shift surprises.
  const date = value.length === 10 ? new Date(`${value}T00:00:00`) : new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/** True if the given ISO date is strictly in the past (today is fine). */
export function isOverdue(deadline: string | null | undefined): boolean {
  if (!deadline) return false;
  const date = new Date(`${deadline}T23:59:59`);
  return date.getTime() < Date.now();
}