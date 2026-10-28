import { SkipLink } from '../../components/ui/SkipLink'
import { LiveRegion } from '../../components/ui/LiveRegion'
import { NavBar } from '../../components/ui/NavBar'
import { Hero } from '../../components/ui/Hero'
import { OverviewSection } from './OverviewSection'
import { ChartsSection } from './ChartsSection'
import { LedgerSection } from './LedgerSection'
import { Footer } from '../../components/ui/Footer'
import { MethodologySheet } from '../../components/ui/MethodologySheet'

export function WindwardPage() {
  return (
    <>
      <SkipLink />
      <LiveRegion />
      <NavBar />
      <main id="main">
        <Hero />
        <OverviewSection />
        <ChartsSection />
        <LedgerSection />
      </main>
      <Footer />
      <MethodologySheet />
    </>
  )
}
