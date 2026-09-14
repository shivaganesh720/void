"use client";

import React, { useState } from "react";
import { Send, Settings, Paperclip, Mic, ShieldAlert, Cpu } from "lucide-react";

import { motion } from "framer-motion";

export interface UniversalCommandPanelProps {
  onExecute: (prompt: string) => void;
  isExecuting: boolean;
}

export function UniversalCommandPanel({ onExecute, isExecuting }: UniversalCommandPanelProps) {
  const [prompt, setPrompt] = useState("");

  const handleExecute = () => {
    if (prompt.trim()) {
      onExecute(prompt);
      setPrompt("");
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="glass-panel-strong" 
      style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}
    >
      <div>
        <h2 style={{ fontSize: '28px', marginBottom: '8px' }}>Universal Command</h2>
        <p className="text-muted">Tell VOID what you want to achieve. We'll handle the rest.</p>
      </div>

      <div style={{ position: 'relative' }}>
        <textarea
          className="void-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. Analyze my resume against this job description and provide improvement suggestions."
          style={{ paddingBottom: '60px' }}
        />
        <div style={{ position: 'absolute', bottom: '16px', left: '16px', right: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="button-secondary" style={{ padding: '6px' }} title="Attach File"><Paperclip size={18} /></button>
            <button className="button-secondary" style={{ padding: '6px' }} title="Voice Input"><Mic size={18} /></button>
          </div>
          <button 
            className="glow-button-primary" 
            onClick={handleExecute}
            disabled={isExecuting || !prompt.trim()}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {isExecuting ? "Executing..." : "Confirm & Execute"} <Send size={16} />
          </button>
        </div>
      </div>

      <div className="grid-cols-2" style={{ gap: '12px' }}>
        <motion.div whileHover={{ y: -2 }} className="glass-card" style={{ padding: '12px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
          <Cpu size={18} className="text-secondary" />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600 }}>Model Preference</div>
            <div style={{ fontSize: '11px' }} className="text-muted">Auto-select</div>
          </div>
        </motion.div>
        <motion.div whileHover={{ y: -2 }} className="glass-card" style={{ padding: '12px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
          <ShieldAlert size={18} className="text-secondary" />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600 }}>Privacy Mode</div>
            <div style={{ fontSize: '11px' }} className="text-muted">Standard execution</div>
          </div>
        </motion.div>
      </div>

      <div style={{ marginTop: '8px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, marginBottom: '12px' }} className="text-muted">QUICK COMMANDS</div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {["Analyze resume", "Research topic", "Build application", "Create report", "Learn something"].map((cmd) => (
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              key={cmd}
              onClick={() => setPrompt(cmd)}
              className="button-secondary" 
              style={{ padding: '6px 12px', fontSize: '12px', borderRadius: '16px' }}
            >
              {cmd}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
