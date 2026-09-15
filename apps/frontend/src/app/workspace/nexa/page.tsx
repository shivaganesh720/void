"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  AudioLines,
  Bot,
  BriefcaseBusiness,
  Cpu,
  FileText,
  Globe2,
  Mic,
  MonitorPlay,
  Search,
  ShieldCheck,
  Sparkles,
  Volume2,
  Wand2,
} from "lucide-react";

const capabilityRows = [
  { label: "Voice commands", icon: Mic },
  { label: "Open apps", icon: MonitorPlay },
  { label: "Browse the web", icon: Globe2 },
  { label: "Search files", icon: Search },
  { label: "Manage tasks", icon: BriefcaseBusiness },
  { label: "Mission updates", icon: AudioLines },
  { label: "Document drafting", icon: FileText },
  { label: "System actions", icon: Cpu },
];

const suggestedCommands = [
  "Open VS Code",
  "Launch Chrome and search for project status",
  "Create a mission to summarize the sprint",
  "Open the workspace dashboard",
  "Read my recent notes and draft a brief",
];

export default function NexaPage() {
  const [isListening, setIsListening] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Ready to assist");

  const liveCapabilities = useMemo(
    () => capabilityRows.map((item) => ({ ...item, active: item.label === "Voice commands" || item.label === "Mission updates" })),
    []
  );

  const handleListen = () => {
    setIsListening((current) => !current);
    setStatusMessage(isListening ? "Ready to assist" : "Listening for your command");
  };

  return (
    <main className="nexa-screen-shell">
      <div className="nexa-screen-frame">
        <header className="nexa-screen-header">
          <Link href="/workspace" className="nexa-back-link">
            <ArrowLeft size={16} /> Workspace
          </Link>
          <div className="nexa-status-pill">
            <span className={`nexa-dot ${isListening ? "active" : "idle"}`} />
            {isListening ? "LISTENING" : "READY"}
          </div>
        </header>

        <section className="nexa-hero-panel">
          <div className="nexa-robot-stage">
            <div className={`nexa-avatar nexa-${isListening ? "listening" : "active"}`} aria-label="NEXA robot assistant">
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

          <div className="nexa-hero-copy">
            <p className="eyebrow text-uppercase">VOICE COMPANION</p>
            <h1>NEXA</h1>
            <p className="nexa-subtitle">Your local AI desktop companion for mission execution, document work, browser activity, and system-level task control.</p>

            <div className="nexa-quick-actions">
              <button type="button" className="glow-button-primary" onClick={handleListen}>
                <Mic size={16} /> {isListening ? "Stop listening" : "Start listening"}
              </button>
              <button type="button" className="button-secondary" aria-label="Speak to NEXA">
                <Volume2 size={16} /> Speak
              </button>
            </div>

            <div className="nexa-status-block">
              <Bot size={16} />
              <span>{statusMessage}</span>
            </div>
          </div>
        </section>

        <section className="nexa-lower-grid">
          <div className="nexa-panel-column">
            <div className="nexa-section-header">
              <Sparkles size={16} />
              <h2>Capabilities</h2>
            </div>

            <div className="nexa-capability-grid">
              {liveCapabilities.map(({ label, icon: Icon, active }) => (
                <div key={label} className={`nexa-capability ${active ? "active" : ""}`}>
                  <span className="nexa-capability-icon"><Icon size={14} /></span>
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="nexa-panel-column">
            <div className="nexa-section-header">
              <ShieldCheck size={16} />
              <h2>Suggested actions</h2>
            </div>

            <div className="nexa-command-list">
              {suggestedCommands.map((command) => (
                <button key={command} type="button" className="nexa-command-item">
                  <Wand2 size={14} />
                  <span>{command}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
