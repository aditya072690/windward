export const CUTOFFS = [0, 3, 6, 9, 12, 15, 18, 21] as const

export type ViewMode = 'decision' | 'latest'

export type ControlsState = {
  view: ViewMode
  /** Delivery day shown in the DAY control, YYYY-MM-DD. */
  deliveryDate: string
  /** Index into CUTOFFS. The only stored representation of the cutoff. */
  cutoffIndex: number
}

export const DEFAULT_CONTROLS: ControlsState = {
  view: 'decision',
  deliveryDate: '',
  cutoffIndex: CUTOFFS.indexOf(9),
}

export const DEFAULT_DAY_BOUNDS = { min: '2026-08-29', max: '2026-10-28' }

export function pad2(n: number) {
  return String(n).padStart(2, '0')
}

/** "09:00" from an index into CUTOFFS. */
export function cutoffLabel(index: number): string {
  const safe = Math.min(Math.max(Math.trunc(index), 0), CUTOFFS.length - 1)
  return `${pad2(CUTOFFS[safe])}:00`
}

export function clampCutoffIndex(index: number): number {
  if (!Number.isFinite(index)) return DEFAULT_CONTROLS.cutoffIndex
  return Math.min(Math.max(Math.trunc(index), 0), CUTOFFS.length - 1)
}

/** Thumb position as a 0..1 ratio, shared by the fill and the tick labels. */
export function cutoffRatio(index: number): number {
  return clampCutoffIndex(index) / (CUTOFFS.length - 1)
}

function parseIsoDate(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(Date.UTC(y, (m || 1) - 1, d || 1, 12, 0, 0))
}

export function addDays(iso: string, days: number): string {
  const d = parseIsoDate(iso)
  d.setUTCDate(d.getUTCDate() + days)
  return d.toISOString().slice(0, 10)
}

/** Delivery day minus one. The API's decision_date. */
export function decisionDateOf(deliveryDate: string): string {
  return addDays(deliveryDate, -1)
}

/** Stable long day label (timezone independent). */
export function formatDayLong(iso: string): string {
  const d = parseIsoDate(iso)
  if (Number.isNaN(d.getTime())) return iso
  return new Intl.DateTimeFormat('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    timeZone: 'UTC',
  }).format(d)
}

/** "Fri 16 Jan" */
export function formatDayShort(iso: string): string {
  const d = parseIsoDate(iso)
  if (Number.isNaN(d.getTime())) return iso
  return new Intl.DateTimeFormat('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    timeZone: 'UTC',
  }).format(d)
}

/** True when the ISO string is a real YYYY-MM-DD date. */
export function isIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const d = parseIsoDate(value)
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === value
}
