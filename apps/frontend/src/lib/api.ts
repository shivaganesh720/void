import type { Agent, Approval, Artifact, Capability, Evidence, Mission, ModelDescriptor, ProjectSummary, Workflow } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include", ...init });
  if (response.status === 401 && typeof window !== "undefined") window.location.assign(new URL("/sign-in", window.location.origin));
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload?.error?.message ?? payload?.detail;
    throw new ApiError(Array.isArray(detail) ? detail[0]?.msg ?? "Invalid request" : detail ?? `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  async ensureProject(): Promise<string> {
    const stored = window.localStorage.getItem("void_project_id");
    if (stored) return stored;
    const project = await request<{ id: string }>("/api/v1/projects", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: "Default Project" }),
    });
    window.localStorage.setItem("void_project_id", project.id);
    return project.id;
  },
  dashboard: (projectId: string) => request<ProjectSummary>(`/api/v1/dashboard/summary?project_id=${projectId}`),
  missions: (projectId: string) => request<Mission[]>(`/api/v1/missions?project_id=${projectId}`),
  mission: (projectId: string, missionId: string) => request<Mission>(`/api/v1/missions/${missionId}?project_id=${projectId}`),
  createMission: (projectId: string, prompt: string, executionMode: string, modelMode: string, privacyMode: string) => request<Mission>("/api/v1/missions/universal", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId, prompt, execution_profile: { execution_mode: executionMode, model_mode: modelMode, privacy_mode: privacyMode } }),
  }),
  controlMission: (projectId: string, missionId: string, action: string) => request<Mission>(`/api/v1/missions/${missionId}/actions/${action}?project_id=${projectId}`, { method: "POST" }),
  approvals: (projectId: string) => request<Approval[]>(`/api/v1/approvals?project_id=${projectId}`),
  decideApproval: (projectId: string, approval: Approval, decision: "APPROVED" | "REJECTED") => request<Approval>(`/api/v1/missions/${approval.mission_id}/approvals/${approval.id}?project_id=${projectId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ decision }) }),
  capabilities: () => request<Capability[]>("/api/v1/capabilities"),
  agents: () => request<Agent[]>("/api/v1/agents"),
  models: () => request<ModelDescriptor[]>("/api/v1/models"),
  tools: () => request<Record<string, unknown>[]>("/api/v1/tools"),
  workflows: () => request<Workflow[]>("/api/v1/workflows"),
  artifacts: (projectId: string) => request<Artifact[]>(`/api/v1/projects/${projectId}/artifacts`),
  evidence: (projectId: string) => request<Evidence[]>(`/api/v1/projects/${projectId}/evidence`),
};
