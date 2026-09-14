"use client";

import Link from "next/link";
import { FormEvent, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowRight, Eye, EyeOff, CheckCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (password !== confirm) { setError("Passwords do not match."); return; }
    if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password)) {
      setError("Password must be 8+ chars with uppercase, lowercase and number.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.error?.message ?? "Invalid or expired reset token.");
      }
      setDone(true);
      setTimeout(() => router.replace("/sign-in"), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="auth-error-banner">
        Invalid reset link. Please request a new password reset.
      </div>
    );
  }

  if (done) {
    return (
      <div className="auth-success-banner">
        <CheckCircle size={20} />
        <div>
          <strong>Password reset successfully</strong>
          <p>Redirecting you to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="auth-form">
      <div className="auth-field">
        <label htmlFor="reset-password">New password</label>
        <div className="auth-password-wrap">
          <input
            id="reset-password"
            type={show ? "text" : "password"}
            required
            autoComplete="new-password"
            placeholder="Min. 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="button" className="auth-password-toggle" onClick={() => setShow(!show)} aria-label="Toggle password">
            {show ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>
      <div className="auth-field">
        <label htmlFor="reset-confirm">Confirm new password</label>
        <input
          id="reset-confirm"
          type="password"
          required
          autoComplete="new-password"
          placeholder="Re-enter password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
      </div>
      {error && <div className="auth-error-banner" role="alert">{error}</div>}
      <button type="submit" className="button button-primary button-auth" disabled={loading}>
        {loading ? <span className="auth-spinner" /> : <>Set new password <ArrowRight size={16} /></>}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="auth-split-layout auth-centered">
      <div className="auth-form-card glass-panel">
        <div className="auth-form-header">
          <Link href="/" className="auth-brand auth-brand-small">
            <span className="auth-brand-orbit">◌</span>
            <span className="auth-brand-name">VOID</span>
          </Link>
          <p className="auth-eyebrow">PASSWORD RESET</p>
          <h2>Set a new password</h2>
          <p className="auth-form-subtext">Choose a strong password to secure your account.</p>
        </div>
        <Suspense fallback={<div className="auth-spinner-center"><span className="auth-spinner" /></div>}>
          <ResetForm />
        </Suspense>
        <p className="auth-switch-text">
          <Link href="/sign-in">← Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
