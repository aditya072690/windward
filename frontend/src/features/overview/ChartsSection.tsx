export function ChartsSection() {
  return (
    <section className="section section-tight" id="charts" aria-labelledby="charts-title">
      <div className="container">
        <div className="section-head">
          <div>
            <h2 id="charts-title">Forecast vs actual</h2>
            <p className="section-sub" id="chart-sub">
              Wind · Friday 16 January · Europe/London
            </p>
          </div>
        </div>

        <div className="stack-24">
          <div className="card controls">
            <div className="controls-row">
              <div className="control-block">
                <span className="control-label" id="series-label">
                  View
                </span>
                <div className="segmented" id="segmented" role="radiogroup" aria-labelledby="series-label">
                  <span className="seg-thumb" id="seg-thumb" aria-hidden="true"></span>
                  <button type="button" role="radio" aria-checked="true" tabIndex={0}>
                    Decision-time
                  </button>
                  <button type="button" role="radio" aria-checked="false" tabIndex={-1}>
                    Latest
                  </button>
                </div>
              </div>
              <div className="control-block">
                <span className="control-label">Day</span>
                <div className="rail od-rail" id="date-rail" role="group" aria-label="Choose a decision date in January 2026"></div>
              </div>
            </div>

            <div className="cutoff">
              <div className="cutoff-head">
                <label htmlFor="cutoff">Cutoff</label>
                <span className="chip">
                  <span className="chip-dot" aria-hidden="true"></span>
                  <span id="vintage-chip">09:00 vintage</span>
                </span>
              </div>
              <input id="cutoff" type="range" min="0" max="47" step="1" defaultValue="18" aria-describedby="cutoff-help" />
              <div className="ticks" aria-hidden="true">
                <span>00</span>
                <span>03</span>
                <span>06</span>
                <span>09</span>
                <span>12</span>
                <span>15</span>
                <span>18</span>
                <span>21</span>
              </div>
              <p className="help" id="cutoff-help">
                Using vintages published <span id="cutoff-window">05:30 → 08:30</span> for Friday 16 January. Nothing published after the cutoff is used.
              </p>
            </div>
          </div>

          <figure className="card chart-card">
            <figcaption className="chart-head">
              <div>
                <h3 id="main-card-title">Wind · Friday 16 January</h3>
                <p className="caption" id="main-card-sub">
                  48 half-hours · Europe/London · GW · decided 15 Jan at 09:00 · 144 GWh
                </p>
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
                <button className="btn btn-ghost btn-compact" type="button" data-table-toggle="main" aria-pressed="false" aria-controls="main-table">
                  View as table
                </button>
                <button className="btn btn-ghost btn-compact" type="button" id="hindsight-toggle" aria-pressed="true">
                  Hide actuals
                </button>
              </div>
            </figcaption>
            <div className="chart-shell" data-shell="main">
              <div id="main-chart"></div>
              <div className="tip" id="main-tip" hidden></div>
            </div>
            <div className="table-scroll tall" id="main-table" data-table="main" tabIndex={0} role="region" aria-label="Forecast and actual values, table view" hidden></div>
            <p className="chart-note"></p>
          </figure>

          <div className="grid-2">
            <figure className="card chart-card">
              <figcaption className="chart-head">
                <div>
                  <h3>Error by horizon</h3>
                  <p className="caption">Absolute error percentiles by forecast age, all of January at this cutoff, MW</p>
                </div>
                <div className="chart-tools">
                  <button className="btn btn-ghost btn-compact" type="button" data-table-toggle="horizon" aria-pressed="false" aria-controls="horizon-table">
                    View as table
                  </button>
                </div>
              </figcaption>
              <div className="chart-shell" data-shell="horizon">
                <div id="horizon-chart"></div>
              </div>
              <div className="table-scroll" id="horizon-table" data-table="horizon" tabIndex={0} role="region" aria-label="Error by horizon, table view" hidden></div>
              <p className="chart-note"></p>
            </figure>

            <figure className="card chart-card">
              <figcaption className="chart-head">
                <div>
                  <h3>Error by hour</h3>
                  <p className="caption">Mean signed error by hour · all of January at this cutoff · positive means forecast ran high</p>
                </div>
                <div className="chart-tools">
                  <button className="btn btn-ghost btn-compact" type="button" data-table-toggle="bars" aria-pressed="false" aria-controls="bars-table">
                    View as table
                  </button>
                </div>
              </figcaption>
              <div className="chart-shell" data-shell="bars">
                <div id="bars-chart"></div>
              </div>
              <div className="table-scroll" id="bars-table" data-table="bars" tabIndex={0} role="region" aria-label="Error by hour, table view" hidden></div>
              <p className="chart-note"></p>
            </figure>
          </div>
        </div>
      </div>
    </section>
  )
}
