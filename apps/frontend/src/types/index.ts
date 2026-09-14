export type ExecutionMode = "AUTO" | "GUIDED" | "MANUAL";

export interface Task {
  id: string;
  mission_id: string;
  name: string;
  status: string;
  result?: Record<string, unknown> | null;
  error?: string | null;
}

export interface MissionEvent {
  id: string;
  event_type: string;
  timestamp: string;
  detail: string;
}

export interface Approval {
  id: string;
  mission_id: string;
  task_id?: string | null;
  requested_action: string;
  risk_reason: string;
  required_by_policy: boolean;
  status: string;
  requested_at: string;
  reviewed_at?: string | null;
  metadata?: Record<string, unknown>;
}

export interface Mission {
  id: string;
  project_id: string;
  intent: string;
  status: string;
  execution_mode: ExecutionMode;
  created_at: string;
  updated_at?: string;
  completed_at?: string | null;
  task: Task;
  result?: Record<string, unknown> | null;
  error?: string | null;
  events?: MissionEvent[];
  approvals?: Approval[];
  approval_required?: boolean;
  execution_profile?: Record<string, unknown> | null;
}

export interface ProjectSummary {
  total_missions: number;
  running_missions: number;
  completed_missions: number;
  failed_missions: number;
  blocked_missions: number;
  recent_missions: Mission[];
}

export interface Capability {
  slug: string;
  name: string;
  version: string;
  description: string;
  required_tools: string[];
  supported_file_types: string[];
  risk_level: string;
  privacy_level: string;
  enabled: boolean;
  validation_requirements: string[];
}

export interface Agent {
  id: string;
  name: string;
  version: string;
  role: string;
  responsibilities: string[];
  tool_allowlist: string[];
  model_class: string;
  risk_level: string;
  prompt_version: string;
  budget_tokens: number;
  timeout_seconds: number;
  enabled: boolean;
}

export interface ModelDescriptor {
  id: string;
  provider: string;
  capability_classes: string[];
  privacy_level: string;
  supports_tools: boolean;
  supports_vision: boolean;
  supports_structured_output: boolean;
  availability: string;
  fallback: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at?: string;
}

export interface Artifact {
  id: string;
  name: string;
  type: string;
  mime_type: string;
  size_bytes: number;
  status: string;
  created_at: string;
  mission_id?: string | null;
  task_id?: string | null;
}

export interface Evidence {
  id: string;
  mission_id: string;
  task_id?: string | null;
  source: string;
  label: string;
  quote: string;
  confidence: number;
  created_at: string;
}
