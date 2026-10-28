const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export async function fetchMeta() {
  const res = await fetch(`${API_BASE}/meta`)
  if (!res.ok) throw new Error(`Failed to fetch meta (${res.status})`)
  return res.json()
}

export async function fetchDecisionForecast(
  decisionDate: string,
  cutoff: string,
  view: string = 'decision',
) {
  const res = await fetch(
    `${API_BASE}/decision-forecast?decision_date=${encodeURIComponent(decisionDate)}&cutoff=${encodeURIComponent(cutoff)}&view=${encodeURIComponent(view)}`,
  )
  if (!res.ok) throw new Error(`Failed to fetch decision forecast (${res.status})`)
  return res.json()
}

export async function fetchLedger(decisionDate: string, view: string = 'decision') {
  const res = await fetch(
    `${API_BASE}/accuracy/ledger?decision_date=${encodeURIComponent(decisionDate)}&view=${encodeURIComponent(view)}`,
  )
  if (!res.ok) throw new Error(`Failed to fetch ledger (${res.status})`)
  return res.json()
}

export async function fetchByHorizon(
  start: string,
  end: string,
  cutoff: string = '09:00',
  view: string = 'decision',
) {
  const res = await fetch(
    `${API_BASE}/accuracy/by-horizon?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&cutoff=${encodeURIComponent(cutoff)}&view=${encodeURIComponent(view)}`,
  )
  if (!res.ok) throw new Error(`Failed to fetch by-horizon (${res.status})`)
  return res.json()
}

export async function fetchByHour(
  start: string,
  end: string,
  cutoff: string = '09:00',
  view: string = 'decision',
) {
  const res = await fetch(
    `${API_BASE}/accuracy/by-hour?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&cutoff=${encodeURIComponent(cutoff)}&view=${encodeURIComponent(view)}`,
  )
  if (!res.ok) throw new Error(`Failed to fetch by-hour (${res.status})`)
  return res.json()
}
