import React, { useState } from 'react';
import { supabase } from '../lib/supabase';

/* ─────────────────────────────────────────────────────────
   PrepGenie — Login Pages with Supabase Auth
   Student login  → Google OAuth or Phone OTP → role = 'student'
   Admin login    → Google OAuth or Phone OTP → role = 'admin'
   Demo login     → skips Supabase entirely (hackathon fallback)
───────────────────────────────────────────────────────── */

/* ══════════════════ GOOGLE ICON SVG ══════════════════ */
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" style={{ marginRight: 8, flexShrink: 0 }}>
      <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/>
      <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
      <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"/>
      <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z"/>
    </svg>
  );
}

/* ══════════════════ PHONE OTP FORM ══════════════════ */
function PhoneOTPForm({ role, onLogin }) {
  const [phone, setPhone]     = useState('');
  const [otp, setOtp]         = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [info, setInfo]       = useState('');

  /* ── Send OTP ── */
  const sendOtp = async (e) => {
    e.preventDefault();
    if (!phone.trim()) { setError('Enter a phone number'); return; }
    setLoading(true);
    setError('');
    setInfo('');

    const { error: err } = await supabase.auth.signInWithOtp({ phone: phone.trim() });
    setLoading(false);

    if (err) {
      setError(err.message);
    } else {
      setOtpSent(true);
      setInfo(`OTP sent to ${phone}. Check your messages.`);
    }
  };

  /* ── Verify OTP ── */
  const verifyOtp = async (e) => {
    e.preventDefault();
    if (!otp.trim()) { setError('Enter the OTP'); return; }
    setLoading(true);
    setError('');

    const { data, error: err } = await supabase.auth.verifyOtp({
      phone: phone.trim(),
      token: otp.trim(),
      type: 'sms',
    });
    setLoading(false);

    if (err) {
      setError(err.message);
      return;
    }

    const user = data?.user;
    if (user) {
      /* Upsert role into profiles table */
      await supabase.from('profiles').upsert({
        id: user.id,
        email: user.email || null,
        role,
      });

      onLogin({
        role,
        name: user.phone || user.email || (role === 'admin' ? 'Admin User' : 'Student'),
        id: user.id,
        supabaseUser: user,
      });
    }
  };

  return (
    <>
      {!otpSent ? (
        <form onSubmit={sendOtp} className="login-form">
          <div className="login-field">
            <label htmlFor={`phone-${role}`}>Phone Number</label>
            <input
              id={`phone-${role}`}
              type="tel"
              placeholder="+91 9876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="login-input"
              required
              disabled={loading}
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="login-btn-primary" disabled={loading}>
            {loading ? 'Sending OTP…' : 'Send OTP →'}
          </button>
        </form>
      ) : (
        <form onSubmit={verifyOtp} className="login-form">
          {info && <div className="login-info">{info}</div>}
          <div className="login-field">
            <label htmlFor={`otp-${role}`}>Enter OTP</label>
            <input
              id={`otp-${role}`}
              type="text"
              inputMode="numeric"
              placeholder="6-digit code"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="login-input otp-input"
              required
              disabled={loading}
              autoFocus
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="login-btn-primary" disabled={loading}>
            {loading ? 'Verifying…' : 'Verify & Sign In'}
          </button>
          <button
            type="button"
            className="login-btn-ghost"
            onClick={() => { setOtpSent(false); setOtp(''); setError(''); setInfo(''); }}
            disabled={loading}
          >
            ← Change number
          </button>
        </form>
      )}

      {/* Demo button removed — use real authentication only */}
    </>
  );
}

/* ══════════════════ STUDENT LOGIN ══════════════════ */
export function StudentLogin({ onLogin }) {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  /* ── Google OAuth ── */
  const signInWithGoogle = async () => {
    setLoading(true);
    setError('');
    const { error: err } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/auth/callback?role=student',
        queryParams: { prompt: 'select_account' },
      },
    });
    if (err) { setError(err.message); setLoading(false); }
    /* On success Supabase redirects — no further action needed */
  };

  /* ── Demo removed — use real Supabase auth ── */

  return (
    <div className="login-shell">
      <div className="ai-badge">
        <span className="ai-dot" />
        AI Active
      </div>

      <div className="login-card">
        <div className="login-logo">
          <span className="login-logo-icon">🚀</span>
          <span className="login-logo-text">PrepGenie</span>
          <span className="login-logo-sub">Your AI Placement OS</span>
        </div>

        <h1 className="login-headline">Welcome Back, Student</h1>
        <p className="login-subtext">Sign in to access your personalized roadmap and AI insights</p>

        {/* Google OAuth */}
        <button
          id="student-google-btn"
          className="login-btn-google"
          onClick={signInWithGoogle}
          disabled={loading}
        >
          <GoogleIcon />
          {loading ? 'Redirecting…' : 'Continue with Google'}
        </button>

        <div className="login-divider"><span>OR use phone</span></div>

        {error && <div className="login-error" style={{ marginBottom: 12 }}>{error}</div>}

        {/* Phone OTP */}
        <PhoneOTPForm role="student" onLogin={onLogin} />

        <div className="login-switch">
          <span>Admin?</span>
          <a
            href="/admin-login"
            className="login-switch-link"
            onClick={(e) => {
              e.preventDefault();
              window.dispatchEvent(new CustomEvent('switchLogin', { detail: 'admin' }));
            }}
          >
            Login here →
          </a>
        </div>
      </div>
    </div>
  );
}

