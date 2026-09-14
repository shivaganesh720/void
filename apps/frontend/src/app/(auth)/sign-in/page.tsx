"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, ArrowRight, ShieldCheck } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data?.error?.message ?? "We couldn't sign you in with those details.");
      }
      const next = new URLSearchParams(window.location.search).get("next");
      router.replace(next?.startsWith("/") ? next : "/workspace");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-split-layout">
      {/* Left visual panel */}
      <div className="auth-split-left">
        <div className="auth-split-left-bg">
          <div className="auth-glow-orb purple" />
          <div className="auth-glow-orb cyan" />
        </div>
        <div className="auth-split-left-content">
          <Link href="/" className="auth-brand">
            <span className="auth-brand-orbit">◌</span>
            <span className="auth-brand-name">VOID</span>
          </Link>
          <div className="auth-split-tagline">
            <p className="auth-split-eyebrow">WELCOME BACK</p>
            <h1 className="auth-split-heading">
              Pick up where your<br />
              <span className="auth-split-accent">intent left off.</span>
            </h1>
            <p className="auth-split-desc">
              Resume missions, review evidence, and continue governed execution with clarity.
            </p>
          </div>
          <div className="auth-trust-badges">
            <div className="auth-trust-badge"><ShieldCheck size={14} /> Policy boundary online</div>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-split-right">
        <div className="auth-form-card glass-panel">
          <div className="auth-form-header">
            <p className="auth-eyebrow">SIGN IN</p>
            <h2>Welcome back to VOID</h2>
            <p className="auth-form-subtext">Enter your account details to continue.</p>
          </div>

          <form onSubmit={submit} className="auth-form">
            <div className="auth-field">
              <label htmlFor="signin-email">Email address</label>
              <input
                id="signin-email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="auth-field">
              <label htmlFor="signin-password">Password</label>
              <div className="auth-password-wrap">
                <input
                  id="signin-password"
                  type={show ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShow(!show)}
                  aria-label={show ? "Hide password" : "Show password"}
                >
                  {show ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="auth-form-meta">
              <label className="auth-remember">
                <input type="checkbox" />
                <span>Remember this device</span>
              </label>
              <Link href="/forgot-password" className="auth-forgot-link">
                Forgot password?
              </Link>
            </div>

            {error && (
              <div className="auth-error-banner" role="alert">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="button button-primary button-auth"
              disabled={loading}
            >
              {loading ? (
                <span className="auth-spinner" />
              ) : (
                <>Sign in <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          <p className="auth-switch-text">
            Don&apos;t have an account?{" "}
            <Link href="/sign-up">Create your VOID account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
