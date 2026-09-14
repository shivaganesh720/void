"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ArrowRight, ShieldCheck, Zap, Lock, Target, Command, Box,
  GitBranch, CheckCircle, Activity, Server, FileText,
  Search, ShieldAlert, AlertTriangle
} from "lucide-react";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="landing-layout">
      {/* 1. NAVIGATION BAR */}
      <nav className={`landing-nav ${scrolled ? "scrolled" : ""}`}>
        <div className="nav-container">
          <Link href="/" className="nav-brand">
            <span className="brand-orbit">◌</span>
            <span className="brand-text">
              <strong>VOID</strong>
              <small>OBSIDIAN GLASS</small>
            </span>
          </Link>
          <div className="nav-links">
            <a href="#product">Product</a>
            <a href="#capabilities">Capabilities</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#security">Security</a>
          </div>
          <div className="nav-actions">
            <Link href="/sign-in" className="nav-link-subtle">Sign In</Link>
            <Link href="/sign-up" className="button button-primary button-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <section className="hero-section">
        <div className="hero-background">
          <div className="glow-orb primary"></div>
          <div className="glow-orb secondary"></div>
          <div className="grid-overlay"></div>
        </div>
        
        <motion.div 
          className="hero-content"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <motion.div variants={fadeIn} className="trust-badge">
            <ShieldCheck size={14} /> ENFORCED POLICY BOUNDARY ACTIVE
          </motion.div>
          
          <motion.h1 variants={fadeIn}>
            Turn Intent Into <br />
            <span className="text-gradient">Controlled Execution.</span>
          </motion.h1>
          
          <motion.p variants={fadeIn} className="hero-subtitle">
            VOID is a governed AI execution platform that coordinates models, agents, tools, workflows, knowledge, and artifacts under your exact rules.
          </motion.p>
          
          <motion.div variants={fadeIn} className="hero-actions">
            <Link href="/sign-up" className="button button-primary button-lg">
              Start Building <ArrowRight size={18} />
            </Link>
            <a href="#how-it-works" className="button button-secondary button-lg">
              Explore VOID
            </a>
          </motion.div>

          {/* Animated Command Preview */}
          <motion.div variants={fadeIn} className="hero-terminal-wrapper">
            <div className="hero-terminal glass-panel">
              <div className="terminal-header">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
                <span className="terminal-title">void / mission-control</span>
              </div>
              <div className="terminal-body">
                <p><span className="prompt">&gt;</span> <span className="typing-text">Analyze Q3 financial reports and cross-reference with risk policies.</span></p>
                <div className="terminal-response">
                  <p className="text-muted">Initializing Intent Gate...</p>
                  <p className="text-info">[✓] Intent validated.</p>
                  <p className="text-muted">Evaluating execution strategies...</p>
                  <p className="text-success">[✓] AUTO strategy selected within risk budget.</p>
                  <p className="text-muted">Allocating agents and tools...</p>
                  <div className="progress-bar-container"><div className="progress-bar animate-progress"></div></div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* 3. TRUST STRIP */}
      <section className="trust-strip">
        <div className="trust-strip-container">
          <div className="trust-item"><Lock size={20} /> Policy-aware execution</div>
          <div className="trust-item"><Target size={20} /> Project-scoped access</div>
          <div className="trust-item"><Activity size={20} /> Observable missions</div>
          <div className="trust-item"><CheckCircle size={20} /> Validation-first workflows</div>
          <div className="trust-item"><FileText size={20} /> Evidence-backed outputs</div>
        </div>
      </section>

      {/* 4. WHAT VOID SOLVES */}
      <section id="product" className="section">
        <motion.div 
          className="section-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeIn} className="section-header">
            <h2>The Chaos of Fragmented AI. <br />The Order of VOID.</h2>
            <p>Uncontrolled agents lead to unpredictable risks. We built a unified control layer.</p>
          </motion.div>

          <div className="solutions-grid">
            <motion.div variants={fadeIn} className="solution-card glass-card">
              <div className="solution-icon danger"><AlertTriangle size={24} /></div>
              <h3>Fragmented Tools</h3>
              <p>Models don&apos;t share context or boundaries.</p>
              <div className="solution-arrow"><ArrowRight size={16} /></div>
              <h4 className="text-success">Unified Fabric</h4>
              <p className="text-muted">A single execution layer mapping intents to precise capabilities.</p>
            </motion.div>

            <motion.div variants={fadeIn} className="solution-card glass-card">
              <div className="solution-icon danger"><Command size={24} /></div>
              <h3>Unpredictable Agents</h3>
              <p>Agents hallucinate or get stuck in loops.</p>
              <div className="solution-arrow"><ArrowRight size={16} /></div>
              <h4 className="text-success">Governed Orchestration</h4>
              <p className="text-muted">Strict validation checks and human-in-the-loop approvals.</p>
            </motion.div>

            <motion.div variants={fadeIn} className="solution-card glass-card">
              <div className="solution-icon danger"><ShieldAlert size={24} /></div>
              <h3>Unclear Permissions</h3>
              <p>Data access leaks across different tools.</p>
              <div className="solution-arrow"><ArrowRight size={16} /></div>
              <h4 className="text-success">Zero-Trust Boundaries</h4>
              <p className="text-muted">Project-scoped isolation with RBAC and explicit ownership.</p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* 5. HOW VOID WORKS */}
      <section id="how-it-works" className="section alt-bg">
        <motion.div 
          className="section-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeIn} className="section-header">
            <h2>How VOID Works</h2>
            <p>From human intent to verifiable evidence.</p>
          </motion.div>

          <div className="workflow-diagram">
            <div className="flow-step">
              <div className="flow-icon"><Command /></div>
              <h4>1. Human Intent</h4>
            </div>
            <div className="flow-connector"></div>
            <div className="flow-step">
              <div className="flow-icon"><GitBranch /></div>
              <h4>2. Strategy Resolver</h4>
            </div>
            <div className="flow-connector"></div>
            <div className="flow-step">
              <div className="flow-icon"><ShieldCheck /></div>
              <h4>3. Policy Evaluation</h4>
            </div>
            <div className="flow-connector"></div>
            <div className="flow-step">
              <div className="flow-icon"><Server /></div>
              <h4>4. Execution Fabric</h4>
            </div>
            <div className="flow-connector"></div>
            <div className="flow-step">
              <div className="flow-icon"><CheckCircle /></div>
              <h4>5. Validation & Evidence</h4>
            </div>
          </div>
        </motion.div>
      </section>

      {/* 6. CORE CAPABILITIES */}
      <section id="capabilities" className="section">
        <motion.div 
          className="section-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeIn} className="section-header">
            <h2>Core Capabilities</h2>
            <p>Enterprise-grade tooling out of the box.</p>
          </motion.div>

          <div className="capabilities-grid">
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <Zap className="capability-icon" />
              <h3>Universal Command</h3>
              <p>One prompt interface to trigger any workflow, agent, or tool.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <Box className="capability-icon" />
              <h3>Mission Control</h3>
              <p>Monitor real-time task progression, logs, and state.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <Search className="capability-icon" />
              <h3>Document Intelligence</h3>
              <p>Advanced RAG and structured extraction from complex PDFs.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <FileText className="capability-icon" />
              <h3>Resume/JD Analysis</h3>
              <p>Deterministic, bias-free candidate profiling.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <Target className="capability-icon" />
              <h3>Artifact Management</h3>
              <p>Track, version, and cryptographically hash generated files.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="capability-card glass-card">
              <ShieldCheck className="capability-icon" />
              <h3>Audit & Evaluation</h3>
              <p>Comprehensive event logs for compliance and debugging.</p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* 7. SECURITY-FIRST SECTION */}
      <section id="security" className="section alt-bg">
        <div className="section-container split-layout">
          <motion.div 
            className="split-content"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
          >
            <motion.h2 variants={fadeIn}>Security is not an afterthought.</motion.h2>
            <motion.p variants={fadeIn} className="text-muted mb-6">
              VOID implements strict defense-in-depth methodologies to ensure your AI execution stays within defined risk parameters.
            </motion.p>
            <ul className="feature-list">
              <motion.li variants={fadeIn}><CheckCircle size={18} className="text-success" /> Project-level tenant isolation</motion.li>
              <motion.li variants={fadeIn}><CheckCircle size={18} className="text-success" /> Explicit Role-Based Access Control</motion.li>
              <motion.li variants={fadeIn}><CheckCircle size={18} className="text-success" /> Tamper-resistant Audit Trails</motion.li>
              <motion.li variants={fadeIn}><CheckCircle size={18} className="text-success" /> Pre-execution policy enforcement</motion.li>
            </ul>
          </motion.div>
          <motion.div 
            className="split-visual glass-panel"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="code-snippet">
              <pre>
{`{
  "policy": "DENY_BY_DEFAULT",
  "resource": "mission:execute",
  "context": {
    "project_id": "prj_8x92a",
    "risk_level": "HIGH"
  },
  "action": "REQUIRE_APPROVAL",
  "reason": "Budget limit exceeded"
}`}
              </pre>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 8. EXECUTION MODES */}
      <section className="section">
        <motion.div 
          className="section-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeIn} className="section-header">
            <h2>Three Modes of Control</h2>
            <p>Scale automation based on your trust and risk appetite.</p>
          </motion.div>

          <div className="modes-grid">
            <motion.div variants={fadeIn} className="mode-card glass-card">
              <div className="mode-header">
                <h3>AUTO</h3>
                <span className="badge success">Fastest</span>
              </div>
              <p>VOID selects the execution strategy and proceeds autonomously within configured policies.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="mode-card glass-card">
              <div className="mode-header">
                <h3>GUIDED</h3>
                <span className="badge warning">Balanced</span>
              </div>
              <p>VOID plans the execution, pauses, and requires human approval before dispatching agents.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="mode-card glass-card">
              <div className="mode-header">
                <h3>MANUAL</h3>
                <span className="badge neutral">Max Control</span>
              </div>
              <p>You explicitly select models, tools, and workflows for every step of the mission.</p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* 10. FINAL CTA */}
      <section className="cta-section">
        <div className="glow-orb primary centered"></div>
        <motion.div 
          className="cta-content"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2>Your intent. Your policies. Your execution layer.</h2>
          <div className="cta-actions">
            <Link href="/sign-up" className="button button-primary button-xl">
              Create Your VOID Workspace
            </Link>
          </div>
        </motion.div>
      </section>

      {/* 11. FOOTER */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-brand">
            <span className="brand-orbit">◌</span>
            <span className="brand-text"><strong>VOID</strong></span>
            <p className="footer-desc">Versatile Orchestrated Intelligent Dispatcher</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>Product</h4>
              <a href="#product">Platform</a>
              <a href="#capabilities">Capabilities</a>
              <a href="#security">Security</a>
            </div>
            <div className="footer-column">
              <h4>Resources</h4>
              <a href="#">Documentation</a>
              <a href="#">API Reference</a>
              <a href="https://github.com/shivaganesh720/void" target="_blank" rel="noreferrer">GitHub</a>
            </div>
            <div className="footer-column">
              <h4>Legal (Pending Review)</h4>
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
              <a href="#">Security Disclosure</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 VOID Operations. All systems governed.</p>
          <p className="version-info">v0.1.0-alpha</p>
        </div>
      </footer>
    </div>
  );
}
