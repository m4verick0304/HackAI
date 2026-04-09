import React, { useState, useEffect } from 'react';
import './index.css';
import { StudentLogin, AdminLogin } from './components/LoginPage';
import StudentDashboard from './components/StudentDashboard';
import AdminDashboard from './components/AdminDashboard';
import InsightsPanel from './components/InsightsPanel';

/*
  PrepGenie App — Auth-gated routing
  ─────────────────────────────────────────────────────────
  Routes:
    /  (no auth)  → Landing: choose Student or Admin login
    student login → student-only views (Dashboard + AI Insights)
    admin login   → admin-only view (Admin Dashboard)
  ─────────────────────────────────────────────────────────
*/

function App() {
  // auth = null | { role: 'student'|'admin', name, id }
  const [auth, setAuth] = useState(null);
  // loginView = 'landing' | 'student' | 'admin'
  const [loginView, setLoginView] = useState('landing');
  // Active tab within student portal
  const [activeTab, setActiveTab] = useState('student');
  const [sharedStudentData, setSharedStudentData] = useState(null);

  // Listen for cross-component login switch events
  useEffect(() => {
    const handler = (e) => setLoginView(e.detail);
    window.addEventListener('switchLogin', handler);
    return () => window.removeEventListener('switchLogin', handler);
  }, []);

  const handleLogin = (userData) => {
    setAuth(userData);
    setActiveTab(userData.role === 'admin' ? 'admin' : 'student');
  };

  const handleLogout = () => {
    setAuth(null);
    setLoginView('landing');
    setSharedStudentData(null);
  };

  /* ── NOT LOGGED IN ─────────────────────────────────── */
  if (!auth) {
    if (loginView === 'student') {
      return <StudentLogin onLogin={handleLogin} />;
    }
    if (loginView === 'admin') {
      return <AdminLogin onLogin={handleLogin} />;
    }

    // Landing page — choose portal
    return (
      <div className="landing-shell">
        <div className="landing-content">
          <div className="landing-logo">
            <span className="brand-icon" style={{ fontSize: 48 }}>🚀</span>
            <h1 className="landing-title">PrepGenie</h1>
            <p className="landing-sub">Your AI-Powered Placement OS</p>
          </div>

          <div className="landing-tagline">
            <span className="landing-tag">PlannerAgent</span>
            <span className="landing-tag">EvaluatorAgent</span>
            <span className="landing-tag">SimulatorAgent</span>
            <span className="landing-tag">StrategistAgent</span>
            <span className="landing-tag">DecisionAgent</span>
          </div>

          <p className="landing-desc">
            An autonomous agentic AI system that manages your entire placement journey —
            from resume to offer letter.
          </p>

          <div className="landing-portals">
            <button
              className="portal-card student-portal"
              onClick={() => setLoginView('student')}
            >
              <span className="portal-icon">🎓</span>
              <div className="portal-info">
                <div className="portal-title">Student Portal</div>
                <div className="portal-desc">Access your roadmap, track tasks, run AI simulations</div>
              </div>
              <span className="portal-arrow">→</span>
            </button>

            <button
              className="portal-card admin-portal"
              onClick={() => setLoginView('admin')}
            >
              <span className="portal-icon">📋</span>
              <div className="portal-info">
                <div className="portal-title">Admin Portal</div>
                <div className="portal-desc">Monitor students, view AI insights, manage cohorts</div>
              </div>
              <span className="portal-arrow">→</span>
            </button>
          </div>

          <p className="landing-hint">
            Demo credentials — Student: <code>STU001 / student123</code> &nbsp;|&nbsp; Admin: <code>ADMIN001 / admin123</code>
          </p>
        </div>
      </div>
    );
  }

  /* ── LOGGED IN — STUDENT ────────────────────────────── */
  if (auth.role === 'student') {
    return (
      <div className="app-shell">
        <nav className="navbar">
          <button className="navbar-brand" onClick={() => setActiveTab('student')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <span className="brand-icon">🚀</span> PrepGenie
          </button>

          <div className="navbar-tabs">
            <button
              className={`nav-tab ${activeTab === 'student' ? 'active' : ''}`}
              onClick={() => setActiveTab('student')}
            >🎓 Dashboard</button>
            <button
              className={`nav-tab ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >🤖 AI Insights</button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div className="navbar-badge">
              <div className="status-dot" />
              <span style={{ fontSize: 13, color: '#64748b' }}>AI Active</span>
            </div>
            <span style={{ fontSize: 13, color: '#64748b' }}>👤 {auth.name}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </nav>

        <main className="page-content">
          {activeTab === 'student' && (
            <StudentDashboard onDataUpdate={setSharedStudentData} />
          )}
          {activeTab === 'insights' && (
            <InsightsPanel studentData={sharedStudentData} />
          )}
        </main>

        <footer className="app-footer">
          PrepGenie — Agentic AI Placement Engine · Student Portal · Built for Hackathon 2026
        </footer>
      </div>
    );
  }

  /* ── LOGGED IN — ADMIN ──────────────────────────────── */
  if (auth.role === 'admin') {
    return (
      <div className="app-shell">
        <nav className="navbar admin-navbar">
          <button className="navbar-brand" onClick={() => {}}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <span className="brand-icon">🚀</span> PrepGenie
            <span className="admin-nav-badge">ADMIN</span>
          </button>

          <div className="navbar-tabs">
            <button className="nav-tab active">📋 Admin Dashboard</button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div className="navbar-badge">
              <div className="status-dot" />
              <span style={{ fontSize: 13, color: '#64748b' }}>AI Active</span>
            </div>
            <span style={{ fontSize: 13, color: '#64748b' }}>🛡️ {auth.name}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </nav>

        <main className="page-content">
          <AdminDashboard />
        </main>

        <footer className="app-footer">
          PrepGenie — Agentic AI Placement Engine · Admin Portal · Built for Hackathon 2026
        </footer>
      </div>
    );
  }

  return null;
}

export default App;
