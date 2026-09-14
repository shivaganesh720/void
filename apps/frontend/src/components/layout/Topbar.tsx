"use client";

import React from "react";
import { Command, Search, ShieldCheck, User } from "lucide-react";

export function Topbar({ onCommand }: { onCommand?: () => void }) {
  return (
    <div className="topbar-container">
      <div className="flex-row">
        <button type="button" onClick={onCommand} className="topbar-command" aria-label="Open Universal Command">
          <Search size={16} className="text-muted" />
          <span>Open Universal Command</span><kbd>⌘ K</kbd>
        </button>
      </div>
      <div className="flex-row">
        <div className="topbar-health"><ShieldCheck size={16} /> Local policy online</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '13px', fontWeight: 600 }}>Administrator</span>
            <span style={{ fontSize: '11px', color: 'var(--void-success)' }}>System Online</span>
          </div>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--void-purple), var(--void-cyan))', display: 'grid', placeItems: 'center' }}>
            <User size={16} color="#fff" />
          </div>
        </div>
      </div>
    </div>
  );
}
