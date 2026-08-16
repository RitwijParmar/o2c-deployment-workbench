const kpis = [
  { label: "Auto-match rate", baseline: "10.0%", future: "80.7%", delta: "+70.7 pp", met: true },
  { label: "Manual-review rate", baseline: "90.3%", future: "21.9%", delta: "−68.5 pp", met: true },
  { label: "Unapplied cash", baseline: "$2.19M", future: "$550K", delta: "−$1.64M", met: false },
  { label: "DSO", baseline: "115.9 d", future: "51.6 d", delta: "−64.3 d", met: false },
  { label: "CEI", baseline: "8.7%", future: "75.7%", delta: "+67.0 pp", met: false },
  { label: "Past-due AR", baseline: "69.5%", future: "44.9%", delta: "−24.6 pp", met: false },
  { label: "Processing time", baseline: "67.7 h", future: "13.0 h", delta: "−54.7 h", met: true },
];

const cases = [
  "Exact invoice payment", "Partial payment", "Overpayment", "One payment → many invoices",
  "Many payments → one invoice", "Missing remittance", "Cross-currency tolerance",
  "Duplicate payment", "Deduction short-pay", "Unmatched cash",
];

const deliverables = [
  "Current-state process", "Future-state workflow", "Source-to-target mapping", "Data-quality report",
  "KPI definition sheet", "Requirements traceability matrix", "28 UAT scenarios", "Cutover & rollback",
  "Go-live monitoring", "User training guide", "Five-minute demo", "Implementation workbook",
];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="O2C Deployment Workbench home">
          <span className="brand-mark">O2C</span>
          <span>Deployment Workbench</span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#benchmark">Benchmark</a>
          <a href="#architecture">Architecture</a>
          <a href="#delivery">Delivery</a>
        </nav>
        <a className="nav-cta" href="/O2C_Implementation_Workbook.xlsx">Download workbook</a>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">ERP receivables implementation simulation</p>
          <h1>Cash application is easy—until the payment stops matching the invoice.</h1>
          <p className="hero-lede">
            A production-minded O2C implementation workbench spanning three simulated ERP source styles,
            deterministic cash matching, collections, MCP, multi-agent exception operations, and end-to-end deployment controls.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#benchmark">Explore the benchmark</a>
            <a className="button secondary" href="/o2c_implementation_demo.mp4">Watch the five-minute demo</a>
          </div>
          <p className="synthetic-note">
            Synthetic ERP exports and controlled benchmark results only. No live customer data or claimed customer impact.
          </p>
        </div>
        <aside className="readiness-card" aria-label="Implementation readiness summary">
          <div className="readiness-topline"><span>Go-live decision</span><span className="status-dot" /></div>
          <strong>Conditional go</strong>
          <p>Core automation works. Four stretch KPIs remain in managed hypercare.</p>
          <dl>
            <div><dt>Canonical records</dt><dd>1,908</dd></div>
            <div><dt>Validation errors</dt><dd>0</dd></div>
            <div><dt>Routed warnings</dt><dd>18</dd></div>
            <div><dt>Agent trace errors</dt><dd>0</dd></div>
          </dl>
        </aside>
      </section>

      <section className="trust-strip" aria-label="Implementation scope">
        <span>SAP S/4HANA-style</span><span>Oracle Fusion-style</span><span>NetSuite-style</span>
        <span>7 canonical entities</span><span>28 UAT scenarios</span>
      </section>

      <section className="section" id="benchmark">
        <div className="section-heading">
          <div><p className="eyebrow">Controlled implementation benchmark</p><h2>Evidence before optimism.</h2></div>
          <p>The future-state workflow improves every required KPI while retaining missed targets instead of rewriting them after the run.</p>
        </div>
        <div className="kpi-grid">
          {kpis.map((kpi) => (
            <article className="kpi-card" key={kpi.label}>
              <div className="kpi-label"><span>{kpi.label}</span><span className={kpi.met ? "badge met" : "badge gap"}>{kpi.met ? "Target met" : "Gap"}</span></div>
              <div className="kpi-value">{kpi.future}</div>
              <div className="kpi-foot"><span>Baseline {kpi.baseline}</span><strong>{kpi.delta}</strong></div>
            </article>
          ))}
        </div>
      </section>

      <section className="section architecture" id="architecture">
        <div className="section-heading inverse">
          <div><p className="eyebrow">System design</p><h2>Deterministic money movement. Agentic judgment at the edges.</h2></div>
          <p>Agents investigate and recommend. They never post, refund, write off, or alter master data without human approval.</p>
        </div>
        <div className="flow" aria-label="O2C implementation architecture">
          <article><span>01</span><h3>Source onboarding</h3><p>Three mapping-driven synthetic ERP export adapters.</p></article>
          <article><span>02</span><h3>Control gate</h3><p>Required fields, keys, dates, currencies, amounts, and duplicates.</p></article>
          <article><span>03</span><h3>Cash matching</h3><p>References, remittance, tolerance, FX, partials, residuals, deductions.</p></article>
          <article><span>04</span><h3>Agent operations</h3><p>Supervisor handoffs to cash, data-quality, collections, and go-live specialists.</p></article>
          <article><span>05</span><h3>Human control</h3><p>Approval gate for every controlled financial action.</p></article>
        </div>
        <div className="protocol-grid">
          <div><small>MCP surface</small><strong>4 tools · 3 resources · 2 prompts</strong><p>Narrow evidence access over stdio or Streamable HTTP.</p></div>
          <div><small>Observability</small><strong>80 OpenTelemetry spans</strong><p>Pipeline, agent, tool, and handoff telemetry with content capture disabled.</p></div>
          <div><small>Evaluation</small><strong>Grounding · overrides · latency</strong><p>Precision and approval-bypass metrics designed into the operating model.</p></div>
        </div>
      </section>

      <section className="section cases">
        <div className="section-heading">
          <div><p className="eyebrow">Cash-application depth</p><h2>The cases analysts actually lose time on.</h2></div>
          <p>The workbench does not force ambiguity into an auto-match to improve the dashboard.</p>
        </div>
        <div className="case-grid">{cases.map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</div>)}</div>
      </section>

      <section className="section delivery" id="delivery">
        <div className="delivery-copy">
          <p className="eyebrow">Consulting-grade delivery</p>
          <h2>A deployable implementation pack—not a notebook with a nice chart.</h2>
          <p>Requirements, controls, UAT, cutover, monitoring, training, and operating evidence live beside the runnable system.</p>
          <div className="download-row">
            <a className="button primary" href="/O2C_Implementation_Workbook.xlsx">Implementation workbook</a>
            <a className="button secondary" href="/benchmark_summary.json">Benchmark JSON</a>
          </div>
        </div>
        <div className="deliverable-grid">{deliverables.map((item) => <div key={item}><span aria-hidden="true">✓</span>{item}</div>)}</div>
      </section>

      <footer>
        <div><strong>O2C Deployment Workbench</strong><p>Northstar Industrial Distribution (Synthetic) · Benchmark date 2026-07-31</p></div>
        <p>All vendor-style exports are simulations. KPI movement is a controlled implementation benchmark, not real customer impact.</p>
      </footer>
    </main>
  );
}
