"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "../../components/layout/AppShell";
import { UniversalCommandPanel } from "../../components/ui/UniversalCommandPanel";
import { MetricCard } from "../../components/ui/MetricCard";
import { MissionCard } from "../../components/ui/MissionCard";
import { Target, CheckCircle, Clock, AlertTriangle, Play, ShieldAlert } from "lucide-react";

// Assuming types from original
import { Mission, ProjectSummary, Analysis } from "../../types";

// Provide a mock AnalysisResult component for now to fix TS errors if we removed it
function AnalysisResult({ analysis }: { analysis: any }) {
  return (
    <div className="glass-panel" style={{ padding: '16px', marginTop: '16px' }}>
      <p style={{ fontWeight: 600 }}>Legacy Analysis Result</p>
      <pre className="font-mono text-muted" style={{ fontSize: '11px', whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(analysis, null, 2)}
      </pre>
    </div>
  );
}

export default function WorkspacePage() {
  const [view, setView] = useState("dashboard");
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataError, setDataError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [mission, setMission] = useState<Mission | null>(null);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [error, setError] = useState("");

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  async function ensureProject() {
    let projectId = localStorage.getItem("void_project_id");
    if (!projectId) {
      const response = await fetch(`${API_BASE}/api/v1/projects`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        credentials: "include",
        body: JSON.stringify({ name: "Default Project", description: "Auto-created project" }) 
      });
      if (!response.ok) throw new Error("Failed to initialize project");
      const data = await response.json();
      projectId = data.id;
      localStorage.setItem("void_project_id", data.id);
    }
    return projectId;
  }

  async function getJson<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, { credentials: "include" });
    if (response.status === 401) {
      window.location.href = "/sign-in";
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async function loadDashboard() {
    try {
      setLoading(true);
      const projectId = await ensureProject();
      const data = await getJson<ProjectSummary>(`/api/v1/dashboard/summary?project_id=${projectId}`);
      setSummary(data);
      setDataError("");
    } catch {
      setDataError("Failed to connect to local Control Plane API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadDashboard(); }, []);

  // Simple polling
  useEffect(() => {
    if (!mission || ["COMPLETED", "FAILED", "CANCELLED", "BLOCKED"].includes(mission.status)) return;
    const timer = window.setInterval(async () => {
      try { const projectId = await ensureProject(); setMission(await getJson<Mission>(`/api/v1/missions/${mission.id}?project_id=${projectId}`)); }
      catch { setError("Mission status could not be refreshed."); }
    }, 1000);
    return () => window.clearInterval(timer);
  }, [mission]);

  async function handleUniversalExecute(prompt: string) {
    setSubmitting(true); setError(""); setMission(null);
    try {
      const projectId = await ensureProject();
      const response = await fetch(`${API_BASE}/api/v1/missions/universal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ project_id: projectId, prompt })
      });
      if (response.status === 401) {
        window.location.href = "/sign-in";
        return;
      }
      const payload = await response.json(); 
      if (!response.ok) throw new Error(payload.detail?.[0]?.msg ?? payload.detail ?? "Mission request failed");
      setMission(payload); 
      await loadDashboard();
    } catch (requestError) { 
      setError(requestError instanceof Error ? requestError.message : "Mission request failed"); 
    } finally { 
      setSubmitting(false); 
    }
  }

  const renderDashboard = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <UniversalCommandPanel onExecute={handleUniversalExecute} isExecuting={submitting} />
      
      {error && <div className="glass-panel" style={{ padding: '16px', color: 'var(--void-danger)', border: '1px solid rgba(248,113,113,0.3)' }}>{error}</div>}
      
      {mission && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px' }}>Active Mission: {mission.intent || mission.id.substring(0, 8)}</h3>
            <span className={`status-badge ${mission.status === 'COMPLETED' ? 'success' : mission.status === 'FAILED' ? 'danger' : 'info'}`}>
              {mission.status}
            </span>
          </div>
          
          <div style={{ marginBottom: '16px', fontSize: '13px' }} className="text-secondary">
            Task Status: <strong>{mission.task?.status}</strong>
          </div>

          {mission.result && (mission.result as any).output ? (
            <div className="glass-card">
              <div style={{ marginBottom: '12px' }}>
                <span className="status-badge neutral" style={{ marginRight: '8px' }}>Agent: {(mission.result as any).agent}</span>
                <span className="status-badge neutral">Capability: {(mission.result as any).capability}</span>
              </div>
              <pre className="font-mono" style={{ fontSize: '12px', whiteSpace: 'pre-wrap', color: 'var(--void-text-primary)' }}>
                {(mission.result as any).output}
              </pre>
            </div>
          ) : (
            mission.result && <AnalysisResult analysis={mission.result as Analysis} />
          )}
          {mission.error && <p className="text-danger" style={{ marginTop: '12px', fontSize: '13px' }}>{mission.error}</p>}
        </div>
      )}

      <div>
        <h3 style={{ fontSize: '20px', marginBottom: '16px' }}>Project Overview</h3>
        <div className="grid-cols-4">
          <MetricCard title="Total Missions" value={loading ? "-" : summary?.total_missions ?? 0} icon={Target} />
          <MetricCard title="Completed" value={loading ? "-" : summary?.completed_missions ?? 0} icon={CheckCircle} trendPositive={true} />
          <MetricCard title="In Progress" value={loading ? "-" : summary?.running_missions ?? 0} icon={Play} />
          <MetricCard title="Failed" value={loading ? "-" : summary?.failed_missions ?? 0} icon={AlertTriangle} trendPositive={false} />
        </div>
      </div>

      {summary?.recent_missions && summary.recent_missions.length > 0 && (
        <div>
          <h3 style={{ fontSize: '20px', marginBottom: '16px' }}>Recent Missions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {summary.recent_missions.map((m: Mission, i: number) => (
              <MissionCard key={m.id} mission={m} index={i} onClick={() => setView('missions')} />
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderPlaceholder = (title: string, desc: string) => (
    <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
      <h2 style={{ fontSize: '24px', marginBottom: '12px' }}>{title}</h2>
      <p className="text-muted" style={{ maxWidth: '400px' }}>{desc}</p>
    </div>
  );

  return (
    <AppShell currentView={view} onNavigate={setView}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '64px' }}>
        <header style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>
            {view === 'dashboard' ? 'Good morning, Administrator' : view.charAt(0).toUpperCase() + view.slice(1)}
          </h1>
          {view === 'dashboard' && <p className="text-muted">Turn your ideas into intelligent actions.</p>}
        </header>

        {dataError && (
          <div className="glass-panel" style={{ padding: '16px', marginBottom: '24px', border: '1px solid var(--void-danger)', color: 'var(--void-danger)' }}>
            {dataError}
          </div>
        )}

        {view === 'dashboard' && renderDashboard()}
        {view === 'missions' && renderPlaceholder("Mission History", "A detailed view of all project missions, capabilities used, and execution timelines.")}
        {view === 'approvals' && renderPlaceholder("Approval Center", "Review and authorize blocked missions, governed tools, and high-risk actions.")}
        {view === 'capabilities' && renderPlaceholder("Capability Registry", "Explore available platform capabilities and tools.")}
        {view === 'models' && renderPlaceholder("Model Explorer", "Configure and inspect available intelligence providers.")}
        {view === 'tools' && renderPlaceholder("Tool Registry", "Manage executable tools and their permission scopes.")}
        {view === 'knowledge' && renderPlaceholder("Knowledge Base", "Upload and manage RAG documents for context injection.")}
        {view === 'artifacts' && renderPlaceholder("Artifacts", "View output files, documents, and code generated by missions.")}
        {view === 'settings' && renderPlaceholder("Settings", "Configure workspace defaults and execution profiles.")}
      </div>
    </AppShell>
  );
}
