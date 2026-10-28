export function hhmmToIndex(hhmm: string): number {
  const [h, m] = hhmm.split(':').map(Number)
  return h * 2 + (m >= 30 ? 1 : 0)
}

export function indexToHhmm(i: number): string {
  const h = Math.floor(i / 2)
  const m = i % 2 === 0 ? '00' : '30'
  return `${String(h).padStart(2, '0')}:${m}`
}
