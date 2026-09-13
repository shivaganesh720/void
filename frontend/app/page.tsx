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
    resume: { file_name: string; summary: string; candidate_profile: { skills: string[] } };
    job_description: { file_name: string; required_skills: string[]; keywords: string[] };
    match_analysis: { overall_match_score: number; score_explanation: string; matching_skills: string[]; missing_skills: string[]; matching_keywords: string[]; missing_keywords: string[] };
    defect_analysis: { resume_defects: { severity: string; issue: string; recommended_fix: string }[]; ats_defects: { issue: string }[] };
    improvement_analysis: { high_priority: string[]; medium_priority: string[]; recommended_skill_improvements: string[] };
    action_plan: { priority: number; action: string; reason: string; expected_benefit: string }[];
    evidence: { source: string; quote: string; label: string }[];
    limitations: string[];
    warnings: string[];
    matching_skills: string[];
    missing_skills: string[];
    overall_match_explanation: string;
  };
  error?: string;
};

export default function Home() {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
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
      const body = resumeFile && jdFile ? (() => { const form = new FormData(); form.append("resume", resumeFile); form.append("job_description", jdFile); return form; })() : JSON.stringify({ project_id: PROJECT_ID, resume_text: resume, job_description: jobDescription });
      const response = await fetch(`${API_BASE}/api/v1/missions/resume-jd${resumeFile && jdFile ? "/upload" : ""}`, { method: "POST", headers: resumeFile && jdFile ? undefined : { "Content-Type": "application/json" }, body });
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
          <div className="inputs"><label>Resume file<input type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)} /></label><label>Job description file<input type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => setJdFile(event.target.files?.[0] ?? null)} /></label></div>
          <p className="muted file-note">Or paste text for the bounded local analysis.</p><div className="inputs"><textarea aria-label="Resume" value={resume} onChange={(event) => setResume(event.target.value)} placeholder="Paste resume text" /><textarea aria-label="Job description" value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} placeholder="Paste job description" /></div>
          <div className="command-row"><button type="button" onClick={startMission} disabled={submitting || !resume.trim() || !jobDescription.trim()}>{submitting ? "Starting..." : "Start analysis"} <span>↗</span></button></div>
          {error && <p className="error" role="alert">{error}</p>}
          {mission && <div className="mission-result"><p className="eyebrow">MISSION {mission.id}</p><p>Status: <strong>{mission.status}</strong> / Task: <strong>{mission.task.status}</strong></p>{mission.result && <div className="analysis-grid"><section><span className="eyebrow">MATCH SCORE</span><strong className="score">{mission.result.match_analysis.overall_match_score}</strong><p>{mission.result.match_analysis.score_explanation}</p></section><section><h3>Source files</h3><p>{mission.result.resume.file_name}</p><p>{mission.result.job_description.file_name}</p></section><section><h3>Matching skills</h3><p>{mission.result.match_analysis.matching_skills.join(", ") || "None detected"}</p><h3>Missing skills</h3><p>{mission.result.match_analysis.missing_skills.join(", ") || "None detected"}</p></section><section><h3>Defects</h3>{mission.result.defect_analysis.resume_defects.map((defect) => <p className="warning" key={defect.issue}><b>{defect.severity}</b> {defect.issue}</p>)}</section><section><h3>Priority plan</h3>{mission.result.action_plan.map((item) => <p key={item.priority}><b>{item.priority}.</b> {item.action}</p>)}</section><section><h3>Evidence</h3><p>{mission.result.evidence.map((item) => `${item.source}: ${item.quote}`).join(" | ") || "No evidence detected"}</p></section></div>}{mission.error && <p className="error">{mission.error}</p>}</div>}
        </section>
        <section className="overview"><div><p className="eyebrow">WORKSPACE</p><h2>Quiet systems. Traceable work.</h2><p className="muted">The first vertical slice is the Resume / JD intelligence workflow. No provider or external side effect is enabled by default.</p></div><div className="stat"><strong>0</strong><span>active missions</span></div><div className="stat"><strong>0</strong><span>pending approvals</span></div></section>
        <section className="surface-grid">{surfaces.map(([title, detail], index) => <article className="surface" key={title}><span className="index">0{index + 1}</span><h3>{title}</h3><p>{detail}</p><span className="status">AVAILABLE IN FOUNDATION</span></article>)}</section>
        <section className="empty"><span className="empty-line" /><div><p className="eyebrow">MISSION QUEUE</p><h2>No missions yet</h2><p className="muted">Create a mission to see its frozen execution profile, policy decisions, task graph, and evidence-backed artifacts here.</p></div></section>
      </section>
    </main>
  );
}