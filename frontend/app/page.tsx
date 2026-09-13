const surfaces = [
  ["Mission control", "Create and supervise bounded work"],
  ["Policy state", "Decisions remain server-authoritative"],
  ["Evidence ledger", "Claims stay tied to source material"],
];

export default function Home() {
  return (
    <main className="shell">
      <aside className="rail">
        <div className="mark">V<span>O</span>ID</div>
        <nav aria-label="Primary navigation">
          <a className="active" href="#dashboard">Dashboard</a>
          <a href="#missions">Missions</a>
          <a href="#approvals">Approvals</a>
          <a href="#artifacts">Artifacts</a>
          <a href="#settings">Settings</a>
        </nav>
        <div className="rail-foot">LOCAL / V1<br /><span>CONTROL PLANE ONLINE</span></div>
      </aside>
      <section className="content" id="dashboard">
        <header className="topbar"><div><p className="eyebrow">VOID / OPERATIONS</p><h1>Mission control</h1></div><div className="health"><i /> API boundary healthy</div></header>
        <section className="command">
          <p className="eyebrow">UNIVERSAL COMMAND</p>
          <h2>What should VOID govern next?</h2>
          <p>Describe the outcome. Strategy, permissions, and execution remain under the control plane.</p>
          <div className="command-row"><input aria-label="Mission intent" placeholder="Compare a resume with a job description..." /><button type="button">New mission <span>↗</span></button></div>
        </section>
        <section className="overview"><div><p className="eyebrow">WORKSPACE</p><h2>Quiet systems. Traceable work.</h2><p className="muted">The first vertical slice is the Resume / JD intelligence workflow. No provider or external side effect is enabled by default.</p></div><div className="stat"><strong>0</strong><span>active missions</span></div><div className="stat"><strong>0</strong><span>pending approvals</span></div></section>
        <section className="surface-grid">{surfaces.map(([title, detail], index) => <article className="surface" key={title}><span className="index">0{index + 1}</span><h3>{title}</h3><p>{detail}</p><span className="status">AVAILABLE IN FOUNDATION</span></article>)}</section>
        <section className="empty"><span className="empty-line" /><div><p className="eyebrow">MISSION QUEUE</p><h2>No missions yet</h2><p className="muted">Create a mission to see its frozen execution profile, policy decisions, task graph, and evidence-backed artifacts here.</p></div></section>
      </section>
    </main>
  );
}