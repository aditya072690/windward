export function OverviewSection() {
  return (
    <section className="section band" id="overview" aria-labelledby="overview-title">
      <div className="container">
        <div className="section-head">
          <div>
            <h2 id="overview-title">Today at a glance</h2>
            <p className="section-sub" id="overview-sub">
              Wind · Decision Thursday 15 January 2026 · delivery Friday 16 January · cutoff 09:00
            </p>
          </div>
          <span className="note">Elexon BMRS · data as of 31 Jan 2026</span>
        </div>

        <div className="metric-grid">
          <article className="metric">
            <p className="metric-label">Peak forecast</p>
            <p className="metric-value">
              <span id="kpi-peak">—</span>
              <span className="metric-unit">GW</span>
            </p>
            <p className="metric-delta" id="kpi-peak-delta">
              —
            </p>
            <p className="metric-hint" id="kpi-peak-hint">
              Peak at HH:MM
            </p>
          </article>
          <article className="metric">
            <p className="metric-label">Mean absolute error</p>
            <p className="metric-value">
              <span id="kpi-mae">—</span>
              <span className="metric-unit">MW</span>
            </p>
            <p className="metric-delta" id="kpi-mae-delta">
              —
            </p>
            <p className="metric-hint">Average miss per half-hour</p>
          </article>
          <article className="metric">
            <p className="metric-label">Bias</p>
            <p className="metric-value">
              <span id="kpi-bias">—</span>
              <span className="metric-unit">MW</span>
            </p>
            <p className="metric-delta" id="kpi-bias-delta">
              —
            </p>
            <p className="metric-hint">Positive means the forecast ran high</p>
          </article>
          <article className="metric">
            <p className="metric-label">Accuracy</p>
            <p className="metric-value">
              <span id="kpi-acc">—</span>
              <span className="metric-unit">%</span>
            </p>
            <p className="metric-delta" id="kpi-acc-delta">
              —
            </p>
            <p className="metric-hint">100 minus weighted absolute error</p>
          </article>
        </div>
      </div>
    </section>
  )
}
