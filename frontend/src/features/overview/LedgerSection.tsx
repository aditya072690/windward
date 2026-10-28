export function LedgerSection() {
  return (
    <section className="section band" id="vintages" aria-labelledby="vintages-title">
      <div className="container">
        <div className="section-head">
          <div>
            <h2 id="vintages-title">Vintage ledger</h2>
            <p className="section-sub">Eight cutoffs across the decision day, scored against the same delivery day. Open one to load it above.</p>
          </div>
        </div>
        <div className="card vintage-card">
          <div className="table-scroll">
            <table className="data-table">
              <caption className="visually-hidden">Forecast vintages for the selected decision day, with mean absolute error, bias and peak forecast.</caption>
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
              <tbody id="vintage-body"></tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}
