// api.js - Centralized API service for PrepGenie frontend
const BASE_URL = 'http://localhost:8000';

const api = {
  /**
   * Generate a personalized roadmap from resume
   */
  generateRoadmap: async (resumeText, goal, name = '') => {
    const res = await fetch(`${BASE_URL}/generate-roadmap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: resumeText, goal, name })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Simulate placement probability before/after skill improvement
   */
  simulate: async (skills, goal, tasksCompleted = 5, tasksMissed = 1) => {
    const res = await fetch(`${BASE_URL}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skills, goal, tasks_completed: tasksCompleted, tasks_missed: tasksMissed })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Evaluate student placement probability
   */
  evaluate: async (studentId, tasksCompleted, tasksMissed) => {
    const res = await fetch(`${BASE_URL}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, tasks_completed: tasksCompleted, tasks_missed: tasksMissed })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Update roadmap task completions
   */
  updateTasks: async (studentId, roadmap) => {
    const res = await fetch(`${BASE_URL}/update-tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, roadmap })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Run decision agent
   */
  decision: async (probability, tasksMissed, skills) => {
    const res = await fetch(`${BASE_URL}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ probability, tasks_missed: tasksMissed, skills })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Get admin dashboard data
   */
  getAdminData: async () => {
    const res = await fetch(`${BASE_URL}/admin-data`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  }
};

export default api;
