import { ThemeToggle } from './ThemeToggle'

export function NavBar() {
  const openMethodology = () => {
    const dialog = document.getElementById('methodology') as HTMLDialogElement | null
    dialog?.showModal()
  }

  return (
    <header className="nav">
      <div className="nav-inner">
        <a className="brand" href="#top" aria-label="Windward home">
          <svg
            className="od-icon brand-mark"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M3 8h11a3 3 0 1 0-3-3" />
            <path d="M3 12h15a3 3 0 1 1-3 3" />
            <path d="M3 16h8a2.5 2.5 0 1 1-2.5 2.5" />
          </svg>
          <span>Windward</span>
        </a>
        <nav className="nav-links" aria-label="Sections">
          <a href="#overview">Overview</a>
          <a href="#charts">Charts</a>
          <a href="#vintages">Vintages</a>
        </nav>
        <div className="nav-actions">
          <ThemeToggle />
          <button className="btn btn-secondary btn-compact" type="button" onClick={openMethodology}>
            Methodology
          </button>
        </div>
      </div>
    </header>
  )
}