/* ══════════════════ ADMIN LOGIN ══════════════════ */
export function AdminLogin({ onLogin }) {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');

  /* ── Email / Password sign-in ── */
  const submit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }
    setLoading(true);
    setError('');

    /* 1. Sign in with Supabase */
    const { data: authData, error: authErr } =
      await supabase.auth.signInWithPassword({ email: email.trim(), password });

    if (authErr) {
      setError(authErr.message);
      setLoading(false);
      return;
    }

    const user = authData?.user;
    if (!user) {
      setError('Login failed. Please try again.');
      setLoading(false);
      return;
    }

    /* 2. Check profiles table for role === 'admin' */
    const { data: profile, error: profileErr } = await supabase
      .from('profiles')
      .select('role, full_name')
      .eq('id', user.id)
      .single();

    if (profileErr || !profile) {
      await supabase.auth.signOut();
      setError('Could not verify account role. Contact IT support.');
      setLoading(false);
      return;
    }

    if (profile.role !== 'admin') {
      await supabase.auth.signOut();
      setError('Access denied. Not an admin account.');
      setLoading(false);
      return;
    }

    /* 3. Admin confirmed → proceed */
    setLoading(false);
    onLogin({
      role: 'admin',
      name: profile.full_name || user.email || 'Admin',
      id: user.id,
      supabaseUser: user,
    });
  };

  /* ── Demo fallback ── */
  const demoAdmin = () => {
    setLoading(true);
    setTimeout(() => onLogin({ role: 'admin', name: 'Demo Admin', id: 'DEMO_ADMIN' }), 400);
  };

  return (
    <div className="login-shell admin-login-shell">
      {/* ── Left panel ── */}
      <div className="admin-left-panel">
        <div className="admin-brand">
          <span className="login-logo-icon">🚀</span>
          <div>
            <div className="admin-brand-name">PrepGenie</div>
            <div className="admin-brand-sub">Placement Control Center</div>
          </div>
        </div>

        <div className="admin-stats-preview">
          <div className="admin-stat-item">
            <span className="admin-stat-number">1,240</span>
            <span className="admin-stat-label">Active Students</span>
          </div>
          <div className="admin-stat-item">
            <span className="admin-stat-number text-warn">12</span>
            <span className="admin-stat-label">At-Risk Alerts</span>
          </div>
          <div className="admin-stat-item">
            <span className="admin-stat-number text-success">89</span>
            <span className="admin-stat-label">Job Ready</span>
          </div>
          <div className="admin-stat-item">
            <span className="admin-stat-number">67%</span>
            <span className="admin-stat-label">Avg Probability</span>
          </div>
        </div>

        <div className="admin-left-glow" />
        <p className="admin-left-tagline">
          Monitoring placements across 4 branches with 5 AI agents
        </p>
      </div>

      {/* ── Right panel ── */}
      <div className="admin-right-panel">
        <div className="admin-access-badge">🛡️ Admin Access Only</div>

        <h1 className="login-headline">Placement Control Center</h1>
        <p className="login-subtext">Restricted to authorized placement coordinators only</p>

        {/* Error alert */}
        {error && (
          <div className="admin-login-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Email / Password form */}
        <form onSubmit={submit} className="login-form">
          <div className="login-field">
            <label htmlFor="admin-email">Email Address</label>
            <input
              id="admin-email"
              type="email"
              placeholder="admin@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="login-input"
              required
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="login-field">
            <label htmlFor="admin-password">Password</label>
            <input
              id="admin-password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input"
              required
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button
            id="admin-login-btn"
            type="submit"
            className="login-btn-admin-primary"
            disabled={loading}
          >
            {loading ? 'Authenticating…' : '🔐 Access Admin Dashboard'}
          </button>
        </form>

        <button
          onClick={demoAdmin}
          className="login-btn-demo"
          style={{ marginTop: 12 }}
          disabled={loading}
        >
          ⚡ Demo Admin Access
        </button>

        <p className="login-forgot">Forgot credentials? Contact your IT administrator</p>

        <div className="login-switch">
          <span>Student?</span>
          <a
            href="/student-login"
            className="login-switch-link"
            onClick={(e) => {
              e.preventDefault();
              window.dispatchEvent(new CustomEvent('switchLogin', { detail: 'student' }));
            }}
          >
            Login here →
          </a>
        </div>
      </div>
    </div>
  );
}
