import React, { useState } from 'react';
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
// PROGRESS BAR
// ============================================================
function ProgressBar({ value, label }) {
  const tier = value >= 70 ? 'high' : value >= 40 ? 'medium' : 'low';
  return (
    <div className="progress-wrapper">
      <div className="progress-label">
        <span style={{ color: '#94a3b8', fontSize: 13 }}>{label}</span>
        <span style={{ fontWeight: 700, fontSize: 15 }}>{value}%</span>
      </div>
      <div className="progress-bar-track">
        <div
          className={`progress-bar-fill ${tier}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

// ============================================================
// ROADMAP TASK CARD
// ============================================================
function RoadmapCard({ item, onMarkDone, onMarkMissed }) {
  const getClasses = () => {
    let cls = 'roadmap-item';
    if (item.completed) cls += ' completed';
    if (item.missed) cls += ' missed';
    return cls;
  };

  return (
    <div className={getClasses()}>
      <div className="roadmap-day">Day {item.day}</div>
      <div className="roadmap-task">{item.task}</div>
      <span className="roadmap-topic">{item.topic}</span>
      {!item.completed && !item.missed && (
        <div className="roadmap-actions">
          <button className="mark-done" onClick={() => onMarkDone(item.day)}>
            ✓ Done
          </button>
          <button className="mark-missed" onClick={() => onMarkMissed(item.day)}>
            ✗ Missed
          </button>
        </div>
      )}
      {item.completed && (
        <div style={{ marginTop: 10, fontSize: 12, color: '#10b981', fontWeight: 600 }}>
          ✅ Completed
        </div>
      )}
      {item.missed && (
        <div style={{ marginTop: 10, fontSize: 12, color: '#ef4444', fontWeight: 600 }}>
          ❌ Missed
        </div>
      )}
    </div>
  );
}

// ============================================================
// SIMULATION PANEL
// ============================================================
function SimulationPanel({ data }) {
  if (!data) return null;
  const gain = data.probability_gain;

  return (
    <div className="card mt-24">
      <div className="card-title">
        <span className="icon">⚡</span>
        AI Placement Simulator
      </div>
      <div className="simulate-widget">
        <div className="simulate-box">
          <div className="simulate-label">Current Probability</div>
          <div className="simulate-value before">{data.current_probability}%</div>
        </div>
        <div className="simulate-arrow">→</div>
        <div className="simulate-box">
          <div className="simulate-label">After Upskilling</div>
          <div className="simulate-value after">{data.improved_probability}%</div>
        </div>
      </div>

      {gain > 0 && (
        <div className="alert alert-success mt-16">
          <span>📈</span>
          <span>Add <strong>{data.skills_to_add.slice(0, 3).join(', ')}</strong> to gain +{gain}% placement probability!</span>
        </div>
      )}

      {data.simulation_narrative && (
        <div className="insight-card mt-16">
          <div className="insight-header">🤖 AI Insight</div>
          <div className="insight-body">{data.simulation_narrative}</div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// MAIN STUDENT DASHBOARD
// ============================================================
export default function StudentDashboard({ onDataUpdate }) {
  const GOALS = ['SDE', 'Data Analyst', 'Full Stack Developer', 'Data Scientist', 'Product Manager'];

  const [resumeText, setResumeText] = useState('');
  const [goal, setGoal] = useState('SDE');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [error, setError] = useState('');

  // Student state
  const [studentId, setStudentId] = useState(null);
  const [studentData, setStudentData] = useState(null);
  const [roadmap, setRoadmap] = useState([]);
  const [simulation, setSimulation] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  const msgs = [
    '🔍 Parsing your resume...',
    '🤖 Generating personalized roadmap...',
    '📊 Calculating placement probability...',
    '⚡ Running AI agents...'
  ];

  const handleGeneratePlan = async () => {
    if (!resumeText.trim()) {
      setError('Please paste your resume text first.');
      return;
    }

    setLoading(true);
    setError('');
    setSimulation(null);

    // Cycle loading messages
    let i = 0;
    setLoadingMsg(msgs[0]);
    const interval = setInterval(() => {
      i = (i + 1) % msgs.length;
      setLoadingMsg(msgs[i]);
    }, 1200);

    try {
      const data = await api.generateRoadmap(resumeText, goal, name);
      clearInterval(interval);

      if (data.error) {
        setError(data.error);
        return;
      }

      setStudentId(data.student_id);
      setStudentData(data);
      setRoadmap(data.roadmap || []);
      if (onDataUpdate) onDataUpdate(data);
    } catch (e) {
      clearInterval(interval);
      const errorMsg = e.message || 'Failed to connect to backend. Make sure FastAPI server is running (uvicorn main:app).';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkDone = async (day) => {
    const updated = roadmap.map(t =>
      t.day === day ? { ...t, completed: true, missed: false } : t
    );
    setRoadmap(updated);
    await syncTasks(updated);
  };

  const handleMarkMissed = async (day) => {
    const updated = roadmap.map(t =>
      t.day === day ? { ...t, missed: true, completed: false } : t
    );
    setRoadmap(updated);
    await syncTasks(updated);
  };

  const syncTasks = async (updatedRoadmap) => {
    if (!studentId) return;
    try {
      const result = await api.updateTasks(studentId, updatedRoadmap);
      if (result.success) {
        setStudentData(prev => ({
          ...prev,
          probability: result.probability,
          status: result.status,
          alerts: result.alerts,
          recommendation: result.recommendation,
          tasks_completed: result.tasks_completed,
          tasks_missed: result.tasks_missed
        }));
      }
    } catch (e) {
      console.error('Failed to sync tasks:', e);
    }
  };

  const handleSimulate = async () => {
    if (!studentData) return;
    setSimLoading(true);
    try {
      const result = await api.simulate(
        studentData.skills,
        studentData.goal,
        studentData.tasks_completed || 0,
        studentData.tasks_missed || 0
      );
      setSimulation(result);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <div>
      {/* HERO */}
      <div className="hero-section">
        <div className="hero-title">PrepGenie — Your AI Placement Coach 🚀</div>
        <div className="hero-subtitle">
          Drop your resume, pick your goal, and let AI generate a personalized 7-day placement roadmap with live tracking.
        </div>
      </div>

      <div className="grid-2">
        {/* ---- LEFT: INPUT PANEL ---- */}
        <div>
          <div className="card">
            <div className="card-title">
              <span className="icon">📄</span>
              Your Profile
            </div>

            <div className="form-group">
              <label>Your Name</label>
              <input
                type="text"
                placeholder="e.g. Arjun Sharma"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Target Role</label>
              <select value={goal} onChange={e => setGoal(e.target.value)}>
                {GOALS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Paste Your Resume</label>
              <textarea
                rows={8}
                placeholder={`Paste your resume here...\n\nExample:\nJohn Doe\nSkills: Python, React, SQL, Git, DSA\nExperience: Intern at XYZ...\nProjects: Built e-commerce platform using React...`}
                value={resumeText}
                onChange={e => setResumeText(e.target.value)}
                style={{ minHeight: 180 }}
              />
            </div>

            {error && (
              <div className="alert alert-error mb-16">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{error}</span>
                  <button 
                    onClick={handleGeneratePlan}
                    style={{ 
                      background: 'rgba(255,255,255,0.1)', 
                      border: '1px solid rgba(255,255,255,0.2)', 
                      borderRadius: 6, 
                      padding: '4px 12px', 
                      color: 'white', 
                      cursor: 'pointer', 
                      fontSize: 12,
                      marginLeft: 12
                    }}
                  >
                    🔄 Retry
                  </button>
                </div>
              </div>
            )}

            <button
              className="btn btn-primary btn-full"
              onClick={handleGeneratePlan}
              disabled={loading}
            >
              {loading ? '⏳ Generating...' : '🤖 Generate My Plan'}
            </button>

            {loading && (
              <div className="loading-overlay" style={{ padding: 24 }}>
                <div className="spinner" />
                <div className="loading-text">{loadingMsg}</div>
              </div>
            )}
          </div>

          {/* SKILLS DETECTED */}
          {studentData?.skills?.length > 0 && (
            <div className="card mt-16">
              <div className="card-title">
                <span className="icon">🧠</span>
                Skills Detected from Resume
              </div>
              <div className="skill-tags">
                {studentData.skills.map(s => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
              {studentData.skills.length === 0 && (
                <p className="text-muted text-sm">No skills detected. Try adding specific skill keywords to your resume.</p>
              )}
            </div>
          )}

          {/* AI STRATEGY */}
          {studentData?.strategy && (
            <div className="card mt-16">
              <div className="card-title">
                <span className="icon">🎯</span>
                Career Strategy
              </div>
              <div className="insight-body">{studentData.strategy}</div>

              {studentData.alternative_careers?.length > 0 && (
                <div className="mt-16">
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
                    Alternative Paths
                  </div>
                  {studentData.alternative_careers.slice(0, 2).map((c, i) => (
                    <div key={i} className="insight-card">
                      <div className="insight-header">💼 {c.role}</div>
                      <div className="insight-body">{c.description}</div>
                      {c.companies?.length > 0 && (
                        <div style={{ marginTop: 8 }}>
                          <span style={{ fontSize: 11, color: '#64748b' }}>Companies: </span>
                          <span style={{ fontSize: 12, color: '#94a3b8' }}>{c.companies.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* ---- RIGHT: RESULTS PANEL ---- */}
        <div>
          {studentData ? (
            <>
              {/* PROBABILITY + STATUS */}
              <div className="card">
                <div className="flex justify-between items-center mb-16">
                  <div className="card-title" style={{ marginBottom: 0 }}>
                    <span className="icon">📊</span>
                    Placement Readiness
                  </div>
                  <StatusBadge status={studentData.status} />
                </div>

                <ProgressBar
                  value={studentData.probability}
                  label="Placement Probability"
                />

                <div className="divider" />

                <div className="insight-body">{studentData.explanation}</div>

                {/* ALERTS */}
                {studentData.alerts?.length > 0 && (
                  <div className="mt-16">
                    {studentData.alerts.map((a, i) => (
                      <div key={i} className="alert alert-warning">
                        <span>{a}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* RECOMMENDATION */}
                {studentData.recommendation && (
                  <div className="alert alert-info mt-16">
                    <span>💡</span>
                    <span>{studentData.recommendation}</span>
                  </div>
                )}
              </div>

              {/* TASK STATS */}
              <div className="card mt-16">
                <div className="card-title">
                  <span className="icon">📈</span>
                  Task Progress
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 10, padding: '16px', textAlign: 'center' }}>
                    <div style={{ fontSize: 32, fontWeight: 700, color: '#10b981' }}>
                      {studentData.tasks_completed || 0}
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Tasks Completed</div>
                  </div>
                  <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '16px', textAlign: 'center' }}>
                    <div style={{ fontSize: 32, fontWeight: 700, color: '#ef4444' }}>
                      {studentData.tasks_missed || 0}
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Tasks Missed</div>
                  </div>
                </div>
              </div>

              {/* SIMULATE BUTTON */}
              <div className="card mt-16">
                <div className="card-title">
                  <span className="icon">⚡</span>
                  Skill Simulator
                </div>
                <p className="text-muted text-sm mb-16">
                  See how much your placement probability improves if you learn key missing skills.
                </p>
                <button
                  className="btn btn-secondary btn-full"
                  onClick={handleSimulate}
                  disabled={simLoading}
                >
                  {simLoading ? '⏳ Simulating...' : '⚡ Run Simulation'}
                </button>
              </div>
            </>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>🤖</div>
              <div style={{ fontFamily: "'Space Grotesk'", fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                Ready to launch your prep?
              </div>
              <div className="text-muted text-sm">
                Paste your resume and select your goal to get started. PrepGenie will do the rest.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ---- SIMULATION PANEL ---- */}
      {simulation && <SimulationPanel data={simulation} />}

      {/* ---- ROADMAP SECTION ---- */}
      {roadmap.length > 0 && (
        <div className="mt-24">
          <div className="section-header">
            <div className="section-title">🗓️ Your 7-Day Personalized Roadmap</div>
            <div className="section-subtitle">
              Complete tasks daily and track your progress. Your placement score updates in real-time.
            </div>
          </div>
          <div className="roadmap-grid">
            {roadmap.map(item => (
              <RoadmapCard
                key={item.day}
                item={item}
                onMarkDone={handleMarkDone}
                onMarkMissed={handleMarkMissed}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
