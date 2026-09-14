"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, ArrowRight, CheckCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "8+ characters", pass: password.length >= 8 },
    { label: "Uppercase letter", pass: /[A-Z]/.test(password) },
    { label: "Lowercase letter", pass: /[a-z]/.test(password) },
    { label: "Number", pass: /\d/.test(password) },
  ];
  if (!password) return null;
  return (
    <div className="password-strength">
      {checks.map((c) => (
        <span key={c.label} className={`strength-check ${c.pass ? "pass" : "fail"}`}>
          <CheckCircle size={11} /> {c.label}
        </span>
      ))}
    </div>
  );
}

export default function SignUpPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");

    if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password)) {
      setError("Use at least 8 characters with uppercase, lowercase, and a number.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const reg = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: fullName, email, password }),
      });
      const regData = await reg.json().catch(() => ({}));
      if (!reg.ok) throw new Error(regData?.error?.message ?? regData?.detail ?? "We couldn't create your account.");

      const login = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      if (!login.ok) throw new Error("Account created. Please sign in.");

      router.replace("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-split-layout">
      {/* Left visual panel */}
      <div className="auth-split-left">
        <div className="auth-split-left-bg">
          <div className="auth-glow-orb cyan" />
          <div className="auth-glow-orb purple bottom" />
        </div>
        <div className="auth-split-left-content">
          <Link href="/" className="auth-brand">
            <span className="auth-brand-orbit">◌</span>
            <span className="auth-brand-name">VOID</span>
          </Link>
          <div className="auth-split-tagline">
            <p className="auth-split-eyebrow">A BETTER WAY TO WORK</p>
            <h1 className="auth-split-heading">
              Start with your<br />
              <span className="auth-split-accent">intent.</span>
            </h1>
            <p className="auth-split-desc">
              Describe what you need. VOID handles the complexity — governed, observable, and evidence-backed.
            </p>
          </div>
          <div className="auth-feature-list">
            <div className="auth-feature-item"><CheckCircle size={14} /> Policy-aware execution</div>
            <div className="auth-feature-item"><CheckCircle size={14} /> Zero-trust project boundaries</div>
            <div className="auth-feature-item"><CheckCircle size={14} /> Real-time mission observability</div>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-split-right">
        <div className="auth-form-card glass-panel">
          <div className="auth-form-header">
            <p className="auth-eyebrow">CREATE ACCOUNT</p>
            <h2>Create your VOID account</h2>
            <p className="auth-form-subtext">Begin with a simple profile. You can tune execution later.</p>
          </div>

          <form onSubmit={submit} className="auth-form">
            <div className="auth-field">
              <label htmlFor="signup-name">Full name</label>
              <input
                id="signup-name"
                type="text"
                required
                placeholder="Ada Lovelace"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div className="auth-field">
              <label htmlFor="signup-email">Email address</label>
              <input
                id="signup-email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="auth-field">
              <label htmlFor="signup-password">Password</label>
              <div className="auth-password-wrap">
                <input
                  id="signup-password"
                  type={show ? "text" : "password"}
                  required
                  autoComplete="new-password"
                  placeholder="Min. 8 characters"
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
              <PasswordStrength password={password} />
            </div>

            <div className="auth-field">
              <label htmlFor="signup-confirm">Confirm password</label>
              <input
                id="signup-confirm"
                type="password"
                required
                autoComplete="new-password"
                placeholder="Re-enter password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
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
                <>Create account <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          <p className="auth-switch-text">
            Already have an account?{" "}
            <Link href="/sign-in">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
