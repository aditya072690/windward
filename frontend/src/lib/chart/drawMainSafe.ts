const NS = 'http://www.w3.org/2000/svg'

let uid = 0

function svgEl(tag: string, attrs: Record<string, unknown> = {}, parent?: Element | null) {
  const node = document.createElementNS(NS, tag)
  for (const k in attrs) {
    const v = attrs[k]
    if (v !== null && v !== undefined) node.setAttribute(k, String(v))
  }
  if (parent) parent.appendChild(node)
  return node
}

function clear(host: Element) {
  while (host.firstChild) host.removeChild(host.firstChild)
}

function isNum(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v)
}

function fmtInt(v: number) {
  return new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 }).format(v)
}

/** Handle 46/50-slot days (DST) and 48-slot days without assuming 48. */
export function drawMainChartSafe(host: HTMLElement, points: any[], hindsight: boolean, width: number) {
  clear(host)
  if (width < 80 || !Array.isArray(points) || points.length === 0) return

  const n = points.length
  const height = width < 620 ? 300 : 380
  const padL = 46
  const padR = 16
  const padT = 34
  const padB = 32
  const plotW = width - padL - padR
  const plotH = height - padT - padB
  if (plotW <= 10 || plotH <= 10) return

  // Source data is MW; the card is labelled GW, so scale once up front.
  const toGw = (v: number | null) => (isNum(v) ? v / 1000 : null)
  const forecast = points.map((p) => toGw(isNum(p?.forecast_mw) ? p.forecast_mw : null))
  const actual = points.map((p) => toGw(isNum(p?.actual_mw) ? p.actual_mw : null))
  const conservative = points.map((p, i) =>
    isNum(p?.conservative_mw)
      ? toGw(p.conservative_mw)
      : isNum(forecast[i])
        ? (forecast[i] as number) * 1.08
        : null,
  )

  const vals: number[] = []
  for (const arr of [forecast, actual, conservative]) {
    for (const v of arr) if (isNum(v)) vals.push(v)
  }
  if (vals.length === 0) return

  const rawMin = Math.min(...vals)
  const rawMax = Math.max(...vals)
  const span = Math.max(0.8, rawMax - rawMin)
  const step = span <= 6 ? 1 : span <= 12 ? 2 : span <= 26 ? 5 : 10
  const yMin = Math.max(0, Math.floor((rawMin - span * 0.15) / step) * step)
  let yMax = Math.ceil((rawMax + span * 0.1) / step) * step
  if (yMax - yMin < step * 2) yMax = yMin + step * 2
  const ySpan = yMax - yMin

  const xFor = (i: number) => padL + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW)
  const yFor = (v: number) => padT + (1 - (v - yMin) / ySpan) * plotH

  const svg = svgEl('svg', {
    class: 'chart-svg',
    viewBox: `0 0 ${width} ${height}`,
    width,
    height,
    role: 'img',
    'aria-label': 'Wind forecast versus actual generation for the delivery day',
  })
  host.appendChild(svg)

  const gid = `fc-grad-${++uid}`
  const defs = svgEl('defs', {}, svg)
  const grad = svgEl('linearGradient', { id: gid, x1: '0', y1: '0', x2: '0', y2: '1' }, defs)
  svgEl('stop', { offset: '0%', style: 'stop-color: var(--viz-forecast); stop-opacity: 0.12' }, grad)
  svgEl('stop', { offset: '100%', style: 'stop-color: var(--viz-forecast); stop-opacity: 0' }, grad)

  const grid = svgEl('g', { class: 'chart-grid' }, svg)
  for (let v = yMin; v <= yMax + 1e-6; v += step) {
    const y = yFor(v)
    svgEl('line', { x1: padL, x2: padL + plotW, y1: y, y2: y }, grid)
    const t = svgEl('text', { x: padL - 10, y: y + 4, 'text-anchor': 'end' }, grid)
    t.textContent = step < 1 ? v.toFixed(1) : fmtInt(v)
  }

  const unit = svgEl('text', { x: padL - 10, y: padT - 12, 'text-anchor': 'end', class: 'axis-unit' }, svg)
  unit.textContent = 'GW'

  // X labels every 6 hours, using actual local times from the data.
  const marks = width < 620 ? [0, 12, 24] : [0, 6, 12, 18, 24]
  for (const h of marks) {
    const idx = Math.min(n - 1, Math.round((h / 24) * n))
    if (idx < 0 || idx >= n) continue
    const t = svgEl(
      'text',
      {
        x: xFor(idx),
        y: height - 9,
        'text-anchor': idx === 0 ? 'start' : idx === n - 1 ? 'end' : 'middle',
      },
      svg,
    )
    t.textContent = localHourLabel(points[idx]?.start_time, h)
  }

  const pathFrom = (arr: (number | null)[]) => {
    let d = ''
    for (let i = 0; i < n; i++) {
      const v = arr[i]
      if (!isNum(v)) continue
      d += (d === '' ? 'M' : 'L') + xFor(i).toFixed(1) + ',' + yFor(v).toFixed(1)
    }
    return d
  }

  const forecastPath = pathFrom(forecast)
  if (forecastPath) {
    // Area under the forecast line.
    const area = forecastPath + `L${xFor(n - 1).toFixed(1)},${yFor(yMin).toFixed(1)}` + `L${xFor(0).toFixed(1)},${yFor(yMin).toFixed(1)}Z`
    svgEl('path', { d: area, fill: `url(#${gid})`, stroke: 'none' }, svg)
    svgEl('path', { d: forecastPath, class: 'series-forecast' }, svg)
  }

  const conservativePath = pathFrom(conservative)
  if (conservativePath) svgEl('path', { d: conservativePath, class: 'series-conservative', 'stroke-dasharray': '5 4' }, svg)

  if (hindsight) {
    const actualPath = pathFrom(actual)
    if (actualPath) {
      // Error band between forecast and actual, drawn behind the actual line.
      let band = ''
      let started = false
      for (let i = 0; i < n; i++) {
        if (!isNum(forecast[i]) || !isNum(actual[i])) continue
        band += (started ? 'L' : 'M') + xFor(i).toFixed(1) + ',' + yFor(forecast[i] as number).toFixed(1)
        started = true
      }
      if (started) {
        for (let i = n - 1; i >= 0; i--) {
          if (!isNum(forecast[i]) || !isNum(actual[i])) continue
          band += 'L' + xFor(i).toFixed(1) + ',' + yFor(actual[i] as number).toFixed(1)
        }
        svgEl('path', { d: band + 'Z', class: 'fill-error' }, svg)
      }
      svgEl('path', { d: actualPath, class: 'series-actual' }, svg)
    }
  }
}

function localHourLabel(iso: unknown, fallbackHour: number): string {
  if (typeof iso === 'string') {
    const d = new Date(iso)
    if (!Number.isNaN(d.getTime())) {
      return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' })
    }
  }
  return `${String(fallbackHour).padStart(2, '0')}:00`
}
