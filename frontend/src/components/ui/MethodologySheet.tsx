export function MethodologySheet() {
  const close = () => {
    const dialog = document.getElementById('methodology') as HTMLDialogElement | null
    dialog?.close()
  }

  return (
    <dialog className="sheet" id="methodology" aria-labelledby="methodology-title">
      <div className="sheet-head">
        <h2 id="methodology-title">Methodology</h2>
        <button className="btn-icon" type="button" onClick={close} aria-label="Close methodology">
          <svg
            className="od-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="sheet-body">
        <h3>Decision cutoff and vintage selection</h3>
        <p>
          <strong>Cutoff</strong> is the moment on the decision date. For each delivery half-hour we select the forecast vintage with the greatest <code>publish_time ≤ cutoff</code> (inclusive). This is the latest forecast actually available at decision time.
        </p>
        <p>
          In <strong>Latest</strong> view, for each half-hour we use the greatest <code>publish_time ≤</code> that half-hour's start time (the last forecast published before it).
        </p>
        <h3>Error sign</h3>
        <p>
          <strong>Error = forecast − actual</strong> (MW). <strong>Positive = over-forecast</strong> (the costly direction for a buyer).
        </p>
        <h3>Time and missing data</h3>
        <p>
          Timestamps are stored in UTC and displayed in <strong>Europe/London</strong>. January 2026 has no DST transition. Half-hours with no forecast by the cutoff are reported as missing and excluded from metrics; coverage is reported.
        </p>
        <h3>Metrics</h3>
        <p>
          <strong>MAE</strong> averages absolute miss. <strong>Bias</strong> averages signed miss. <strong>Accuracy</strong> = max(0, 100 − nMAE×100) where nMAE = MAE / mean(actual) over scored half-hours (MAPE uses a floor for very small actuals as noted).
        </p>
        <h3>Risk-adjusted line (walk-forward)</h3>
        <p>
          The conservative line uses a walk-forward P90 of signed error by hour-of-day from strictly prior days (no look-ahead). It requires ≥ 3 prior days; if not available it is omitted with an explanation. This is a heuristic, not a guarantee.
        </p>
        <h3>Percentiles and horizons</h3>
        <p>
          <strong>Error by horizon</strong> is computed over the whole January window at the selected cutoff, bucketed in 3 h buckets up to 48 h, reporting P50/P90/P95 of |error| (MW). <strong>Error by hour</strong> reports mean signed error by London hour.
        </p>
        <h3>Data lineage</h3>
        <p>
          Data from <strong>Elexon BMRS</strong>: <code>FUELHH</code> (actual generation, filtered <code>fuelType = WIND</code>) and <code>WINDFOR</code> (wind forecast, with <code>publishTime</code>). Resolution 30 minutes. Served from a committed, validated SQLite snapshot opened read-only at runtime.
        </p>
        <div className="rule"></div>
        <p>Figures are historical (January 2026) — not an operational forecast.</p>
      </div>
    </dialog>
  )
}
