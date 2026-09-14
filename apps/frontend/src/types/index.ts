export interface Mission {
  id: string;
  intent: string;
  status: string;
  created_at: string;
  updated_at?: string;
  execution_mode?: string;
  completed_at?: string;
  task: { status: string };
  result?: any;
  error?: string;
  events?: any[];
}

export interface ProjectSummary {
  total_missions: number;
  running_missions: number;
  completed_missions: number;
  failed_missions: number;
  blocked_missions: number;
  recent_missions: Mission[];
}

export interface Analysis {
  scores?: any;
  [key: string]: any;
}
