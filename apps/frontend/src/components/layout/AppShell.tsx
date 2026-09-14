"use client";

import React, { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export interface AppShellProps {
  children: ReactNode;
  currentView?: string;
  onNavigate?: (view: string) => void;
}

export function AppShell({ children, currentView, onNavigate }: AppShellProps) {
  return (
    <div className="app-layout">
      <Sidebar currentView={currentView} onNavigate={onNavigate} />
      <div className="main-content">
        <Topbar />
        <div className="workspace-scroll-area">
          {children}
        </div>
      </div>
    </div>
  );
}
