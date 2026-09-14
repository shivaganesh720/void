"use client";

import React from "react";
import { LucideIcon } from "lucide-react";

import { motion } from "framer-motion";

export interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
}

export function MetricCard({ title, value, icon: Icon, trend, trendPositive }: MetricCardProps) {
  return (
    <motion.div 
      whileHover={{ y: -2, boxShadow: "0 8px 30px rgba(0,0,0,0.4)" }}
      className="glass-card" 
      style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '12px', fontWeight: 600 }} className="text-muted">{title}</span>
        <div style={{ padding: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
          <Icon size={16} className="text-secondary" />
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
        <span style={{ fontSize: '32px', fontWeight: 700, fontFamily: 'Space Grotesk, sans-serif' }}>{value}</span>
        {trend && (
          <span style={{ fontSize: '11px', fontWeight: 600, color: trendPositive ? 'var(--void-success)' : 'var(--void-danger)' }}>
            {trend}
          </span>
        )}
      </div>
    </motion.div>
  );
}
