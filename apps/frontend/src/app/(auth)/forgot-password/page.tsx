"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ArrowRight, Mail } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await fetch(`${API_BASE}/api/v1/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      setSent(true);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-split-layout auth-centered">
      <div className="auth-form-card glass-panel">
        <div className="auth-form-header">
          <Link href="/" className="auth-brand auth-brand-small">
            <span className="auth-brand-orbit">◌</span>
            <span className="auth-brand-name">VOID</span>
          </Link>
          <p className="auth-eyebrow">ACCOUNT RECOVERY</p>
          <h2>Reset your password</h2>
          <p className="auth-form-subtext">
            Enter your email and we&apos;ll send you a reset link if an account exists.
          </p>
        </div>

        {sent ? (
          <div className="auth-success-banner">
            <Mail size={20} />
            <div>
              <strong>Check your inbox</strong>
              <p>A reset link has been sent to <strong>{email}</strong>. Check your spam folder if it doesn&apos;t arrive within a few minutes.</p>
            </div>
          </div>
        ) : (
          <form onSubmit={submit} className="auth-form">
            <div className="auth-field">
              <label htmlFor="forgot-email">Email address</label>
              <input
                id="forgot-email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {error && (
              <div className="auth-error-banner" role="alert">{error}</div>
            )}

            <button
              type="submit"
              className="button button-primary button-auth"
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : <>Send reset link <ArrowRight size={16} /></>}
            </button>
          </form>
        )}

        <p className="auth-switch-text">
          <Link href="/sign-in">← Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
