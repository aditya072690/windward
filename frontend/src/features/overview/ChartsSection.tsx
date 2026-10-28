import { useQuery } from '@tanstack/react-query'
import { fetchDecisionForecast, fetchByHorizon, fetchByHour } from '../../lib/api'
import { useState, useCallback, useMemo, useEffect, type CSSProperties } from 'react'
import { drawMainChartSafe } from '../../lib/chart/drawMainSafe'
import { drawHorizonChart, drawHourBars } from '../../lib/chart/drawStats'
import { ErrorBoundary } from '../../components/ErrorBoundary'
import { ChartContainer } from '../../components/ChartContainer'
import {
  CUTOFFS,
  clampCutoffIndex,
  cutoffLabel,
  cutoffRatio,
  decisionDateOf,
  formatDayLong,
  formatDayShort,
  isIsoDate,
  pad2,
  type ControlsState,
} from '../../lib/controls'

const RANGE_START = '2026-01-01'
const RANGE_END = '2026-01-31'

type Props = {
  controls: ControlsState
  onChange: (patch: Partial<ControlsState>) => void
  dayBounds: { min: string; max: string }
  metaLoading: boolean
  metaError: unknown
}

function formatGwh(val: unknown) {
  if (typeof val !== 'number' || !Number.isFinite(val)) return '—'
  return val.toFixed(0)
}

function peakTimeOf(points: any[]): string | null {
  let max = -Infinity
  let best: any = null
  for (const p of points) {
    const v = p?.forecast_mw
    if (typeof v === 'number' && Number.isFinite(v) && v > max) {
      max = v
      best = p
    }
  }
  if (!best?.start_time) return null
  const d = new Date(best.start_time)
  if (Number.isNaN(d.getTime())) return null
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' })
}

