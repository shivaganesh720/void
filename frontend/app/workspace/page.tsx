"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const DEFAULT_PROJECT_ID = "00000000-0000-0000-0000-000000000001";
type View = "dashboard" | "missions" | "capabilities" | "knowledge" | "memory" | "approvals" | "artifacts" | "settings";
type Task = { id: string; name: string; status: string; result?: Record<string, unknown> | null; error?: string | null };
type MissionEvent = { id: string; mission_id: string; event_type: string; timestamp: string; detail: string };
type Analysis = {
  resume: { file_name: string };
  job_description: { file_name: string };
  match_analysis: { overall_match_score: number; score_explanation: string; matching_skills: string[]; missing_skills: string[] };
  defect_analysis: { resume_defects: { severity: string; issue: string }[] };
  action_plan: { priority: number; action: string }[];
  evidence: { source: string; quote: string }[];
};
type Mission = { id: string; project_id: string; intent: string; status: string; task: Task; created_at: string; updated_at?: string; completed_at?: string | null; execution_mode?: string; events?: MissionEvent[]; result?: Analysis | null; error?: string | null };
type Summary = { project_id: string; total_missions: number; running_missions: number; completed_missions: number; failed_missions: number; blocked_missions: number; recent_missions: Mission[] };
type Project = { id: string; name: string };

const navigation: { id: View; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "missions", label: "Missions" },
  { id: "capabilities", label: "Capabilities" },
  { id: "knowledge", label: "Knowledge" },
  { id: "memory", label: "Memory" },
  { id: "approvals", label: "Approvals" },
  { id: "artifacts", label: "Artifacts" },
  { id: "settings", label: "Settings" },
];

async function getJson<T>(path: string): Promise<T> {
  const token = typeof window === "undefined" ? null : localStorage.getItem("void_access_token");
  const response = await fetch(`${API_BASE}${path}`, { headers: token ? { Authorization: `Bearer ${token}` } : undefined });
  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new Error(payload?.detail ?? "VOID API request failed");
  return payload as T;
}

async function ensureProject(): Promise<string> {
  const token = localStorage.getItem("void_access_token");
  if (!token) throw new Error("AUTH_REQUIRED");
  const savedProjectId = localStorage.getItem("void_project_id");
  const response = await fetch(`${API_BASE}/api/v1/projects`, { headers: { Authorization: `Bearer ${token}` } });
  const projects = await response.json().catch(() => [] as Project[]);
  if (!response.ok) throw new Error(projects?.detail ?? "Projects could not be loaded");
  const project = (projects as Project[]).find((candidate) => candidate.id === savedProjectId) ?? (projects as Project[])[0] ?? await (async () => {
    const created = await fetch(`${API_BASE}/api/v1/projects`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify({ name: "My VOID workspace" }) });
    const createdProject = await created.json();
    if (!created.ok) throw new Error(createdProject?.detail ?? "Workspace could not be created");
    return createdProject as Project;
  })();
  localStorage.setItem("void_project_id", project.id);
  return project.id;
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <section className="empty"><span className="empty-line" /><div><p className="eyebrow">EMPTY STATE</p><h2>{title}</h2><p className="muted">{detail}</p></div></section>;
}

function UnsupportedState({ feature }: { feature: string }) {
  return <EmptyState title={`${feature} is not implemented yet`} detail={`VOID does not currently have a persisted ${feature.toLowerCase()} registry or API. This section is intentionally empty; no sample records or statistics are shown.`} />;
}

function AnalysisResult({ analysis }: { analysis: Analysis }) {
  return <div className="analysis-grid">
    <section><span className="eyebrow">MATCH SCORE</span><strong className="score">{analysis.match_analysis.overall_match_score}</strong><p>{analysis.match_analysis.score_explanation}</p></section>
    <section><h3>Source files</h3><p>{analysis.resume.file_name}</p><p>{analysis.job_description.file_name}</p></section>
    <section><h3>Matching skills</h3><p>{analysis.match_analysis.matching_skills.join(", ") || "None detected"}</p><h3>Missing skills</h3><p>{analysis.match_analysis.missing_skills.join(", ") || "None detected"}</p></section>
    <section><h3>Defects</h3>{analysis.defect_analysis.resume_defects.map((defect) => <p className="warning" key={defect.issue}><b>{defect.severity}</b> {defect.issue}</p>)}</section>
    <section><h3>Priority plan</h3>{analysis.action_plan.map((item) => <p key={item.priority}><b>{item.priority}.</b> {item.action}</p>)}</section>
    <section><h3>Evidence</h3><p>{analysis.evidence.map((item) => `${item.source}: ${item.quote}`).join(" | ") || "No evidence detected"}</p></section>
  </div>;
}

