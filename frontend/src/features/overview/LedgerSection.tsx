import { useQuery } from '@tanstack/react-query'
import { fetchLedger } from '../../lib/api'
import { ErrorBoundary } from '../../components/ErrorBoundary'
import {
  CUTOFFS,
  cutoffLabel,
  decisionDateOf,
  formatDayLong,
  formatDayShort,
  type ControlsState,
} from '../../lib/controls'

const nf0 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 })
const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)

function timeOf(iso: unknown): string | null {
  if (typeof iso !== 'string') return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' })
}

type Props = {
  controls: ControlsState
  onOpenCutoff: (cutoffIndex: number) => void
}

export function LedgerSection({ controls, onOpenCutoff }: Props) {
  const decisionDate = decisionDateOf(controls.deliveryDate)
  const view = controls.view
  const latest = view === 'latest'

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['ledger', decisionDate, view],
    queryFn: () => fetchLedger(decisionDate, view),
  })

  const rows = Array.isArray(data?.rows) ? data.rows : []
  const selectedCutoff = cutoffLabel(controls.cutoffIndex)

  return (
    <ErrorBoundary>
      <section className="section band" id="vintages" aria-labelledby="vintages-title">
        <div className="container">
          <div className="section-head">
            <div>
              <h2 id="vintages-title">Vintage ledger</h2>
              <div className="section-sub">
                <span>
                  {latest
                    ? `Latest vintages scored against ${formatDayLong(controls.deliveryDate)}.`
                    : `Eight cutoffs on ${formatDayLong(decisionDate)}, scored against ${formatDayLong(controls.deliveryDate)}. Open one to load it above.`}
                </span>
              </div>
            </div>
            <button
              className="btn btn-ghost btn-compact"
              type="button"
              onClick={() => refetch()}
              disabled={isFetching}
            >
              {isFetching ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>

          <div className="card vintage-card">
            <div className="table-scroll">
              <table className="data-table">
                <caption className="visually-hidden">
                  Forecast vintages for {formatDayShort(decisionDate)} scored against delivery{' '}
                  {formatDayShort(controls.deliveryDate)}, with mean absolute error, bias and peak
                  forecast.
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Vintage</th>
                    <th scope="col">Vintages used</th>
                    <th scope="col">MAE (MW)</th>
                    <th scope="col">Bias (MW)</th>
                    <th scope="col">Peak (GW)</th>
                    <th scope="col">
                      <span className="visually-hidden">Action</span>
                    </th>
                  </tr>
                </thead>
                <tbody id="vintage-body">
                  {isLoading && (
                    <tr>
                      <td colSpan={6}>Loading…</td>
                    </tr>
                  )}

                  {isError && (
                    <tr>
                      <td colSpan={6} role="alert">
                        Couldn't load the ledger.{error?.message ? ` (${error.message})` : ''}{' '}
                        <button className="btn btn-ghost btn-inline" type="button" onClick={() => refetch()}>
                          Retry
                        </button>
                      </td>
                    </tr>
                  )}

                  {!isLoading &&
                    !isError &&
                    rows.map((r: any, idx: number) => {
                      const min = timeOf(r?.vintage_min)
                      const max = timeOf(r?.vintage_max)
                      const peakGw = isNum(r?.peak_mw) ? r.peak_mw / 1000 : null
                      const rowCutoff: string = r?.cutoff ?? ''
                      const cutoffIndex = CUTOFFS.indexOf(
                        Number(rowCutoff.slice(0, 2)) as (typeof CUTOFFS)[number],
                      )
                      const isSelected = latest
                        ? rowCutoff === 'Latest'
                        : r?.cutoff === selectedCutoff
                      const vintagesUsed = isNum((r as any)?.vintages_used) ? (r as any).vintages_used : (min && max ? 1 : (r as any)?.count_vintages)
                      return (
                        <tr
                          key={r?.cutoff ?? `row-${idx}`}
                          className={isSelected ? 'is-selected' : undefined}
                        >
                          <th scope="row">{r?.cutoff ?? '—'}</th>
                          <td>{vintagesUsed != null ? vintagesUsed : '—'}</td>
                          <td>{isNum(r?.mae_mw) ? nf0.format(r.mae_mw) : '—'}</td>
                          <td>
                            {isNum(r?.bias_mw)
                              ? `${r.bias_mw >= 0 ? '+' : ''}${nf0.format(r.bias_mw)}`
                              : '—'}
                          </td>
                          <td>{peakGw != null ? peakGw.toFixed(1) : '—'}</td>
                          <td className="cell-action">
                            {latest ? (
                              <span className="control-note">In use</span>
                            ) : (
                              <button
                                className="btn btn-ghost btn-inline"
                                type="button"
                                aria-pressed={isSelected}
                                onClick={() => {
                                  if (cutoffIndex >= 0) onOpenCutoff(cutoffIndex)
                                  document
                                    .getElementById('charts')
                                    ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                                }}
                              >
                                {isSelected ? 'Shown' : 'Open'}
                              </button>
                            )}
                          </td>
                        </tr>
                      )
                    })}

                  {!isLoading && !isError && rows.length === 0 && (
                    <tr>
                      <td colSpan={6}>No data</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </ErrorBoundary>
  )
}
