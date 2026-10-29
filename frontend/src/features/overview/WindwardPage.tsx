import { useEffect, useMemo, useState } from 'react'
import { SkipLink } from '../../components/ui/SkipLink'
import { LiveRegion } from '../../components/ui/LiveRegion'
import { NavBar } from '../../components/ui/NavBar'
import { Hero } from '../../components/ui/Hero'
import { OverviewSection } from './OverviewSection'
import { ChartsSection } from './ChartsSection'
import { LedgerSection } from './LedgerSection'
import { Footer } from '../../components/ui/Footer'
import { MethodologySheet } from '../../components/ui/MethodologySheet'
import { DEFAULT_CONTROLS, DEFAULT_DAY_BOUNDS, addDays } from '../../lib/controls'
import { useMeta } from '../../lib/useMeta'

export function WindwardPage() {
  const { meta, isLoading: metaLoading, isError: metaError } = useMeta()
  // View, delivery day and cutoff live together so one change cannot drift
  // out of sync with the others.
  const [controls, setControls] = useState(DEFAULT_CONTROLS)

  const dayBounds = useMemo(() => {
    if (meta?.delivery_day_min && meta?.delivery_day_max) {
      return { min: meta.delivery_day_min, max: meta.delivery_day_max }
    }
    const win = meta?.decision_window
    if (Array.isArray(win) && win.length === 2 && win.every((d) => typeof d === 'string')) {
      // The API window is decision days; the DAY control shows delivery days.
      return { min: addDays(win[0], 1), max: addDays(win[1], 1) }
    }
    return DEFAULT_DAY_BOUNDS
  }, [meta])

  useEffect(() => {
    if (meta && (!controls.deliveryDate || controls.deliveryDate < dayBounds.min || controls.deliveryDate > dayBounds.max)) {
      setControls((c) => ({ ...c, deliveryDate: dayBounds.max }))
    }
  }, [meta, dayBounds.min, dayBounds.max])

  return (
    <>
      <SkipLink />
      <LiveRegion />
      <NavBar />
      <main id="main">
        <Hero />
        <OverviewSection controls={controls} />
        <ChartsSection
          controls={controls}
          onChange={(patch) => setControls((c) => ({ ...c, ...patch }))}
          dayBounds={dayBounds}
          metaLoading={metaLoading}
          metaError={metaError}
        />
        <LedgerSection
          controls={controls}
          onOpenCutoff={(cutoffIndex) =>
            setControls((c) => ({ ...c, view: 'decision', cutoffIndex }))
          }
        />
      </main>
      <Footer />
      <MethodologySheet />
    </>
  )
}
