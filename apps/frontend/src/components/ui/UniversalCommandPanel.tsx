"use client";

import { FormEvent, type ReactNode, useState } from "react";
import { ChevronDown, Cpu, LockKeyhole, Send, ShieldAlert, SlidersHorizontal } from "lucide-react";

export interface CommandOptions {
  executionMode: "AUTO" | "GUIDED" | "MANUAL";
  modelMode: "AUTO" | "HIGH_QUALITY" | "LOW_COST" | "FAST" | "PRIVATE" | "MANUAL";
  privacyMode: "STANDARD" | "PRIVATE" | "LOCAL";
}

export interface UniversalCommandPanelProps {
  onExecute: (prompt: string, options: CommandOptions) => void;
  isExecuting: boolean;
}

const quickCommands = [
  "Create a Python learning roadmap for 30 days",
  "Draft an executive project update",
  "Analyze my resume against a job description",
  "Research evidence for this decision",
];

export function UniversalCommandPanel({ onExecute, isExecuting }: UniversalCommandPanelProps) {
  const [prompt, setPrompt] = useState("");
  const [options, setOptions] = useState<CommandOptions>({ executionMode: "AUTO", modelMode: "AUTO", privacyMode: "STANDARD" });

  const execute = (event: FormEvent) => {
    event.preventDefault();
    if (!prompt.trim()) return;
    onExecute(prompt.trim(), options);
  };

  return (
    <section className="glass-panel-strong command-panel" aria-labelledby="command-title">
      <div className="command-heading">
        <div>
          <p className="eyebrow">MISSION INTAKE</p>
          <h2 id="command-title">What do you want VOID to accomplish?</h2>
          <p className="text-muted">Intent is normalized, policy-checked, and persisted before anything executes.</p>
        </div>
        <div className="command-security"><ShieldAlert size={16} /> Policy gateway active</div>
      </div>
      <form onSubmit={execute}>
        <label className="sr-only" htmlFor="mission-command">Mission objective</label>
        <textarea
          id="mission-command"
          className="void-textarea command-textarea"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Analyze my resume against this JD, create a learning plan, review code, or draft a report…"
        />
        <div className="command-controls">
          <CommandSelect icon={<SlidersHorizontal size={15} />} label="Execution" value={options.executionMode} values={["AUTO", "GUIDED", "MANUAL"]} onChange={(value) => setOptions({ ...options, executionMode: value as CommandOptions["executionMode"] })} />
          <CommandSelect icon={<Cpu size={15} />} label="Model" value={options.modelMode} values={["AUTO", "HIGH_QUALITY", "LOW_COST", "FAST", "PRIVATE", "MANUAL"]} onChange={(value) => setOptions({ ...options, modelMode: value as CommandOptions["modelMode"] })} />
          <CommandSelect icon={<LockKeyhole size={15} />} label="Privacy" value={options.privacyMode} values={["STANDARD", "PRIVATE", "LOCAL"]} onChange={(value) => setOptions({ ...options, privacyMode: value as CommandOptions["privacyMode"] })} />
          <button type="submit" className="glow-button-primary command-submit" disabled={isExecuting || !prompt.trim()}>
            {isExecuting ? "Creating mission…" : "Execute mission"}<Send size={16} />
          </button>
        </div>
      </form>
      <div className="quick-commands" aria-label="Suggested prompts">
        <span>Suggested</span>
        {quickCommands.map((command) => <button key={command} type="button" onClick={() => setPrompt(command)}>{command}</button>)}
      </div>
    </section>
  );
}

function CommandSelect({ icon, label, value, values, onChange }: { icon: ReactNode; label: string; value: string; values: string[]; onChange: (value: string) => void }) {
  return (
    <label className="command-select">
      {icon}<span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} aria-label={`${label} mode`}>
        {values.map((entry) => <option key={entry} value={entry}>{entry.replaceAll("_", " ")}</option>)}
      </select><ChevronDown size={14} aria-hidden="true" />
    </label>
  );
}
