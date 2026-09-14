"use client";

import { type ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity, AlertTriangle, Bot, Boxes, CheckCircle2, CircleDollarSign, Clock3, FileBox, FileSearch,
  GitBranch, KeyRound, Play, RefreshCw, ShieldCheck, Sparkles, SquareArrowOutUpRight, XCircle,
} from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { UniversalCommandPanel, type CommandOptions } from "../../components/ui/UniversalCommandPanel";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { api, ApiError } from "../../lib/api";
import type { Agent, Approval, Artifact, Capability, Evidence, Mission, ModelDescriptor, ProjectSummary, Workflow } from "../../types";

type View = "dashboard" | "missions" | "approvals" | "capabilities" | "models" | "tools" | "workflows" | "knowledge" | "memory" | "artifacts" | "evidence" | "evaluation" | "cost" | "privacy" | "integrations" | "admin" | "settings" | "help";

interface ControlPlaneData {
  summary: ProjectSummary | null;
  missions: Mission[];
  approvals: Approval[];
  capabilities: Capability[];
  agents: Agent[];
  models: ModelDescriptor[];
  tools: Record<string, unknown>[];
  workflows: Workflow[];
  artifacts: Artifact[];
  evidence: Evidence[];
}

const emptyData: ControlPlaneData = { summary: null, missions: [], approvals: [], capabilities: [], agents: [], models: [], tools: [], workflows: [], artifacts: [], evidence: [] };

const viewTitles: Record<View, [string, string]> = {
  dashboard: ["Mission control", "Create governed work and observe the control plane."],
  missions: ["Missions", "Search, inspect, and control project-scoped execution."],
  approvals: ["Approval center", "Review actions before governed execution continues."],
  capabilities: ["Capability registry", "Discover the capabilities available to this workspace."],
  models: ["Models & providers", "Availability is reported directly by the provider registry."],
  tools: ["Tool activity", "Only tools admitted through the central gateway appear here."],
  workflows: ["Workflows", "Saved workflow definitions and their current publishing state."],
  knowledge: ["Knowledge", "Project documents available for governed retrieval."],
  memory: ["Memory", "Approved workspace facts are kept separate from mission state."],
  artifacts: ["Artifacts", "Durable outputs created by completed mission runs."],
  evidence: ["Evidence", "Traceable sources and validation records for mission claims."],
  evaluation: ["Evaluations", "Mission validation results and quality signals."],
  cost: ["Usage & cost", "Persisted local-model usage and cost attribution."],
  privacy: ["Privacy", "Execution privacy choices and policy constraints."],
  integrations: ["Integrations", "Provider and companion connection health."],
  admin: ["Administration", "Administrative controls are shown only when authorized."],
  settings: ["Workspace settings", "Configure defaults that are enforced by the backend."],
  help: ["Help", "How governed mission execution works in VOID."],
};

