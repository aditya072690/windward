export function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <p>Contains data from Elexon BMRS. Figures are historical (January 2026) — not an operational forecast.</p>
          <p style={{ marginTop: 8 }}>Built on the Windward design system · v1</p>
        </div>
        <span className="brand" aria-hidden="true">
          <svg
            className="od-icon brand-mark"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 8h11a3 3 0 1 0-3-3" />
            <path d="M3 12h15a3 3 0 1 1-3 3" />
            <path d="M3 16h8a2.5 2.5 0 1 1-2.5 2.5" />
          </svg>
          Windward
        </span>
      </div>
    </footer>
  )
}
