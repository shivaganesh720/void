"use client";

import { AudioLines, Bot, BrainCircuit, Ear, Mic, ShieldCheck, Sparkles, Volume2 } from "lucide-react";

export interface NexaCapability {
  name: string;
  detail: string;
}

interface NexaVoiceAssistantProps {
  capabilities?: NexaCapability[];
  status?: "ACTIVE" | "LISTENING" | "THINKING" | "SPEAKING";
}

interface NexaFaceLauncherProps {
  onOpen: () => void;
}

const defaultCapabilities: NexaCapability[] = [
  { name: "Voice intake", detail: "Mission capture and intent normalization" },
  { name: "Companion sync", detail: "Status updates across the local runtime" },
  { name: "Privacy guard", detail: "Approval-aware local handling" },
  { name: "Mission brief", detail: "Concise summaries and action checks" },
  { name: "Task updates", detail: "Progress, retries, and completion alerts" },
  { name: "Safety review", detail: "Policy-first workflow gating" },
];

export function NexaFaceLauncher({ onOpen }: NexaFaceLauncherProps) {
  return (
    <button type="button" className="nexa-face-launcher" onClick={onOpen} aria-label="Open NEXA voice assistant">
      <span className="nexa-launcher-label">
        <span className="eyebrow">VOICE COMPANION</span>
        <strong>NEXA</strong>
      </span>
      <span className="nexa-launcher-avatar" aria-hidden="true">
        <span className="nexa-launcher-head">
          <span className="nexa-launcher-ear left" />
          <span className="nexa-launcher-ear right" />
          <span className="nexa-launcher-face">
            <span className="nexa-launcher-eyes"><span /><span /></span>
            <span className="nexa-launcher-mouth" />
          </span>
        </span>
        <span className="nexa-launcher-body"><span /></span>
      </span>
    </button>
  );
}

export function NexaVoiceAssistant({
  capabilities = defaultCapabilities,
  status = "ACTIVE",
}: NexaVoiceAssistantProps) {
  const statusLabel = {
    ACTIVE: "Listening and ready",
    LISTENING: "Listening for commands",
    THINKING: "Reasoning through the mission",
    SPEAKING: "Speaking the mission update",
  }[status];

  return (
    <section className="glass-panel-strong nexa-panel" aria-label="NEXA voice assistant">
      <div className="nexa-topbar">
        <div className="nexa-title-wrap">
          <p className="eyebrow">VOICE COMPANION</p>
          <h2>NEXA</h2>
        </div>
        <div className={`nexa-status ${status.toLowerCase()}`}>
          <span className="status-dot" />
          {status}
        </div>
      </div>

      <div className="nexa-layout">
        <div className="nexa-avatar-wrap">
          <div className={`nexa-avatar nexa-${status.toLowerCase()}`}>
            <div className="nexa-head">
              <div className="nexa-ear nexa-ear-left" />
              <div className="nexa-ear nexa-ear-right" />
              <div className="nexa-face">
                <div className="nexa-eye-group">
                  <span className="nexa-eye" />
                  <span className="nexa-eye" />
                </div>
                <div className="nexa-mouth" />
              </div>
            </div>
            <div className="nexa-body">
              <span className="nexa-antenna" />
              <span className="nexa-core" />
            </div>
            <div className="nexa-arms">
              <span className="nexa-arm left" />
              <span className="nexa-arm right" />
            </div>
            <div className="nexa-legs">
              <span className="nexa-leg left" />
              <span className="nexa-leg right" />
            </div>
          </div>
        </div>

        <div className="nexa-content">
          <div className="nexa-summary">
            <Bot size={18} />
            <p>{statusLabel}</p>
          </div>

          <div className="nexa-actions">
            <button type="button" className="glow-button-primary">
              <Mic size={15} /> Listen
            </button>
            <button type="button" className="button-secondary">
              <Volume2 size={15} /> Speak
            </button>
          </div>

          <div className="capability-list" aria-label="Voice assistant capabilities">
            {capabilities.map((capability) => (
              <div key={capability.name} className="capability-item">
                <div className="capability-icon">
                  {capability.name.toLowerCase().includes("privacy") ? <ShieldCheck size={14} /> : capability.name.toLowerCase().includes("brief") ? <AudioLines size={14} /> : capability.name.toLowerCase().includes("brain") || capability.name.toLowerCase().includes("reason") ? <BrainCircuit size={14} /> : capability.name.toLowerCase().includes("companion") ? <Ear size={14} /> : <Sparkles size={14} />}
                </div>
                <div>
                  <strong>{capability.name}</strong>
                  <span>{capability.detail}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