export default function WorkspacePage() {
  const [view, setView] = useState<View>("dashboard");
  const [projectId, setProjectId] = useState<string>();
  const [data, setData] = useState<ControlPlaneData>(emptyData);
  const [selectedMission, setSelectedMission] = useState<Mission>();
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const id = projectId ?? await api.ensureProject();
      setProjectId(id);
      const [summary, missions, approvals, capabilities, agents, models, tools, workflows, artifacts, evidence] = await Promise.all([
        api.dashboard(id), api.missions(id), api.approvals(id), api.capabilities(), api.agents(), api.models(), api.tools(), api.workflows(), api.artifacts(id), api.evidence(id),
      ]);
      setData({ summary, missions, approvals, capabilities, agents, models, tools, workflows, artifacts, evidence });
      setError(undefined);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The VOID control plane is unavailable.");
    } finally { setLoading(false); }
  }, [projectId]);

  useEffect(() => { void load(); }, [load]);

  const createMission = async (prompt: string, options: CommandOptions) => {
    if (!projectId) return;
    try {
      setBusy(true); setError(undefined);
      const mission = await api.createMission(projectId, prompt, options.executionMode, options.modelMode, options.privacyMode);
      setSelectedMission(mission);
      setView("missions");
      await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Mission could not be created."); }
    finally { setBusy(false); }
  };

  const inspectMission = async (mission: Mission) => {
    if (!projectId) return;
    try { setSelectedMission(await api.mission(projectId, mission.id)); setView("missions"); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Mission details are unavailable."); }
  };

  const controlMission = async (mission: Mission, action: string) => {
    if (!projectId) return;
    try {
      setBusy(true);
      const updated = await api.controlMission(projectId, mission.id, action);
      setSelectedMission(updated); await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Mission action was rejected."); }
    finally { setBusy(false); }
  };

  const decideApproval = async (approval: Approval, decision: "APPROVED" | "REJECTED") => {
    if (!projectId) return;
    try { setBusy(true); await api.decideApproval(projectId, approval, decision); await load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Approval decision was rejected."); }
    finally { setBusy(false); }
  };

  const content = () => {
    if (loading && !data.summary) return <LoadingState />;
    switch (view) {
      case "dashboard": return <Dashboard data={data} onCreate={createMission} busy={busy} onInspect={inspectMission} />;
      case "missions": return <MissionsView missions={data.missions} selected={selectedMission} onInspect={inspectMission} onControl={controlMission} busy={busy} />;
      case "approvals": return <ApprovalsView approvals={data.approvals} onDecide={decideApproval} onInspect={(id) => { const mission = data.missions.find((entry) => entry.id === id); if (mission) void inspectMission(mission); }} busy={busy} />;
      case "capabilities": return <CapabilitiesView capabilities={data.capabilities} />;
      case "models": return <ModelsView models={data.models} />;
      case "tools": return <ToolsView tools={data.tools} />;
      case "workflows": return <WorkflowsView workflows={data.workflows} />;
      case "artifacts": return <ArtifactsView artifacts={data.artifacts} />;
      case "evidence": return <EvidenceView evidence={data.evidence} />;
      case "evaluation": return <EvaluationView missions={data.missions} />;
      case "cost": return <CostView missions={data.missions} />;
      case "privacy": return <PrivacyView missions={data.missions} />;
      case "integrations": return <IntegrationView models={data.models} />;
      case "knowledge":
      case "memory": return <EmptyData title={view === "knowledge" ? "No knowledge documents yet" : "No approved memories yet"} detail={view === "knowledge" ? "Ingest a project document to make it available to retrieval-aware missions." : "Approved preferences and facts will appear here; mission execution state stays in Mission Control."} />;
      case "admin": return <EmptyData title="Administrative access required" detail="This section is intentionally hidden behind a backend role check. Sign in with an administrator account to inspect users, policies, and system health." icon={<KeyRound />} />;
      case "settings": return <SettingsView />;
      case "help": return <HelpView />;
    }
  };

  const [title, subtitle] = viewTitles[view];
  return (
    <AppShell currentView={view} onNavigate={(next) => setView(next as View)}>
      <main className="control-plane">
        <header className="page-header">
          <div><p className="eyebrow">WORKSPACE / {view.toUpperCase()}</p><h1>{title}</h1><p className="text-muted">{subtitle}</p></div>
          <button className="button-secondary page-refresh" onClick={() => void load()} disabled={loading}><RefreshCw size={15} className={loading ? "spin" : ""} /> Refresh</button>
        </header>
        {error && <ErrorState error={error} onRetry={() => void load()} />}
        {content()}
      </main>
    </AppShell>
  );
}

function Dashboard({ data, onCreate, busy, onInspect }: { data: ControlPlaneData; onCreate: (prompt: string, options: CommandOptions) => void; busy: boolean; onInspect: (mission: Mission) => void }) {
  const summary = data.summary;
  const approvalCount = data.approvals.filter((approval) => approval.status === "PENDING").length;
  return <div className="section-stack">
    <UniversalCommandPanel onExecute={onCreate} isExecuting={busy} />
    <section className="metric-grid" aria-label="Mission metrics">
      <Metric icon={<Boxes />} label="Total missions" value={summary?.total_missions ?? 0} />
      <Metric icon={<Play />} label="Running" value={summary?.running_missions ?? 0} tone="info" />
      <Metric icon={<CheckCircle2 />} label="Completed" value={summary?.completed_missions ?? 0} tone="success" />
      <Metric icon={<ShieldCheck />} label="Needs approval" value={approvalCount} tone="warning" />
    </section>
    <section className="content-card">
      <div className="card-header"><div><h2>Recent mission activity</h2><p>Latest persisted work in this project.</p></div><StatusBadge value={data.models.some((model) => model.availability === "AVAILABLE") ? "AVAILABLE" : "UNAVAILABLE"}>Provider registry</StatusBadge></div>
      {summary?.recent_missions.length ? <MissionTable missions={summary.recent_missions} onInspect={onInspect} /> : <EmptyData compact title="No missions yet" detail="Create a mission above to start the governed execution trail." />}
    </section>
  </div>;
}

function MissionsView({ missions, selected, onInspect, onControl, busy }: { missions: Mission[]; selected?: Mission; onInspect: (mission: Mission) => void; onControl: (mission: Mission, action: string) => void; busy: boolean }) {
  const [search, setSearch] = useState("");
  const filtered = useMemo(() => missions.filter((mission) => mission.intent.toLowerCase().includes(search.toLowerCase())), [missions, search]);
  return <div className="section-stack">
    <section className="content-card mission-toolbar"><label><span className="sr-only">Search missions</span><input className="void-input" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search mission objective" /></label><span className="text-muted">{filtered.length} mission{filtered.length === 1 ? "" : "s"}</span></section>
    <section className="content-card">{filtered.length ? <MissionTable missions={filtered} onInspect={onInspect} /> : <EmptyData compact title="No missions match this filter" detail="Try a different objective or create a new governed mission." />}</section>
    {selected && <MissionDetail mission={selected} onControl={onControl} busy={busy} />}
  </div>;
}

function MissionTable({ missions, onInspect }: { missions: Mission[]; onInspect: (mission: Mission) => void }) {
  return <div className="table-wrap"><table className="void-table"><thead><tr><th>Objective</th><th>Status</th><th>Mode</th><th>Task</th><th>Updated</th><th aria-label="Open" /></tr></thead><tbody>{missions.map((mission) => <tr key={mission.id}><td><strong>{mission.intent}</strong><span className="table-meta">{mission.id.slice(0, 8)}</span></td><td><StatusBadge value={mission.status} /></td><td>{mission.execution_mode}</td><td><StatusBadge value={mission.task.status} /></td><td>{formatDate(mission.updated_at ?? mission.created_at)}</td><td><button className="button-secondary icon-button" onClick={() => onInspect(mission)} aria-label={`Open ${mission.intent}`}><SquareArrowOutUpRight size={15} /></button></td></tr>)}</tbody></table></div>;
}

function MissionDetail({ mission, onControl, busy }: { mission: Mission; onControl: (mission: Mission, action: string) => void; busy: boolean }) {
  const [tab, setTab] = useState("overview");
  const blueprint = mission.result?.strategy ?? (mission as unknown as { metadata_json?: { blueprint?: unknown } }).metadata_json?.blueprint;
  const tabs = ["overview", "plan", "execution", "policy", "approvals", "evidence", "logs"];
  const actions = mission.status === "RUNNING" ? ["pause", "cancel"] : mission.status === "PAUSED" ? ["resume", "cancel"] : mission.status === "WAITING_FOR_APPROVAL" ? ["cancel"] : [];
  return <section className="content-card mission-detail"><div className="card-header"><div><p className="eyebrow">MISSION {mission.id.slice(0, 8)}</p><h2>{mission.intent}</h2></div><div className="inline-actions"><StatusBadge value={mission.status} />{actions.map((action) => <button key={action} className={action === "cancel" ? "button-secondary danger-action" : "button-secondary"} onClick={() => onControl(mission, action)} disabled={busy}>{action}</button>)}</div></div>
    <nav className="detail-tabs" aria-label="Mission detail tabs">{tabs.map((entry) => <button key={entry} className={tab === entry ? "active" : ""} onClick={() => setTab(entry)}>{entry}</button>)}</nav>
    {tab === "overview" && <div className="detail-grid"><Detail label="Execution mode" value={mission.execution_mode} /><Detail label="Task status" value={mission.task.status} /><Detail label="Created" value={formatDate(mission.created_at)} /><Detail label="Approval" value={mission.approval_required ? "Required" : "Not required"} />{mission.error && <Detail label="Error" value={mission.error} />}{mission.result?.summary && <div className="detail-full"><p className="eyebrow">VALIDATED OUTPUT</p><p>{String(mission.result.summary)}</p></div>}</div>}
    {tab === "plan" && <JsonPanel value={blueprint ?? { message: "The persisted blueprint is available after mission planning." }} />}
    {tab === "execution" && <JsonPanel value={mission.result ?? { task: mission.task, status: mission.status }} />}
    {tab === "policy" && <JsonPanel value={{ approval_required: mission.approval_required, execution_profile: mission.execution_profile ?? {}, status: mission.status }} />}
    {tab === "approvals" && <ApprovalList approvals={mission.approvals ?? []} />}
    {tab === "evidence" && <EmptyData compact title="Evidence is linked to the mission artifact trail" detail="Open the Evidence section to inspect project-wide records." />}
    {tab === "logs" && <Timeline events={mission.events ?? []} />}
  </section>;
}

function ApprovalsView({ approvals, onDecide, onInspect, busy }: { approvals: Approval[]; onDecide: (approval: Approval, decision: "APPROVED" | "REJECTED") => void; onInspect: (missionId: string) => void; busy: boolean }) {
  return <section className="content-card"><div className="card-header"><div><h2>Pending and decision history</h2><p>Approval does not bypass a second policy check during execution.</p></div><StatusBadge value={`${approvals.filter((entry) => entry.status === "PENDING").length} PENDING`}>Pending</StatusBadge></div>{approvals.length ? <div className="approval-list">{approvals.map((approval) => <article className="approval-card" key={approval.id}><div><StatusBadge value={approval.status} /><h3>{approval.requested_action}</h3><p>{approval.risk_reason}</p><span className="table-meta">Requested {formatDate(approval.requested_at)}</span></div><div className="approval-actions"><button className="button-secondary" onClick={() => onInspect(approval.mission_id)}>Open mission</button>{approval.status === "PENDING" && <><button className="button-secondary danger-action" disabled={busy} onClick={() => onDecide(approval, "REJECTED")}>Reject</button><button className="glow-button-primary" disabled={busy} onClick={() => onDecide(approval, "APPROVED")}>Approve</button></>}</div></article>)}</div> : <EmptyData compact title="No approval requests" detail="High-risk or guided missions will appear here with their policy rationale." />}</section>;
}

function CapabilitiesView({ capabilities }: { capabilities: Capability[] }) { return <section className="registry-grid">{capabilities.length ? capabilities.map((capability) => <article className="registry-card" key={capability.slug}><div className="card-header"><Sparkles size={18} /><StatusBadge value={capability.enabled ? "AVAILABLE" : "UNAVAILABLE"} /></div><h2>{capability.name}</h2><p>{capability.description}</p><div className="tag-row"><span>{capability.version}</span><span>{capability.risk_level}</span><span>{capability.privacy_level}</span></div><p className="table-meta">Tools: {capability.required_tools.length ? capability.required_tools.join(", ") : "none"}</p></article>) : <EmptyData title="Capability registry unavailable" detail="Retry after the control plane reconnects." />}</section>; }

function ModelsView({ models }: { models: ModelDescriptor[] }) { return <section className="registry-grid">{models.map((model) => <article className="registry-card" key={model.id}><div className="card-header"><Cpu size={18} /><StatusBadge value={model.availability} /></div><h2>{model.id}</h2><p>{model.provider} · {model.privacy_level} privacy</p><div className="tag-row">{model.capability_classes.map((entry) => <span key={entry}>{entry.replaceAll("_", " ")}</span>)}</div><p className="table-meta">Tools {model.supports_tools ? "supported" : "not supported"} · Vision {model.supports_vision ? "supported" : "not supported"}</p></article>)}</section>; }

function ToolsView({ tools }: { tools: Record<string, unknown>[] }) { return <section className="content-card"><div className="card-header"><div><h2>Gateway tool catalog</h2><p>Agents cannot directly execute arbitrary tools; each call is validated through the gateway.</p></div><StatusBadge value="GOVERNED" /></div>{tools.length ? <JsonPanel value={tools} /> : <EmptyData compact title="No tool adapters are enabled" detail="The local provider is running without external tool permissions. This is a truthful unavailable state, not a simulated integration." />}</section>; }

function WorkflowsView({ workflows }: { workflows: Workflow[] }) { return <section className="content-card">{workflows.length ? <div className="workflow-list">{workflows.map((workflow) => <article className="approval-card" key={workflow.id}><div><StatusBadge value={workflow.is_active ? "PUBLISHED" : "UNPUBLISHED"} /><h3>{workflow.name}</h3><p>{workflow.description}</p></div><GitBranch size={20} className="text-muted" /></article>)}</div> : <EmptyData title="No saved workflows" detail="Mission blueprints are created automatically from intent. Published reusable workflows will appear here once created through the governed workflow API." icon={<GitBranch />} />}</section>; }

function ArtifactsView({ artifacts }: { artifacts: Artifact[] }) { return <section className="content-card"><div className="card-header"><div><h2>Generated artifacts</h2><p>Each output is linked to a mission and carries an immutable content hash.</p></div><FileBox size={20} /></div>{artifacts.length ? <div className="table-wrap"><table className="void-table"><thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Size</th><th>Created</th></tr></thead><tbody>{artifacts.map((artifact) => <tr key={artifact.id}><td>{artifact.name}<span className="table-meta">{artifact.mission_id?.slice(0, 8)}</span></td><td>{artifact.mime_type}</td><td><StatusBadge value={artifact.status} /></td><td>{formatBytes(artifact.size_bytes)}</td><td>{formatDate(artifact.created_at)}</td></tr>)}</tbody></table></div> : <EmptyData compact title="No artifacts yet" detail="Completing a local mission creates a hashed mission report here." />}</section>; }

function EvidenceView({ evidence }: { evidence: Evidence[] }) { return <section className="content-card"><div className="card-header"><div><h2>Claim evidence</h2><p>Evidence preserves the source, excerpt, confidence, and mission linkage.</p></div><FileSearch size={20} /></div>{evidence.length ? <div className="evidence-list">{evidence.map((item) => <article key={item.id} className="evidence-card"><div><StatusBadge value="VALIDATED" /><h3>{item.label.replaceAll("_", " ")}</h3><p>“{item.quote}”</p><span className="table-meta">{item.source} · mission {item.mission_id.slice(0, 8)}</span></div><strong>{Math.round(item.confidence * 100)}%</strong></article>)}</div> : <EmptyData compact title="No evidence recorded" detail="Source-backed missions will expose their evidence trail here." />}</section>; }

function EvaluationView({ missions }: { missions: Mission[] }) { const completed = missions.filter((entry) => entry.status === "COMPLETED"); return <section className="content-card"><div className="metric-grid compact"><Metric icon={<CheckCircle2 />} label="Validated completions" value={completed.length} tone="success" /><Metric icon={<AlertTriangle />} label="Requires review" value={missions.filter((entry) => entry.status === "REQUIRES_REVIEW").length} tone="warning" /><Metric icon={<XCircle />} label="Failed" value={missions.filter((entry) => entry.status === "FAILED").length} tone="danger" /></div><div className="evaluation-note"><Activity size={18} /><p>Every local completion records a schema, policy, and artifact-hash validation result in its mission record.</p></div></section>; }

function CostView({ missions }: { missions: Mission[] }) { const completed = missions.filter((mission) => mission.status === "COMPLETED").length; return <section className="content-card"><div className="metric-grid compact"><Metric icon={<CircleDollarSign />} label="Completed executions" value={completed} /><Metric icon={<Clock3 />} label="Current provider" value="Local" tone="info" /><Metric icon={<ShieldCheck />} label="Budget enforcement" value="Active" tone="success" /></div><p className="text-muted">Usage is persisted for every completed mission. Remote-provider cost remains zero until a configured provider is selected and approved.</p></section>; }

function PrivacyView({ missions }: { missions: Mission[] }) { return <section className="content-card"><div className="card-header"><div><h2>Privacy enforcement</h2><p>Privacy choices are carried into mission planning and policy evaluation.</p></div><StatusBadge value="ENFORCED" /></div><div className="detail-grid"><Detail label="Default local fallback" value="Enabled" /><Detail label="External provider policy" value="Approval required for private data" /><Detail label="Mission records" value={`${missions.length} persisted in this project`} /><Detail label="Artifact integrity" value="SHA-256 hashes recorded" /></div></section>; }

function IntegrationView({ models }: { models: ModelDescriptor[] }) { return <section className="content-card"><div className="card-header"><div><h2>Provider health</h2><p>Connections are never marked successful without configured credentials.</p></div><StatusBadge value="LIVE STATUS" /></div><div className="integration-list">{models.map((model) => <div className="integration-row" key={model.id}><div><strong>{model.provider}</strong><span className="table-meta">{model.id}</span></div><StatusBadge value={model.availability} /></div>)}</div></section>; }

function SettingsView() { return <section className="content-card"><div className="card-header"><div><h2>Execution defaults</h2><p>Per-mission options take precedence over these workspace controls.</p></div><SlidersIcon /></div><div className="detail-grid"><Detail label="Default execution" value="AUTO" /><Detail label="Default model route" value="AUTO" /><Detail label="Default privacy" value="STANDARD" /><Detail label="Approval gate" value="Risk and guided-mode controlled" /></div></section>; }
function HelpView() { return <section className="content-card help-grid"><article><span>01</span><h2>Describe the outcome</h2><p>Use Universal Command to enter natural language with your execution and privacy preferences.</p></article><article><span>02</span><h2>Review the plan</h2><p>VOID records intent normalization, capability routing, policy decisions, and a mission blueprint.</p></article><article><span>03</span><h2>Observe or approve</h2><p>Low-risk local work runs and produces a hashed artifact. Higher-risk work waits for approval.</p></article></section>; }

function ApprovalList({ approvals }: { approvals: Approval[] }) { return approvals.length ? <div className="approval-list">{approvals.map((approval) => <article className="approval-card" key={approval.id}><div><StatusBadge value={approval.status} /><h3>{approval.requested_action}</h3><p>{approval.risk_reason}</p></div></article>)}</div> : <EmptyData compact title="No approval checkpoints" detail="This mission can proceed without a human approval gate." />; }
function Timeline({ events }: { events: { id: string; event_type: string; timestamp: string; detail: string }[] }) { return events.length ? <ol className="timeline">{events.map((event) => <li key={event.id}><span /><div><strong>{event.event_type.replaceAll("_", " ")}</strong><p>{event.detail}</p><small>{formatDate(event.timestamp)}</small></div></li>)}</ol> : <EmptyData compact title="No lifecycle events" detail="Events will appear as the mission moves through the state machine." />; }
function Detail({ label, value }: { label: string; value: string }) { return <div className="detail"><span>{label}</span><strong>{value}</strong></div>; }
function JsonPanel({ value }: { value: unknown }) { return <pre className="json-panel">{JSON.stringify(value, null, 2)}</pre>; }
function Metric({ icon, label, value, tone = "" }: { icon: ReactNode; label: string; value: string | number; tone?: string }) { return <article className={`metric-card ${tone}`}><div>{icon}<span>{label}</span></div><strong>{value}</strong></article>; }
function LoadingState() { return <div className="state-card"><RefreshCw className="spin" /><h2>Connecting to the control plane</h2><p>Loading only persists while a request is in flight.</p></div>; }
function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) { return <div className="error-state" role="alert"><AlertTriangle size={18} /><span>{error}</span><button onClick={onRetry}>Retry</button></div>; }
function EmptyData({ title, detail, compact = false, icon }: { title: string; detail: string; compact?: boolean; icon?: React.ReactNode }) { return <div className={`empty-state ${compact ? "compact" : ""}`}>{icon ?? <Boxes size={24} />}<h2>{title}</h2><p>{detail}</p></div>; }
function SlidersIcon() { return <Sparkles size={20} />; }
function formatDate(value?: string) { if (!value) return "—"; const date = new Date(value); return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString([], { dateStyle: "medium", timeStyle: "short" }); }
function formatBytes(value: number) { return value < 1024 ? `${value} B` : `${(value / 1024).toFixed(1)} KB`; }
