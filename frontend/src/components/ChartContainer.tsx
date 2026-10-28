import { useEffect, useRef } from 'react'

type Props = {
  draw: (el: HTMLDivElement) => void
  isLoading?: boolean
  isError?: boolean
  error?: any
  isEmpty?: boolean
  emptyMessage?: string
  className?: string
  debugData?: any
  minHeight?: number
}

function assertChartData(data: any) {
  if (!import.meta.env.DEV) return
  try {
    if (!Array.isArray(data)) return
    console.log('chart input data: length=', data.length)
    if (data.length) console.log('chart first 3:', data.slice(0, 3))
    data.forEach((p: any, idx: number) => {
      const fx = p?.forecast_mw
      const ax = p?.actual_mw
      if (typeof fx === 'number' && !Number.isFinite(fx)) console.error('bad forecast_mw at', idx, p)
      if (typeof ax === 'number' && !Number.isFinite(ax)) console.error('bad actual_mw at', idx, p)
      if (p?.start_time && Number.isNaN(new Date(p.start_time).getTime())) {
        console.error('invalid start_time at', idx, p.start_time)
      }
    })
  } catch (e) {
    console.error('assertChartData error', e)
  }
}

/**
 * Owns a DOM node that React never renders children into.
 *
 * Why: React cannot reconcile DOM that was mutated outside of it. If the chart
 * host also held React-rendered children (e.g. "Loading…"), clearing it in the
 * draw effect left React with stale child Fibers, and the next commit threw
 * Safari's "NotFoundError: The object can not be found here" from
 * commitMutationEffects. Status messages therefore live in a sibling, and the
 * host is always childless from React's point of view.
 */
export function ChartContainer({
  draw,
  isLoading,
  isError,
  error,
  isEmpty,
  emptyMessage = 'No data',
  className,
  debugData,
  minHeight = 300,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = hostRef.current
    if (!el) return

    // The host is exclusively ours: clear whatever we drew last time.
    clearChildren(el)
    assertChartData(debugData)

    if (isLoading || isError || isEmpty) {
      return () => clearChildren(el)
    }

    try {
      draw(el)
    } catch (e) {
      console.error('ChartContainer draw error:', e)
      // Let the surrounding ErrorBoundary show a real message.
      throw e
    }

    return () => clearChildren(el)
  }, [draw, isLoading, isError, isEmpty, debugData])

  const status = isLoading
    ? 'Loading…'
    : isError
      ? `We couldn't load this view.${error?.message ? ` (${error.message})` : ''}`
      : isEmpty
        ? emptyMessage
        : null

  return (
    <div className={['chart-host-wrap', className].filter(Boolean).join(' ')}>
      {/* Ref-only: React never renders children in here. */}
      <div ref={hostRef} className="chart-host" style={{ minHeight }} aria-hidden={status ? true : undefined} />
      {status && <div className="empty chart-status">{status}</div>}
    </div>
  )
}

function clearChildren(el: Element) {
  // removeChild (not innerHTML) keeps Safari's live tree consistent.
  while (el.firstChild) el.removeChild(el.firstChild)
}
