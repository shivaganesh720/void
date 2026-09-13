"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const PROJECT_ID = "00000000-0000-0000-0000-000000000001";

const surfaces = [
  ["Mission control", "Create and supervise bounded work"],
  ["Policy state", "Decisions remain server-authoritative"],
  ["Evidence ledger", "Claims stay tied to source material"],
];

type Mission = {
  id: string;
  status: string;
  task: { status: string };
  result?: {
    matching_skills: string[];
    missing_skills: string[];
    overall_match_explanation: string;
    warnings: string[];
  };
  error?: string;
};

export default function Home() {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [mission, setMission] = useState<Mission | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!mission || ["COMPLETED", "FAILED", "BLOCKED"].includes(mission.status)) return;
    const timer = window.setInterval(async () => {
      const response = await fetch(`${API_BASE}/api/v1/missions/${mission.id}`);
      if (response.ok) setMission(await response.json());
    }, 1000);
    return () => window.clearInterval(timer);
  }, [mission]);

  async function startMission() {
    setSubmitting(true);
    setError("");
    setMission(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/missions/resume-jd`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: PROJECT_ID, resume_text: resume, job_description: jobDescription }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail?.[0]?.msg ?? payload.detail ?? "Mission request failed");
      setMission(payload);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Mission request failed");
    } finally {
      setSubmitting(false);
    }
  }

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
          <div className="inputs"><textarea aria-label="Resume" value={resume} onChange={(event) => setResume(event.target.value)} placeholder="Paste resume text" /><textarea aria-label="Job description" value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} placeholder="Paste job description" /></div>
          <div className="command-row"><button type="button" onClick={startMission} disabled={submitting || !resume.trim() || !jobDescription.trim()}>{submitting ? "Starting..." : "Start analysis"} <span>↗</span></button></div>
          {error && <p className="error" role="alert">{error}</p>}
          {mission && <div className="mission-result"><p className="eyebrow">MISSION {mission.id}</p><p>Status: <strong>{mission.status}</strong> / Task: <strong>{mission.task.status}</strong></p>{mission.result && <><p>{mission.result.overall_match_explanation}</p><p>Matched: {mission.result.matching_skills.join(", ") || "None"}</p><p>Missing: {mission.result.missing_skills.join(", ") || "None"}</p><p className="muted">{mission.result.warnings.join(" ")}</p></>}{mission.error && <p className="error">{mission.error}</p>}</div>}
        </section>
        <section className="overview"><div><p className="eyebrow">WORKSPACE</p><h2>Quiet systems. Traceable work.</h2><p className="muted">The first vertical slice is the Resume / JD intelligence workflow. No provider or external side effect is enabled by default.</p></div><div className="stat"><strong>0</strong><span>active missions</span></div><div className="stat"><strong>0</strong><span>pending approvals</span></div></section>
        <section className="surface-grid">{surfaces.map(([title, detail], index) => <article className="surface" key={title}><span className="index">0{index + 1}</span><h3>{title}</h3><p>{detail}</p><span className="status">AVAILABLE IN FOUNDATION</span></article>)}</section>
        <section className="empty"><span className="empty-line" /><div><p className="eyebrow">MISSION QUEUE</p><h2>No missions yet</h2><p className="muted">Create a mission to see its frozen execution profile, policy decisions, task graph, and evidence-backed artifacts here.</p></div></section>
      </section>
    </main>
  );
}