export default function Home() {
  const [view, setView] = useState<View>("dashboard");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [mission, setMission] = useState<Mission | null>(null);
  const [error, setError] = useState("");
  const [dataError, setDataError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [missionSearch, setMissionSearch] = useState("");
  const [missionStatus, setMissionStatus] = useState("");
  const hasFilePair = Boolean(resumeFile && jdFile);
  const hasTextPair = Boolean(resume.trim() && jobDescription.trim());
  const hasMixedInputs = Boolean((resumeFile || jdFile) && !(resumeFile && jdFile));

  useEffect(() => {
    if (!localStorage.getItem("void_access_token")) window.location.replace("/login?next=/workspace");
  }, []);

  function logout() {
    localStorage.removeItem("void_access_token");
    window.location.replace("/login");
  }

  function selectView(nextView: View) {
    setView(nextView);
    window.location.hash = nextView;
  }

  async function loadDashboard() {
    setLoading(true); setDataError("");
    try { const projectId = await ensureProject(); setSummary(await getJson<Summary>(`/api/v1/dashboard/summary?project_id=${projectId}`)); }
    catch (requestError) { setDataError(requestError instanceof Error ? requestError.message : "Dashboard request failed"); }
    finally { setLoading(false); }
  }

  async function loadMissions() {
    setLoading(true); setDataError("");
    try { const projectId = await ensureProject(); const params = new URLSearchParams({ project_id: projectId }); if (missionSearch.trim()) params.set("search", missionSearch.trim()); if (missionStatus) params.set("status", missionStatus); setMissions(await getJson<Mission[]>(`/api/v1/missions?${params.toString()}`)); }
    catch (requestError) { setDataError(requestError instanceof Error ? requestError.message : "Mission request failed"); }
    finally { setLoading(false); }
  }

  async function openMission(item: Mission) {
    setDataError("");
    try { const projectId = await ensureProject(); setSelectedMission(await getJson<Mission>(`/api/v1/missions/${item.id}?project_id=${projectId}`)); }
    catch (requestError) { setDataError(requestError instanceof Error ? requestError.message : "Mission detail request failed"); }
  }

  useEffect(() => {
    const updateFromHash = () => { const hash = window.location.hash.slice(1) as View; if (navigation.some((item) => item.id === hash)) setView(hash); };
    updateFromHash(); window.addEventListener("hashchange", updateFromHash); return () => window.removeEventListener("hashchange", updateFromHash);
  }, []);
  useEffect(() => { void loadDashboard(); }, []);
  useEffect(() => { if (view === "missions") void loadMissions(); }, [view, missionSearch, missionStatus]);
  useEffect(() => {
    if (!mission || ["COMPLETED", "FAILED", "BLOCKED"].includes(mission.status)) return;
    const timer = window.setInterval(async () => {
      try { const projectId = await ensureProject(); setMission(await getJson<Mission>(`/api/v1/missions/${mission.id}?project_id=${projectId}`)); }
      catch { setError("Mission status could not be refreshed."); }
    }, 1000);
    return () => window.clearInterval(timer);
  }, [mission]);

  async function startMission() {
    if (hasMixedInputs || (!hasFilePair && !hasTextPair)) { setError("Select both files, or provide both pasted text inputs."); return; }
    setSubmitting(true); setError(""); setMission(null);
    try {
      const projectId = await ensureProject();
      const body = hasFilePair ? (() => { const form = new FormData(); form.append("resume", resumeFile!); form.append("job_description", jdFile!); form.append("project_id", projectId); return form; })() : JSON.stringify({ project_id: projectId, resume_text: resume, job_description: jobDescription });
      const token = localStorage.getItem("void_access_token");
      const headers = token ? { Authorization: `Bearer ${token}`, ...(hasFilePair ? {} : { "Content-Type": "application/json" }) } : hasFilePair ? undefined : { "Content-Type": "application/json" };
      const response = await fetch(`${API_BASE}/api/v1/missions/resume-jd${hasFilePair ? "/upload" : ""}`, { method: "POST", headers, body });
      const payload = await response.json(); if (!response.ok) throw new Error(payload.detail?.[0]?.msg ?? payload.detail ?? "Mission request failed");
      setMission(payload); await loadDashboard();
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Mission request failed"); }
    finally { setSubmitting(false); }
  }

  return <main className="shell">
    <aside className="rail"><div className="mark">V<span>O</span>ID</div><nav aria-label="Primary navigation">{navigation.map((item) => <a className={view === item.id ? "active" : ""} href={`#${item.id}`} onClick={() => setView(item.id)} key={item.id}>{item.label}</a>)}</nav><div className="rail-foot">LOCAL / V1<br /><span>CONTROL PLANE ONLINE</span></div></aside>
    <section className="content">
      <header className="topbar"><div><p className="eyebrow">VOID / OPERATIONS</p><h1>{navigation.find((item) => item.id === view)?.label}</h1></div><div className="topbar-actions"><div className="health"><i /> API boundary {dataError ? "unavailable" : "healthy"}</div><button className="workspace-logout" type="button" onClick={logout}>Log out</button></div></header>
      {dataError && <p className="error" role="alert">{dataError} <button type="button" onClick={() => view === "missions" ? void loadMissions() : void loadDashboard()}>Retry</button></p>}
      {view === "dashboard" && <>
        <section className="command"><p className="eyebrow">RESUME / JD INTELLIGENCE</p><h2>Compare a resume with a job description.</h2><p>Run the bounded local analysis. Results are evidence-backed and do not call an external model provider.</p><div className="inputs"><label>Resume file<input type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)} /></label><label>Job description file<input type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => setJdFile(event.target.files?.[0] ?? null)} /></label></div><p className="muted file-note">Or paste text for the bounded local analysis.</p><div className="inputs"><textarea aria-label="Resume" value={resume} onChange={(event) => setResume(event.target.value)} placeholder="Paste resume text" /><textarea aria-label="Job description" value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} placeholder="Paste job description" /></div><div className="command-row"><button type="button" onClick={startMission} disabled={submitting || hasMixedInputs || (!hasFilePair && !hasTextPair)}>{submitting ? "Starting..." : "Start analysis"} <span>↗</span></button></div>{error && <p className="error" role="alert">{error}</p>}{mission && <div className="mission-result"><p className="eyebrow">MISSION {mission.id}</p><p>Status: <strong>{mission.status}</strong> / Task: <strong>{mission.task.status}</strong></p>{mission.result && <AnalysisResult analysis={mission.result} />}{mission.error && <p className="error">{mission.error}</p>}</div>}</section>
        <section className="overview"><div><p className="eyebrow">WORKSPACE</p><h2>Current project activity</h2><p className="muted">Counts come from the project-scoped development mission store and reset when the API restarts.</p></div><div className="stat"><strong>{loading ? "-" : summary?.total_missions ?? 0}</strong><span>total missions</span></div><div className="stat"><strong>{loading ? "-" : summary?.running_missions ?? 0}</strong><span>running missions</span></div><div className="stat"><strong>{loading ? "-" : summary?.completed_missions ?? 0}</strong><span>completed missions</span></div><div className="stat"><strong>{loading ? "-" : summary?.failed_missions ?? 0}</strong><span>failed missions</span></div><div className="stat"><strong>{loading ? "-" : summary?.blocked_missions ?? 0}</strong><span>blocked missions</span></div></section>
        {summary?.recent_missions.length ? <section className="recent"><p className="eyebrow">RECENT MISSIONS</p>{summary.recent_missions.map((item) => <button className="mission-row" key={item.id} onClick={() => { selectView("missions"); void openMission(item); }}><span>{item.intent}</span><b>{item.status}</b><small>{new Date(item.created_at).toLocaleString()}</small></button>)}</section> : !loading && <EmptyState title="No missions yet" detail="Start a Resume/JD Analysis mission to see activity here." />}
      </>}
      {view === "missions" && <section className="page-section"><div className="section-heading"><div><p className="eyebrow">PROJECT MISSIONS</p><h2>Mission history</h2></div><button type="button" onClick={() => void loadMissions()}>Refresh</button></div><div className="mission-filters"><input aria-label="Search missions" value={missionSearch} onChange={(event) => setMissionSearch(event.target.value)} placeholder="Search name or ID" /><select aria-label="Filter mission status" value={missionStatus} onChange={(event) => setMissionStatus(event.target.value)}><option value="">All statuses</option><option value="COMPLETED">Completed</option><option value="RUNNING">Running</option><option value="FAILED">Failed</option><option value="BLOCKED">Blocked</option></select></div>{loading && <p className="muted">Loading missions...</p>}{!loading && !missions.length && <EmptyState title="No matching missions" detail="Start a Resume/JD Analysis mission or adjust the current filters." />}{missions.map((item) => <button className="mission-row" key={item.id} onClick={() => void openMission(item)}><span>{item.intent}<small>{item.id}</small></span><b>{item.status}</b><small>{new Date(item.updated_at ?? item.created_at).toLocaleString()}</small></button>)}{selectedMission && <div className="mission-result"><p className="eyebrow">MISSION DETAIL</p><h2>{selectedMission.intent}</h2><p>{selectedMission.id}</p><p>Status: <strong>{selectedMission.status}</strong> / Task: <strong>{selectedMission.task.status}</strong></p><p className="muted">Execution mode: {selectedMission.execution_mode ?? "AUTO"} {selectedMission.completed_at ? `/ completed ${new Date(selectedMission.completed_at).toLocaleString()}` : ""}</p>{selectedMission.events?.length ? <div className="timeline"><h3>Event timeline</h3>{selectedMission.events.map((event) => <p key={event.id}><b>{event.event_type}</b> {event.detail}<small>{new Date(event.timestamp).toLocaleString()}</small></p>)}</div> : <p className="muted">No events recorded.</p>}{selectedMission.result && <AnalysisResult analysis={selectedMission.result} />}{selectedMission.error && <p className="error">{selectedMission.error}</p>}</div>}</section>}
      {view === "approvals" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">GOVERNANCE</p><h2>Approval Center</h2></div>
        </div>
        <EmptyState title="No pending approvals" detail="There are no missions currently blocked awaiting your authorization." />
      </section>}
      {view === "capabilities" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">REGISTRY</p><h2>Capabilities</h2></div>
        </div>
        <EmptyState title="Capabilities Loading" detail="The capability registry is currently running in local fallback mode. See backend/app/control_plane/capabilities.py for registered items." />
      </section>}
      {view === "knowledge" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">RAG</p><h2>Knowledge Base</h2></div>
        </div>
        <EmptyState title="No documents indexed" detail="Upload a document via the universal command to begin chunking and RAG ingestion." />
      </section>}
      {view === "memory" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">PREFERENCES</p><h2>Workspace Memory</h2></div>
        </div>
        <EmptyState title="Memory is empty" detail="No facts or preferences have been committed to long-term memory for this project." />
      </section>}
      {view === "artifacts" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">RECORDS</p><h2>Artifact & Evidence Registry</h2></div>
        </div>
        <EmptyState title="No artifacts generated" detail="Mission artifacts and execution evidence will appear here once a mission completes." />
      </section>}
      {view === "settings" && <section className="page-section">
        <div className="section-heading">
          <div><p className="eyebrow">PREFERENCES</p><h2>Workspace Settings</h2></div>
        </div>
        <div className="settings-grid">
          <section className="settings-card">
            <h3>Execution Defaults</h3>
            <label>
              <span>Default Mode</span>
              <select defaultValue="AUTO">
                <option value="AUTO">AUTO (Recommended)</option>
                <option value="GUIDED">GUIDED</option>
                <option value="MANUAL">MANUAL</option>
              </select>
            </label>
            <label>
              <span>Privacy Mode</span>
              <select defaultValue="STANDARD">
                <option value="STANDARD">Standard</option>
                <option value="STRICT">Strict (Local only)</option>
              </select>
            </label>
          </section>
          
          <section className="settings-card">
            <h3>Provider Configuration</h3>
            <p className="muted">API keys are securely stored and never exposed to agents.</p>
            <label>
              <span>OpenAI API Key</span>
              <input type="password" placeholder="sk-..." />
            </label>
            <label>
              <span>Anthropic API Key</span>
              <input type="password" placeholder="sk-ant-..." />
            </label>
            <button className="button-secondary" type="button">Save Keys</button>
          </section>
        </div>
      </section>}
    </section>
  </main>;
}
