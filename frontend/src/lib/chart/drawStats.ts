const NS = 'http://www.w3.org/2000/svg'

function el(tag: string, attrs: Record<string, unknown> = {}, parent?: Element | null) {
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

function frame(host: HTMLElement, width: number, height = 220) {
  const svg = el('svg', {
    class: 'chart-svg',
    viewBox: `0 0 ${width} ${height}`,
    width,
    height,
    role: 'img',
  })
  host.appendChild(svg)
  return svg
}

/** p50/p90/p95 of |forecast − actual| grouped by forecast age. */
export function drawHorizonChart(host: HTMLElement, buckets: any[], width: number) {
  clear(host)
  if (width < 80 || !Array.isArray(buckets) || buckets.length === 0) return
  const height = 220
  const padL = 44
  const padR = 14
  const padT = 16
  const padB = 42
  const plotW = width - padL - padR
  const plotH = height - padT - padB
  if (plotW <= 10 || plotH <= 10) return

  const svg = frame(host, width, height)
  svg.setAttribute('aria-label', 'Absolute error percentiles by forecast age in hours')

  const maxV = Math.max(
    1,
    ...buckets.map((b) => (isNum(b?.p95) ? b.p95 : isNum(b?.p90) ? b.p90 : 0)),
  )
  const stepX = plotW / buckets.length
  const barW = Math.max(4, Math.min(28, stepX * 0.55))

  // Baseline + y ticks
  for (let i = 0; i <= 4; i++) {
    const v = (maxV / 4) * i
    const y = padT + plotH - (plotH * v) / maxV
    el('line', { x1: padL, x2: padL + plotW, y1: y, y2: y, class: 'grid-line' }, svg)
    const t = el('text', { x: padL - 8, y: y + 4, 'text-anchor': 'end', class: 'axis-text' }, svg)
    t.textContent = Math.round(v).toString()
  }

  buckets.forEach((b, i) => {
    const cx = padL + stepX * i + stepX / 2
    const p50 = isNum(b?.p50) ? b.p50 : 0
    const p90 = isNum(b?.p90) ? b.p90 : 0
    const p95 = isNum(b?.p95) ? b.p95 : 0
    const y95 = padT + plotH - (plotH * p95) / maxV
    const y90 = padT + plotH - (plotH * p90) / maxV
    const y50 = padT + plotH - (plotH * p50) / maxV

    // p90–p95 whisker
    el('line', { x1: cx, x2: cx, y1: y95, y2: y90, class: 'whisker' }, svg)
    el('line', { x1: cx - 3, x2: cx + 3, y1: y95, y2: y95, class: 'whisker' }, svg)
    // p50–p90 box
    el('rect', {
      x: cx - barW / 2,
      y: y90,
      width: barW,
      height: Math.max(1, y50 - y90),
      class: 'horizon-box',
      rx: 2,
    }, svg)

    if (i % 2 === 0 || buckets.length <= 8) {
      const t = el('text', { x: cx, y: height - 22, 'text-anchor': 'middle', class: 'axis-text' }, svg)
      t.textContent = b?.bucket ?? ''
    }
  })

  const unit = el('text', { x: padL - 8, y: padT - 4, 'text-anchor': 'end', class: 'axis-unit' }, svg)
  unit.textContent = 'MW'
  const axis = el('text', { x: padL + plotW / 2, y: height - 4, 'text-anchor': 'middle', class: 'axis-text' }, svg)
  axis.textContent = 'forecast age (h)'
}

/** Mean signed error by London hour of day. */
export function drawHourBars(host: HTMLElement, hours: any[], width: number) {
  clear(host)
  if (width < 80 || !Array.isArray(hours) || hours.length === 0) return
  const height = 220
  const padL = 44
  const padR = 14
  const padT = 16
  const padB = 42
  const plotW = width - padL - padR
  const plotH = height - padT - padB
  if (plotW <= 10 || plotH <= 10) return

  const svg = frame(host, width, height)
  svg.setAttribute('aria-label', 'Mean signed forecast error by hour of day, positive means forecast ran high')

  const values = hours.map((h) => (isNum(h?.mean_signed_error_mw) ? h.mean_signed_error_mw : 0))
  const maxAbs = Math.max(1, ...values.map((v) => Math.abs(v)))
  const zero = padT + plotH / 2
  const scale = (plotH / 2) / maxAbs
  const stepX = plotW / hours.length
  const barW = Math.max(3, Math.min(22, stepX * 0.62))

  el('line', { x1: padL, x2: padL + plotW, y1: zero, y2: zero, class: 'grid-line zero-line' }, svg)

  ;[-maxAbs, -maxAbs / 2, maxAbs / 2, maxAbs].forEach((v) => {
    const y = zero - v * scale
    el('line', { x1: padL, x2: padL + plotW, y1: y, y2: y, class: 'grid-line' }, svg)
    const t = el('text', { x: padL - 8, y: y + 4, 'text-anchor': 'end', class: 'axis-text' }, svg)
    t.textContent = Math.round(v).toString()
  })

  hours.forEach((h, i) => {
    const v = values[i]
    const cx = padL + stepX * i + stepX / 2
    const hgt = Math.max(1, Math.abs(v) * scale)
    const y = v >= 0 ? zero - hgt : zero
    el('rect', {
      x: cx - barW / 2,
      y,
      width: barW,
      height: hgt,
      class: v >= 0 ? 'hour-bar pos' : 'hour-bar neg',
      rx: 2,
    }, svg)
    if (i % 3 === 0) {
      const t = el('text', { x: cx, y: height - 22, 'text-anchor': 'middle', class: 'axis-text' }, svg)
      t.textContent = `${String(h?.hour ?? i).padStart(2, '0')}`
    }
  })

  const unit = el('text', { x: padL - 8, y: padT - 4, 'text-anchor': 'end', class: 'axis-unit' }, svg)
  unit.textContent = 'MW'
  const axis = el('text', { x: padL + plotW / 2, y: height - 4, 'text-anchor': 'middle', class: 'axis-text' }, svg)
  axis.textContent = 'hour (Europe/London)'
}