export function ChartsSection({ controls, onChange, dayBounds, metaLoading, metaError }: Props) {
  const [hindsight, setHindsight] = useState(true)
  const [showMainTable, setShowMainTable] = useState(false)
  const [showHorizonTable, setShowHorizonTable] = useState(false)
  const [showBarsTable, setShowBarsTable] = useState(false)

  const cutoffIndex = clampCutoffIndex(controls.cutoffIndex)
  const cutoff = cutoffLabel(cutoffIndex)
  const view = controls.view
  const deliveryDate = controls.deliveryDate
  const decisionDate = decisionDateOf(deliveryDate)
  const latest = view === 'latest'

  const mainQuery = useQuery({
    queryKey: ['decision-forecast', decisionDate, cutoff, view],
    queryFn: () => fetchDecisionForecast(decisionDate, cutoff, view),
  })

  const horizonQuery = useQuery({
    queryKey: ['by-horizon', RANGE_START, RANGE_END, cutoff, view],
    queryFn: () => fetchByHorizon(RANGE_START, RANGE_END, cutoff, view),
  })

  const hourQuery = useQuery({
    queryKey: ['by-hour', RANGE_START, RANGE_END, cutoff, view],
    queryFn: () => fetchByHour(RANGE_START, RANGE_END, cutoff, view),
  })

  const points = useMemo(
    () => (Array.isArray(mainQuery.data?.points) ? mainQuery.data.points : []),
    [mainQuery.data],
  )
  const buckets = useMemo(
    () => (Array.isArray(horizonQuery.data?.buckets) ? horizonQuery.data.buckets : []),
    [horizonQuery.data],
  )
  const hours = useMemo(
    () => (Array.isArray(hourQuery.data?.hours) ? hourQuery.data.hours : []),
    [hourQuery.data],
  )

  const energyGwh = formatGwh(mainQuery.data?.summary?.energy_gwh)
  const peakTime = useMemo(() => peakTimeOf(points), [points])

  const drawMain = useCallback(
    (el: HTMLDivElement) => {
      drawMainChartSafe(el, points, hindsight, el.clientWidth || 320)
    },
    [points, hindsight],
  )

  const drawHorizon = useCallback(
    (el: HTMLDivElement) => {
      drawHorizonChart(el, buckets, el.clientWidth || 320)
    },
    [buckets],
  )

  const drawHours = useCallback(
    (el: HTMLDivElement) => {
      drawHourBars(el, hours, el.clientWidth || 320)
    },
    [hours],
  )

  return (
    <section className="section section-tight" id="charts" aria-labelledby="charts-title">
      <div className="container">
        <div className="section-head">
          <div>
            <h2 id="charts-title">Forecast vs actual</h2>
            <div className="section-sub" id="chart-sub">
              <span>Wind · {formatDayLong(deliveryDate)} · Europe/London</span>
            </div>
          </div>
        </div>

        <div className="stack-24">
          <div className="card controls">
            <div className="controls-row">
              <div className="control-block">
                <span className="control-label" id="series-label">
                  View
                </span>
                <div
                  className="segmented"
                  id="segmented"
                  role="radiogroup"
                  aria-labelledby="series-label"
                  style={{ '--seg-index': latest ? 1 : 0 } as CSSProperties}
                >
                  <span className="seg-thumb" id="seg-thumb" aria-hidden="true"></span>
                  <button
                    type="button"
                    role="radio"
                    aria-checked={!latest}
                    tabIndex={!latest ? 0 : -1}
                    onClick={() => onChange({ view: 'decision' })}
                  >
                    Decision-time
                  </button>
                  <button
                    type="button"
                    role="radio"
                    aria-checked={latest}
                    tabIndex={latest ? 0 : -1}
                    onClick={() => onChange({ view: 'latest' })}
                  >
                    Latest
                  </button>
                </div>
              </div>

              <DayControl
                deliveryDate={deliveryDate}
                decisionDate={decisionDate}
                bounds={dayBounds}
                metaLoading={metaLoading}
                metaError={metaError}
                onChange={(date) => onChange({ deliveryDate: date })}
              />
            </div>

            <div className={latest ? 'cutoff is-disabled' : 'cutoff'}>
              <div className="cutoff-head">
                <label htmlFor="cutoff">Cutoff</label>
                <span className="chip" aria-live="polite">
                  <span className="chip-dot" aria-hidden="true"></span>
                  <span id="vintage-chip">{cutoff} vintage</span>
                </span>
              </div>

              <div
                className="range-wrap"
                style={{ '--pct': String(cutoffRatio(cutoffIndex)) } as CSSProperties}
              >
                <div className="range-track" aria-hidden="true" />
                <div className="range-fill" aria-hidden="true" />
                <input
                  id="cutoff"
                  type="range"
                  min={0}
                  max={CUTOFFS.length - 1}
                  step={1}
                  value={cutoffIndex}
                  disabled={latest}
                  aria-valuetext={`${cutoff} vintage`}
                  aria-describedby="cutoff-help"
                  onChange={(e) => onChange({ cutoffIndex: clampCutoffIndex(Number(e.target.value)) })}
                />
              </div>

              <div className="ticks" aria-hidden="true">
                {CUTOFFS.map((hour, i) => (
                  <span
                    key={hour}
                    style={{
                      left: `calc(var(--thumb-pad) + ${cutoffRatio(i)} * (100% - 2 * var(--thumb-pad)))`,
                    }}
                  >
                    {pad2(hour)}
                  </span>
                ))}
              </div>

              <div className="help" id="cutoff-help">
                {latest ? (
                  <span>Latest vintages used; the cutoff is ignored.</span>
                ) : (
                  <span>
                    Using vintages published up to <span>{cutoff}</span> on {formatDayLong(decisionDate)} for{' '}
                    {formatDayLong(deliveryDate)}. Nothing published after the cutoff is used.
                  </span>
                )}
              </div>
            </div>
          </div>

          <figure className="card chart-card">
            <figcaption className="chart-head">
              <div>
                <h3 id="main-card-title">Wind · {formatDayLong(deliveryDate)}</h3>
                <div className="caption" id="main-card-sub">
                  <span>
                    48 half-hours · Europe/London · GW ·{' '}
                    {latest
                      ? 'latest vintages'
                      : `decided ${formatDayShort(decisionDate)} at ${cutoff}`}{' '}
                    · {energyGwh} GWh
                  </span>
                </div>
              </div>
              <div className="chart-tools">
                <ul className="legend">
                  <li>
                    <span className="sw sw-f" aria-hidden="true"></span>Forecast
                  </li>
                  <li>
                    <span className="sw sw-a" aria-hidden="true"></span>Actual
                  </li>
                  <li>
                    <span className="sw sw-c" aria-hidden="true"></span>Conservative
                  </li>
                  <li>
                    <span className="sw sw-e" aria-hidden="true"></span>Error
                  </li>
                </ul>
                <button
                  className="btn btn-ghost btn-compact"
                  type="button"
                  aria-pressed={showMainTable}
                  aria-controls="main-table"
                  onClick={() => setShowMainTable((v) => !v)}
                >
                  {showMainTable ? 'Hide table' : 'View as table'}
                </button>
                <button
                  className="btn btn-ghost btn-compact"
                  type="button"
                  id="hindsight-toggle"
                  aria-pressed={hindsight}
                  onClick={() => setHindsight((v) => !v)}
                >
                  {hindsight ? 'Hide actuals' : 'Show actuals'}
                </button>
              </div>
            </figcaption>
            <div className="chart-shell" data-shell="main">
              <ErrorBoundary fallback={undefined}>
                <ChartContainer
                  draw={drawMain}
                  isLoading={mainQuery.isLoading}
                  isError={mainQuery.isError}
                  error={mainQuery.error}
                  isEmpty={!mainQuery.isLoading && !mainQuery.isError && points.length === 0}
                  emptyMessage="No forecast data for this day and cutoff."
                  debugData={points}
                />
              </ErrorBoundary>
              <div className="tip" id="main-tip" hidden></div>
            </div>
            {showMainTable && (
              <div className="table-scroll tall" id="main-table" tabIndex={0} role="region" aria-label="Forecast and actual values, table view">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th scope="col">Time</th>
                      <th scope="col">Forecast (GW)</th>
                      <th scope="col">Actual (GW)</th>
                      <th scope="col">Error (MW)</th>
                      <th scope="col">Horizon (h)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {points.map((p: any) => (
                      <tr key={p?.start_time}>
                        <th scope="row">{formatSlot(p?.start_time)}</th>
                        <td>{gw(p?.forecast_mw)}</td>
                        <td>{gw(p?.actual_mw)}</td>
                        <td>{mw(p?.error_mw)}</td>
                        <td>{num(p?.horizon_h, 1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="chart-note">
              {peakTime ? <span>Peak forecast around {peakTime}</span> : <span aria-hidden="true">&nbsp;</span>}
            </div>
          </figure>

          <div className="grid-2">
            <figure className="card chart-card">
              <figcaption className="chart-head">
                <div>
                  <h3>Error by horizon</h3>
                  <div className="caption">
                    <span>
                      Absolute error percentiles by forecast age, all of January{' '}
                      {latest ? 'at latest vintages' : `at ${cutoff}`}, MW
                    </span>
                  </div>
                </div>
                <div className="chart-tools">
                  <button
                    className="btn btn-ghost btn-compact"
                    type="button"
                    aria-pressed={showHorizonTable}
                    aria-controls="horizon-table"
                    onClick={() => setShowHorizonTable((v) => !v)}
                  >
                    {showHorizonTable ? 'Hide table' : 'View as table'}
                  </button>
                </div>
              </figcaption>
              <div className="chart-shell" data-shell="horizon">
                <ChartContainer
                  draw={drawHorizon}
                  isLoading={horizonQuery.isLoading}
                  isError={horizonQuery.isError}
                  error={horizonQuery.error}
                  isEmpty={!horizonQuery.isLoading && !horizonQuery.isError && buckets.length === 0}
                  emptyMessage="No scored forecasts in January at this cutoff."
                  debugData={buckets}
                  minHeight={220}
                />
              </div>
              {showHorizonTable && (
                <div className="table-scroll" id="horizon-table" tabIndex={0} role="region" aria-label="Error by horizon, table view">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th scope="col">Forecast age (h)</th>
                        <th scope="col">p50 (MW)</th>
                        <th scope="col">p90 (MW)</th>
                        <th scope="col">p95 (MW)</th>
                        <th scope="col">n</th>
                      </tr>
                    </thead>
                    <tbody>
                      {buckets.map((b: any, i: number) => (
                        <tr key={b?.bucket ?? i}>
                          <th scope="row">{b?.bucket ?? '—'}</th>
                          <td>{mw(b?.p50)}</td>
                          <td>{mw(b?.p90)}</td>
                          <td>{mw(b?.p95)}</td>
                          <td>{num(b?.count, 0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="chart-note">
                <span>p50 / p90 / p95 of |forecast − actual|</span>
              </div>
            </figure>

            <figure className="card chart-card">
              <figcaption className="chart-head">
                <div>
                  <h3>Error by hour</h3>
                  <div className="caption">
                    <span>
                      Mean signed error by hour · all of January{' '}
                      {latest ? 'at latest vintages' : `at ${cutoff}`} · positive means forecast ran high
                    </span>
                  </div>
                </div>
                <div className="chart-tools">
                  <button
                    className="btn btn-ghost btn-compact"
                    type="button"
                    aria-pressed={showBarsTable}
                    aria-controls="bars-table"
                    onClick={() => setShowBarsTable((v) => !v)}
                  >
                    {showBarsTable ? 'Hide table' : 'View as table'}
                  </button>
                </div>
              </figcaption>
              <div className="chart-shell" data-shell="bars">
                <ChartContainer
                  draw={drawHours}
                  isLoading={hourQuery.isLoading}
                  isError={hourQuery.isError}
                  error={hourQuery.error}
                  isEmpty={!hourQuery.isLoading && !hourQuery.isError && hours.length === 0}
                  emptyMessage="No scored forecasts in January at this cutoff."
                  debugData={hours}
                  minHeight={220}
                />
              </div>
              {showBarsTable && (
                <div className="table-scroll" id="bars-table" tabIndex={0} role="region" aria-label="Error by hour, table view">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th scope="col">Hour (London)</th>
                        <th scope="col">Mean signed error (MW)</th>
                        <th scope="col">n</th>
                      </tr>
                    </thead>
                    <tbody>
                      {hours.map((h: any, i: number) => (
                        <tr key={typeof h?.hour === 'number' ? h.hour : i}>
                          <th scope="row">{String(h?.hour ?? i).padStart(2, '0')}:00</th>
                          <td>{signedMw(h?.mean_signed_error_mw)}</td>
                          <td>{num(h?.count, 0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="chart-note">
                <span>Signed error = forecast − actual</span>
              </div>
            </figure>
          </div>
        </div>
      </div>
    </section>
  )
}

function DayControl({
  deliveryDate,
  decisionDate,
  bounds,
  metaLoading,
  metaError,
  onChange,
}: {
  deliveryDate: string
  decisionDate: string
  bounds: { min: string; max: string }
  metaLoading: boolean
  metaError: unknown
  onChange: (date: string) => void
}) {
  const availableDays = useMemo(() => {
    if (!isIsoDate(bounds.min) || !isIsoDate(bounds.max)) return 0
    const ms = Date.parse(`${bounds.max}T00:00:00Z`) - Date.parse(`${bounds.min}T00:00:00Z`)
    return Math.round(ms / 86_400_000) + 1
  }, [bounds.min, bounds.max])

  useEffect(() => {
    if (!import.meta.env.DEV) return
    console.log('[DayControl]', {
      availableDays,
      bounds,
      selectedDeliveryDate: deliveryDate,
      selectedDecisionDate: decisionDate,
      loading: metaLoading,
      error: metaError ? String((metaError as Error)?.message ?? metaError) : null,
    })
  }, [availableDays, bounds, deliveryDate, decisionDate, metaLoading, metaError])

  return (
    <div className="control-block">
      <label className="control-label" htmlFor="day">
        Day
      </label>
      <div className="day-control">
        <input
          id="day"
          className="date-input"
          type="date"
          value={deliveryDate}
          min={bounds.min}
          max={bounds.max}
          aria-describedby="day-help"
          onChange={(e) => {
            const next = e.target.value
            if (!isIsoDate(next)) return
            if (next < bounds.min || next > bounds.max) return
            onChange(next)
          }}
        />
        <span className="day-hint" id="day-help">
          {formatDayShort(deliveryDate)} · delivery
        </span>
      </div>
      <span className="control-note">
        {metaLoading
          ? 'Loading dataset range…'
          : metaError
            ? `Dataset range unavailable — using ${bounds.min} to ${bounds.max}.`
            : `${availableDays} delivery days available`}
      </span>
    </div>
  )
}

function formatSlot(iso: unknown): string {
  if (typeof iso !== 'string') return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' })
}

function gw(v: unknown): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—'
  return (v / 1000).toFixed(2)
}

function mw(v: unknown): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—'
  return Math.round(v).toString()
}

function signedMw(v: unknown): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—'
  return `${v >= 0 ? '+' : ''}${Math.round(v)}`
}

function num(v: unknown, digits: number): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—'
  return v.toFixed(digits)
}
