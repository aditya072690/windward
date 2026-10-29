import { WindLines } from './WindLines'

export function Hero() {
  const openPilot = () => {
    document.getElementById('charts')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  const openMethodology = () => {
    const dialog = document.getElementById('methodology') as HTMLDialogElement | null
    dialog?.showModal()
  }

  return (
    <section className="hero" id="top" aria-labelledby="hero-title">
      <WindLines />
      <div className="container hero-inner">
        <p className="eyebrow">GB electricity · forecast accountability</p>
        <h1 id="hero-title">The forecast, held to account.</h1>
        <p className="lead">
          Every vintage, scored against what actually happened. Error by horizon, bias by hour, and the cost of being wrong — in one quiet view.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" type="button" onClick={openPilot}>
            Open the pilot
          </button>
          <button className="btn btn-ghost" type="button" onClick={openMethodology}>
            Read the methodology
          </button>
        </div>
        <ul className="hero-meta">
          <li>Aug–Oct 2026</li>
          <li>Europe/London</li>
          <li>Elexon BMRS</li>
        </ul>
      </div>
    </section>
  )
}
