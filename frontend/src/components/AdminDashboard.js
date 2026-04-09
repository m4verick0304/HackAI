import React, { useState, useEffect, useCallback } from 'react';
import api from '../api';

// ============================================================
// STATUS BADGE
// ============================================================
function StatusBadge({ status }) {
  const map = {
    'Ready': { cls: 'badge badge-ready', icon: '✅' },
    'Learning': { cls: 'badge badge-learning', icon: '📚' },
    'At Risk': { cls: 'badge badge-at-risk', icon: '🚨' }
  };
  const { cls, icon } = map[status] || map['Learning'];
  return <span className={cls}>{icon} {status}</span>;
}

// ============================================================
// PROBABILITY MINI BAR
// ============================================================
function MiniBar({ value }) {
  const tier = value >= 70 ? 'high' : value >= 40 ? 'medium' : 'low';
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div className="progress-bar-track" style={{ flex: 1, height: 6 }}>
          <div className={`progress-bar-fill ${tier}`} style={{ width: `${value}%` }} />
        </div>
        <span style={{ fontSize: 13, fontWeight: 700, minWidth: 36 }}>{value}%</span>
      </div>
    </div>
  );
}

// ============================================================
// STUDENT DETAIL MODAL
// ============================================================
function StudentModal({ student, onClose }) {
  if (!student) return null;

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', zIndex: 1000, padding: 24
      }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div style={{
        background: '#16181f', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 20, padding: 32, width: '100%', maxWidth: 600,
        maxHeight: '85vh', overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
          <div>
            <h2 style={{ fontFamily: "'Space Grotesk'", fontSize: 22, fontWeight: 700, marginBottom: 6 }}>
              {student.name}
            </h2>
            <div style={{ color: '#94a3b8', fontSize: 14 }}>Target: {student.goal}</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <StatusBadge status={student.status} />
            <button
              onClick={onClose}
              style={{
                background: 'transparent', border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: 8, padding: '6px 12px', color: '#94a3b8',
                cursor: 'pointer', fontSize: 16
              }}
            >✕</button>
          </div>
        </div>

        {/* Probability */}
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>
            <span className="icon">📊</span> Placement Analysis
          </div>
          <div className="progress-wrapper">
            <div className="progress-label">
              <span style={{ color: '#94a3b8', fontSize: 13 }}>Placement Probability</span>
              <span style={{ fontWeight: 700 }}>{student.probability}%</span>
            </div>
            <div className="progress-bar-track">
              <div
                className={`progress-bar-fill ${student.probability >= 70 ? 'high' : student.probability >= 40 ? 'medium' : 'low'}`}
                style={{ width: `${student.probability}%` }}
              />
            </div>
          </div>
          {student.explanation && (
            <div style={{ marginTop: 12, fontSize: 14, color: '#94a3b8', lineHeight: 1.6 }}>
              {student.explanation}
            </div>
          )}
        </div>

        {/* Task Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 10, padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#10b981' }}>{student.tasks_completed}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Tasks Done</div>
          </div>
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#ef4444' }}>{student.tasks_missed}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Tasks Missed</div>
          </div>
        </div>

        {/* Skills */}
        {student.skills?.length > 0 && (
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>
              <span className="icon">🧠</span> Skills
            </div>
            <div className="skill-tags">
              {student.skills.map(s => <span key={s} className="skill-tag">{s}</span>)}
            </div>
          </div>
        )}

        {/* Alerts */}
        {student.alerts?.length > 0 && (
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>
              <span className="icon">⚠️</span> Alerts
            </div>
            {student.alerts.map((a, i) => (
              <div key={i} className="alert alert-warning">{a}</div>
            ))}
          </div>
        )}

        {/* Suggestion */}
        {student.suggestions?.length > 0 && (
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>
              <span className="icon">💡</span> AI Recommendation
            </div>
            <div style={{ fontSize: 14, color: '#94a3b8', lineHeight: 1.6 }}>
              {student.suggestions[0]}
            </div>
          </div>
        )}

        {/* Career Strategy */}
        {student.strategy && (
          <div className="card">
            <div className="card-title" style={{ marginBottom: 10 }}>
              <span className="icon">🎯</span> Career Strategy
            </div>
            <div style={{ fontSize: 14, color: '#94a3b8', lineHeight: 1.6 }}>
              {student.strategy}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// MAIN ADMIN DASHBOARD
// ============================================================
export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [filter, setFilter] = useState('All');

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await api.getAdminData();
      if (result.success) {
        setData(result);
      } else {
        setError('Failed to load admin data.');
      }
    } catch (e) {
      setError('Cannot connect to backend. Make sure Flask server is running on port 5000.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const filteredStudents = data?.students?.filter(s => {
    if (filter === 'All') return true;
    return s.status === filter;
  }) || [];

  if (loading) return (
    <div className="loading-overlay" style={{ minHeight: 300 }}>
      <div className="spinner" />
      <div className="loading-text">Loading admin data...</div>
    </div>
  );

  if (error) return (
    <div className="alert alert-error" style={{ maxWidth: 600, margin: '48px auto' }}>
      ❌ {error}
    </div>
  );

  const { stats = {} } = data || {};

  return (
    <div>
      <div className="section-header">
        <div className="flex justify-between items-center">
          <div>
            <div className="section-title">📋 Admin Dashboard</div>
            <div className="section-subtitle">
              Monitor all students in real-time. At-risk students are prioritized.
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={fetchData}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* STATS GRID */}
      <div className="stats-grid">
        <div className="stat-card purple">
          <div className="stat-label">Total Students</div>
          <div className="stat-value purple">{stats.total || 0}</div>
        </div>
        <div className="stat-card red">
          <div className="stat-label">At Risk 🚨</div>
          <div className="stat-value red">{stats.at_risk || 0}</div>
        </div>
        <div className="stat-card" style={{ '--color': '#f59e0b' }}>
          <div className="stat-label">Learning 📚</div>
          <div className="stat-value" style={{ color: '#f59e0b' }}>{stats.learning || 0}</div>
        </div>
        <div className="stat-card green">
          <div className="stat-label">Job Ready ✅</div>
          <div className="stat-value green">{stats.ready || 0}</div>
        </div>
      </div>

      {/* Secondary stats row */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ flex: 1 }}>
          <div className="stat-label">Avg. Probability</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#a78bfa', marginTop: 4 }}>
            {stats.avg_probability || 0}%
          </div>
        </div>
        <div className="card" style={{ flex: 1 }}>
          <div className="stat-label">At-Risk Rate</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#ef4444', marginTop: 4 }}>
            {stats.total ? Math.round((stats.at_risk / stats.total) * 100) : 0}%
          </div>
        </div>
        <div className="card" style={{ flex: 1 }}>
          <div className="stat-label">Readiness Rate</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#10b981', marginTop: 4 }}>
            {stats.total ? Math.round((stats.ready / stats.total) * 100) : 0}%
          </div>
        </div>
      </div>

      {/* FILTER TABS */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['All', 'At Risk', 'Learning', 'Ready'].map(f => (
          <button
            key={f}
            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilter(f)}
          >
            {f}
            {f === 'At Risk' && stats.at_risk > 0 && (
              <span style={{
                background: '#ef4444', color: 'white',
                borderRadius: 999, padding: '1px 6px', fontSize: 11, marginLeft: 4
              }}>{stats.at_risk}</span>
            )}
          </button>
        ))}
      </div>

      {/* STUDENT TABLE */}
      {filteredStudents.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>👥</div>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>No students yet</div>
          <div className="text-muted text-sm">
            Students will appear here after they generate a plan in the Student Dashboard.
          </div>
        </div>
      ) : (
        <div className="admin-table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Goal</th>
                <th>Status</th>
                <th>Probability</th>
                <th>Tasks Done</th>
                <th>Tasks Missed</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map(student => (
                <tr
                  key={student.id}
                  className={student.status === 'At Risk' ? 'at-risk' : ''}
                >
                  <td>
                    <div style={{ fontWeight: 600, color: '#f1f5f9' }}>{student.name}</div>
                    {student.alerts?.length > 0 && (
                      <div style={{ fontSize: 11, color: '#ef4444', marginTop: 2 }}>
                        ⚠️ {student.alerts.length} alert{student.alerts.length > 1 ? 's' : ''}
                      </div>
                    )}
                  </td>
                  <td>
                    <span style={{ fontSize: 13, color: '#94a3b8' }}>{student.goal}</span>
                  </td>
                  <td>
                    <StatusBadge status={student.status} />
                  </td>
                  <td style={{ minWidth: 160 }}>
                    <MiniBar value={student.probability} />
                  </td>
                  <td>
                    <span style={{ color: '#10b981', fontWeight: 600 }}>
                      {student.tasks_completed}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: student.tasks_missed > 3 ? '#ef4444' : '#94a3b8', fontWeight: 600 }}>
                      {student.tasks_missed}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setSelectedStudent(student)}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* AT-RISK ALERT PANEL */}
      {stats.at_risk > 0 && (
        <div className="card mt-24" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
          <div className="card-title" style={{ color: '#ef4444' }}>
            <span className="icon">🚨</span>
            At-Risk Student Interventions
          </div>
          {data.students
            .filter(s => s.status === 'At Risk')
            .map(s => (
              <div key={s.id} className="insight-card" style={{ borderColor: 'rgba(239,68,68,0.2)' }}>
                <div className="insight-header">
                  <span style={{ color: '#ef4444' }}>⚠️</span>
                  {s.name} — {s.probability}% probability
                </div>
                {s.suggestions?.[0] && (
                  <div className="insight-body">{s.suggestions[0]}</div>
                )}
              </div>
            ))
          }
        </div>
      )}

      {/* STUDENT DETAIL MODAL */}
      {selectedStudent && (
        <StudentModal
          student={selectedStudent}
          onClose={() => setSelectedStudent(null)}
        />
      )}
    </div>
  );
}
