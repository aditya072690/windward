import { useQuery } from '@tanstack/react-query'
import { fetchDecisionForecast } from '../../lib/api'
import { useMemo } from 'react'
import { ErrorBoundary } from '../../components/ErrorBoundary'
import {
  cutoffLabel,
  decisionDateOf,
  formatDayLong,
  type ControlsState,
} from '../../lib/controls'
import { useMeta } from '../../lib/useMeta'

const nf0 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 })
const nf1 = new Intl.NumberFormat('en-GB', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)

function timeOf(iso: unknown): string | null {
  if (typeof iso !== 'string') return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' })
}

function peakOf(points: any[], key: 'forecast_mw' | 'actual_mw') {
  let best: any = null
  let max = -Infinity
  for (const p of points) {
    const v = p?.[key]
    if (isNum(v) && v > max) {
      max = v
      best = p
    }
  }
  return best ? { mw: max, time: timeOf(best.start_time) } : null
}

type Props = { controls: ControlsState }

export function OverviewSection({ controls }: Props) {
  const { meta, isLoading: metaLoading, isWarming } = useMeta()
  const decisionDate = decisionDateOf(controls.deliveryDate || '')
  const cutoff = cutoffLabel(controls.cutoffIndex)
  const view = controls.view
  const latest = view === 'latest'

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['decision-forecast', decisionDate, cutoff, view],
    queryFn: () => fetchDecisionForecast(decisionDate, cutoff, view),
    enabled: !!controls.deliveryDate && !metaLoading && !isWarming,
  })

  const summary = data?.summary ?? {}
  const points = useMemo(() => (Array.isArray(data?.points) ? data.points : []), [data])

  const peak = isNum(summary.peak_mw) ? summary.peak_mw : null
  const mae = isNum(summary.mae_mw) ? summary.mae_mw : null
  const bias = isNum(summary.bias_mw) ? summary.bias_mw : null
  const acc = isNum(summary.accuracy_pct) ? summary.accuracy_pct : null

  const forecastPeak = useMemo(() => peakOf(points, 'forecast_mw'), [points])
  const actualPeak = useMemo(() => peakOf(points, 'actual_mw'), [points])
  const peakTime = forecastPeak?.time ?? timeOf(summary.peak_time)
  const peakMissMw = forecastPeak && actualPeak ? Math.round(forecastPeak.mw - actualPeak.mw) : null

  return (
    <ErrorBoundary>
      <section className="section band" id="overview" aria-labelledby="overview-title">
        <div className="container">
          <div className="section-head">
            <div>
              <h2 id="overview-title">Today at a glance</h2>
              <div className="section-sub" id="overview-sub">
                <span>
                  Wind · {latest ? 'Latest vintages' : `Decision ${formatDayLong(decisionDate)}`} ·
                  delivery {controls.deliveryDate ? formatDayLong(controls.deliveryDate) : '—'}
                  {latest ? '' : controls.deliveryDate ? ` · cutoff ${cutoff}` : ''}
                </span>
              </div>
            </div>
            <span className="note">Elexon BMRS · data as of {meta?.data_as_of || ''}</span>
          </div>

          {isError && (
            <div className="empty" role="alert">
              Couldn't load the headline numbers.{error?.message ? ` (${error.message})` : ''}
            </div>
          )}

          <div className="metric-grid">
            <article className="metric">
              <p className="metric-label">Peak forecast</p>
              <p className="metric-value">
                <span id="kpi-peak">{peak != null ? nf1.format(peak / 1000) : isLoading ? '…' : '—'}</span>
                <span className="metric-unit">GW</span>
              </p>
              {peakMissMw != null && (
                <p className="metric-delta" id="kpi-peak-delta">
                  {peakMissMw >= 0 ? 'over' : 'under'} by {nf0.format(Math.abs(peakMissMw))} MW
                </p>
              )}
              <p className="metric-hint" id="kpi-peak-hint">
                {peakTime ? `Peak at ${peakTime}` : isLoading ? 'Loading…' : 'Peak time unavailable'}
              </p>
            </article>

            <article className="metric">
              <p className="metric-label">Mean absolute error</p>
              <p className="metric-value">
                <span id="kpi-mae">{mae != null ? nf0.format(mae) : isLoading ? '…' : '—'}</span>
                <span className="metric-unit">MW</span>
              </p>
              <p className="metric-hint">Average miss per half-hour</p>
            </article>

            <article className="metric">
              <p className="metric-label">Bias</p>
              <p className="metric-value">
                <span id="kpi-bias">
                  {bias != null ? (bias >= 0 ? '+' : '') + nf0.format(bias) : isLoading ? '…' : '—'}
                </span>
                <span className="metric-unit">MW</span>
              </p>
              {bias != null && (
                <p className="metric-delta" id="kpi-bias-delta">
                  {bias >= 0 ? 'ran high' : 'ran low'}
                </p>
              )}
              <p className="metric-hint">Positive means the forecast ran high</p>
            </article>

            <article className="metric">
              <p className="metric-label">Accuracy</p>
              <p className="metric-value">
                <span id="kpi-acc">{acc != null ? nf0.format(acc) : isLoading ? '…' : '—'}</span>
                <span className="metric-unit">%</span>
              </p>
              <p className="metric-hint">100 minus weighted absolute error</p>
            </article>
          </div>
        </div>
      </section>
    </ErrorBoundary>
  )
}
