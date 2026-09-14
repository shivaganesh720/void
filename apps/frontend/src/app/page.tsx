import Link from "next/link";
import { ArrowRight, ShieldCheck, Zap, Lock, Target } from "lucide-react";

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', color: 'var(--void-text-primary)' }}>
      {/* Navigation */}
      <nav style={{ padding: '24px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--void-border)' }} className="glass-panel">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontWeight: 700, fontSize: '24px', letterSpacing: '2px', background: 'linear-gradient(90deg, var(--void-cyan), var(--void-purple))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            VOID
          </div>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px' }} className="text-muted">
            Intelligent Dispatcher
          </div>
        </div>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <a href="#product" className="text-secondary" style={{ fontSize: '14px', textDecoration: 'none' }}>Platform</a>
          <a href="#security" className="text-secondary" style={{ fontSize: '14px', textDecoration: 'none' }}>Security</a>
          <Link href="/login" className="text-primary" style={{ fontSize: '14px', textDecoration: 'none', fontWeight: 500 }}>Sign In</Link>
          <Link href="/register" className="glow-button-primary" style={{ textDecoration: 'none', padding: '8px 16px', fontSize: '14px' }}>
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '120px 24px', textAlign: 'center' }}>
        <div style={{ maxWidth: '800px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px' }}>
          <div className="status-badge info" style={{ padding: '6px 12px', fontSize: '12px', letterSpacing: '1px' }}>
            GOVERNED AI EXECUTION PLATFORM
          </div>
          <h1 style={{ fontSize: '64px', lineHeight: 1.1, fontWeight: 700, fontFamily: 'Space Grotesk, sans-serif' }}>
            Your intent.<br />
            <span style={{ color: 'var(--void-cyan)' }}>Governed orchestration.</span>
          </h1>
          <p className="text-muted" style={{ fontSize: '18px', maxWidth: '600px', lineHeight: 1.6 }}>
            From a simple request to a controlled, validated result. VOID coordinates work with transparency, security, and measurable outcomes.
          </p>
          
          <div style={{ display: 'flex', gap: '16px', marginTop: '32px' }}>
            <Link href="/workspace" className="glow-button-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', padding: '12px 24px', textDecoration: 'none' }}>
              Launch Workspace <ArrowRight size={18} />
            </Link>
            <a href="#workflow" className="button-secondary" style={{ fontSize: '16px', padding: '12px 24px', textDecoration: 'none' }}>
              Explore how it works
            </a>
          </div>

          <div style={{ display: 'flex', gap: '24px', marginTop: '48px', fontSize: '13px' }} className="text-secondary">
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Lock size={14} /> Local-first</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><ShieldCheck size={14} /> Policy-aware</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Zap size={14} /> Evidence-backed</span>
          </div>
        </div>
      </main>

      {/* Services Section */}
      <section id="product" style={{ padding: '80px 24px', background: 'var(--void-background-secondary)' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '32px', textAlign: 'center', marginBottom: '48px' }}>Services Provided</h2>
          <div className="grid-cols-3">
            <div className="glass-card">
              <div style={{ color: 'var(--void-cyan)', marginBottom: '16px' }}><Zap size={32} /></div>
              <h3 style={{ fontSize: '20px', marginBottom: '12px' }}>Deterministic Analysis</h3>
              <p className="text-secondary" style={{ fontSize: '14px', lineHeight: 1.6 }}>Analyze resumes against Job Descriptions with guaranteed reproducible outputs, strict structure validation, and isolated execution.</p>
            </div>
            <div className="glass-card">
              <div style={{ color: 'var(--void-purple)', marginBottom: '16px' }}><ShieldCheck size={32} /></div>
              <h3 style={{ fontSize: '20px', marginBottom: '12px' }}>Policy Enforcement</h3>
              <p className="text-secondary" style={{ fontSize: '14px', lineHeight: 1.6 }}>Every action is evaluated against project-level governance rules. Unauthorized capabilities and unsafe prompts are automatically blocked.</p>
            </div>
            <div className="glass-card">
              <div style={{ color: 'var(--void-success)', marginBottom: '16px' }}><Target size={32} /></div>
              <h3 style={{ fontSize: '20px', marginBottom: '12px' }}>Workspace Isolation</h3>
              <p className="text-secondary" style={{ fontSize: '14px', lineHeight: 1.6 }}>Project-scoped workspaces ensure data boundaries are respected. Track mission states, event timelines, and artifact generation securely.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--void-border)', padding: '48px', textAlign: 'center' }} className="glass-panel text-muted">
        <p style={{ fontSize: '12px' }}>© 2026 VOID | Versatile Orchestrated Intelligent Dispatcher. All systems governed.</p>
      </footer>
    </div>
  );
}
