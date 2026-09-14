"use client";

import React from "react";
import { Search, Bell, User } from "lucide-react";

export function Topbar() {
  return (
    <div className="topbar-container">
      <div className="flex-row">
        <div className="void-input" style={{ display: 'flex', alignItems: 'center', width: '300px', gap: '8px', padding: '6px 12px' }}>
          <Search size={16} className="text-muted" />
          <input 
            type="text" 
            placeholder="Search / Command (Ctrl+K)" 
            style={{ background: 'transparent', border: 'none', width: '100%', outline: 'none', fontSize: '13px' }} 
          />
        </div>
      </div>
      <div className="flex-row">
        <button style={{ color: 'var(--void-text-muted)' }}>
          <Bell size={18} />
        </button>
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
