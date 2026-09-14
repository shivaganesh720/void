"use client";

import React from "react";
import { Zap, Clock, AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";
import { Mission } from "../../types";

import { motion } from "framer-motion";

export interface MissionCardProps {
  mission: any;
  onClick?: () => void;
  index?: number;
}

export function MissionCard({ mission, onClick, index = 0 }: MissionCardProps) {
  
  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'COMPLETED': return <CheckCircle size={14} className="text-success" color="var(--void-success)" />;
      case 'FAILED': return <AlertTriangle size={14} className="text-danger" color="var(--void-danger)" />;
      case 'RUNNING': return <Clock size={14} className="text-info" color="var(--void-info)" />;
      default: return <Clock size={14} className="text-muted" />;
    }
  };

  const getStatusClass = (status: string) => {
    switch(status) {
      case 'COMPLETED': return 'success';
      case 'FAILED': return 'danger';
      case 'RUNNING': return 'info';
      default: return 'neutral';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ y: -2 }}
      className="glass-card" 
      onClick={onClick}
      style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        gap: '16px',
        padding: '16px 20px',
        cursor: onClick ? 'pointer' : 'default'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', display: 'grid', placeItems: 'center' }}>
          <Zap size={18} className="text-secondary" />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600 }}>{mission.intent || "Unnamed Mission"}</span>
            <span className={`status-badge ${getStatusClass(mission.status)}`} style={{ padding: '2px 6px', fontSize: '10px' }}>
              {mission.status}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }} className="text-muted">
            <span className="font-mono">{mission.id.substring(0, 8)}</span>
            <span>•</span>
            <span>{new Date(mission.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '12px', fontWeight: 500 }} className="text-secondary">Task: {mission.task?.status || "PENDING"}</div>
        </div>
        <div style={{ padding: '8px', background: 'var(--void-panel-hover)', borderRadius: '50%' }}>
          <ArrowRight size={14} className="text-secondary" />
        </div>
      </div>
    </motion.div>
  );
}
