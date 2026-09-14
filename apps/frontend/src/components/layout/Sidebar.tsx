"use client";

import React from "react";
import { 
  Command, 
  Target, 
  Zap, 
  Box, 
  Terminal, 
  GitMerge, 
  Book, 
  Brain, 
  Files, 
  ShieldCheck, 
  Search, 
  Activity, 
  DollarSign, 
  Lock, 
  Cable, 
  Settings, 
  HelpCircle 
} from "lucide-react";

export interface SidebarProps {
  currentView?: string;
  onNavigate?: (viewId: string) => void;
}

export function Sidebar({ currentView = "dashboard", onNavigate = () => {} }: SidebarProps) {
  const mainNav = [
    { id: "dashboard", label: "Universal Command", icon: Command },
    { id: "missions", label: "Missions", icon: Target },
    { id: "capabilities", label: "Capabilities", icon: Zap },
    { id: "models", label: "Models", icon: Box },
    { id: "tools", label: "Tools", icon: Terminal },
    { id: "workflows", label: "Workflows", icon: GitMerge },
  ];

  const knowledgeNav = [
    { id: "knowledge", label: "Knowledge", icon: Book },
    { id: "memory", label: "Memory", icon: Brain },
    { id: "artifacts", label: "Artifacts", icon: Files },
  ];

  const govNav = [
    { id: "approvals", label: "Approvals", icon: ShieldCheck },
    { id: "evidence", label: "Evidence", icon: Search },
    { id: "evaluation", label: "Evaluation", icon: Activity },
    { id: "cost", label: "Cost", icon: DollarSign },
    { id: "privacy", label: "Privacy", icon: Lock },
  ];

  const adminNav = [
    { id: "integrations", label: "Integrations", icon: Cable },
    { id: "admin", label: "Admin", icon: Settings },
    { id: "settings", label: "Settings", icon: Settings },
    { id: "help", label: "Help", icon: HelpCircle },
  ];

  const NavItem = ({ item }: { item: any }) => {
    const isActive = currentView === item.id;
    return (
      <a 
        href={`#${item.id}`} 
        onClick={(e) => { e.preventDefault(); onNavigate(item.id); }}
        className={`sidebar-link ${isActive ? "active" : ""}`}
      >
        <item.icon size={18} />
        {item.label}
      </a>
    );
  };

  return (
    <div className="sidebar-container">
      <div className="sidebar-header">
        <div className="brand-v">V</div>
        <div className="brand-text">VOID</div>
      </div>
      <div className="workspace-scroll-area" style={{ padding: "0 0 24px 0" }}>
        <div className="sidebar-nav">
          <div className="nav-group-label">Core</div>
          {mainNav.map(item => <NavItem key={item.id} item={item} />)}
          
          <div className="nav-group-label">Intelligence</div>
          {knowledgeNav.map(item => <NavItem key={item.id} item={item} />)}
          
          <div className="nav-group-label">Governance</div>
          {govNav.map(item => <NavItem key={item.id} item={item} />)}
          
          <div className="nav-group-label">System</div>
          {adminNav.map(item => <NavItem key={item.id} item={item} />)}
        </div>
      </div>
    </div>
  );
}
