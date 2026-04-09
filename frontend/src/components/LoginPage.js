import React, { useState } from 'react';

/* ─────────────────────────────────────────────────────────
   PrepGenie — Login Pages (matches Stitch "Genie Blueprint")
   Student login  → role = 'student'
   Admin login    → role = 'admin'
   Demo login     → skips credentials entirely
───────────────────────────────────────────────────────── */

// Hardcoded demo credentials (no real auth needed for hackathon)
const STUDENT_CREDENTIALS = { id: 'STU001', password: 'student123' };
const ADMIN_CREDENTIALS   = { id: 'ADMIN001', password: 'admin123' };

/* ══════════════════ STUDENT LOGIN ══════════════════ */
export function StudentLogin({ onLogin }) {
  const [form, setForm] = useState({ id: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTimeout(() => {
      if (form.id === STUDENT_CREDENTIALS.id && form.password === STUDENT_CREDENTIALS.password) {
        onLogin({ role: 'student', name: 'Ayush Jha', id: form.id });
      } else {
        setError('Invalid Student ID or password. Try STU001 / student123');
      }
      setLoading(false);
    }, 600);
  };

  const demoLogin = () => {
    setLoading(true);
    setTimeout(() => onLogin({ role: 'student', name: 'Demo Student', id: 'DEMO' }), 400);
  };

  return (
    <div className="login-shell">
      {/* AI Active badge */}
      <div className="ai-badge">
        <span className="ai-dot" />
        AI Active
      </div>

      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">
          <span className="login-logo-icon">🚀</span>
          <span className="login-logo-text">PrepGenie</span>
          <span className="login-logo-sub">Your AI Placement OS</span>
        </div>

        <h1 className="login-headline">Welcome Back, Student</h1>
        <p className="login-subtext">Sign in to access your personalized roadmap and AI insights</p>

        <form onSubmit={submit} className="login-form">
          <div className="login-field">
            <label htmlFor="student-id">Student ID</label>
            <input
              id="student-id"
              name="id"
              type="text"
              placeholder="e.g. STU001"
              value={form.id}
              onChange={handle}
              className="login-input"
              required
            />
          </div>
          <div className="login-field">
            <label htmlFor="student-pass">Password</label>
            <input
              id="student-pass"
              name="password"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handle}
              className="login-input"
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="login-btn-primary" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In to Dashboard'}
          </button>
        </form>

        <div className="login-divider"><span>OR</span></div>

        <button onClick={demoLogin} className="login-btn-demo" disabled={loading}>
          ⚡ Try Demo Student Account
        </button>

        <p className="login-register">
          New Student? <span className="login-link">Register with institution code</span>
        </p>

        <div className="login-switch">
          <span>Are you an admin?</span>
          <a href="/admin-login" className="login-switch-link" onClick={(e) => {
            e.preventDefault();
            window.dispatchEvent(new CustomEvent('switchLogin', { detail: 'admin' }));
          }}>
            Admin Login →
          </a>
        </div>
      </div>
    </div>
  );
}

/* ══════════════════ ADMIN LOGIN ══════════════════ */
export function AdminLogin({ onLogin }) {
  const [form, setForm] = useState({ id: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTimeout(() => {
      if (form.id === ADMIN_CREDENTIALS.id && form.password === ADMIN_CREDENTIALS.password) {
        onLogin({ role: 'admin', name: 'Admin User', id: form.id });
      } else {
        setError('Invalid Admin credentials. Try ADMIN001 / admin123');
      }
      setLoading(false);
    }, 600);
  };

  const demoAdmin = () => {
    setLoading(true);
    setTimeout(() => onLogin({ role: 'admin', name: 'Demo Admin', id: 'DEMO_ADMIN' }), 400);
  };

  return (
    <div className="login-shell admin-login-shell">
      {/* Split screen */}
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
        <p className="admin-left-tagline">Monitoring placements across 4 branches with 5 AI agents</p>
      </div>

      <div className="admin-right-panel">
        <div className="admin-access-badge">
          🛡️ Admin Access Only
        </div>

        <h1 className="login-headline">Placement Control Center</h1>
        <p className="login-subtext">Restricted to authorized placement coordinators only</p>

        <form onSubmit={submit} className="login-form">
          <div className="login-field">
            <label htmlFor="admin-id">Admin ID / Email</label>
            <input
              id="admin-id"
              name="id"
              type="text"
              placeholder="e.g. ADMIN001"
              value={form.id}
              onChange={handle}
              className="login-input"
              required
            />
          </div>
          <div className="login-field">
            <label htmlFor="admin-pass">Password</label>
            <input
              id="admin-pass"
              name="password"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handle}
              className="login-input"
              required
            />
          </div>
          <label className="login-remember">
            <input type="checkbox" /> Remember this device
          </label>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="login-btn-primary" disabled={loading}>
            {loading ? 'Authenticating…' : 'Access Admin Dashboard'}
          </button>
        </form>

        <button onClick={demoAdmin} className="login-btn-demo" style={{ marginTop: 12 }} disabled={loading}>
          ⚡ Demo Admin Access
        </button>

        <p className="login-forgot">Forgot admin credentials? Contact IT support</p>

        <div className="login-switch">
          <span>Student?</span>
          <a href="/student-login" className="login-switch-link" onClick={(e) => {
            e.preventDefault();
            window.dispatchEvent(new CustomEvent('switchLogin', { detail: 'student' }));
          }}>
            Student Login here →
          </a>
        </div>
      </div>
    </div>
  );
}
