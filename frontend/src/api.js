// api.js - Centralized API service for PrepGenie frontend
import { supabase } from "./lib/supabase";

// Use environment variable for backend URL, fallback to localhost for development
const BASE_URL = process.env.REACT_APP_API_URL || 'https://hackai-oz9d.onrender.com'; // Adjust this to your deployed backend URL

export const fetchWithAuth = async (url, options = {}) => {
  let token = null;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    token = session?.access_token;
  } catch (e) {
    console.warn("Could not get supabase session", e);
  }

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "application/json",
    },
  });
};

const api = {
  /**
   * Generate a personalized roadmap from resume
   */
  generateRoadmap: async (resumeText, goal, name = '') => {
    const res = await fetchWithAuth(`${BASE_URL}/generate-roadmap`, {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, goal, name })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Simulate placement probability before/after skill improvement
   */
  simulate: async (skills, goal, tasksCompleted = 5, tasksMissed = 1) => {
    const res = await fetchWithAuth(`${BASE_URL}/simulate`, {
      method: 'POST',
      body: JSON.stringify({ skills, goal, tasks_completed: tasksCompleted, tasks_missed: tasksMissed })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Evaluate student placement probability
   */
  evaluate: async (studentId, tasksCompleted, tasksMissed) => {
    const res = await fetchWithAuth(`${BASE_URL}/evaluate`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, tasks_completed: tasksCompleted, tasks_missed: tasksMissed })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Update roadmap task completions
   */
  updateTasks: async (studentId, roadmap) => {
    const res = await fetchWithAuth(`${BASE_URL}/update-tasks`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, roadmap })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Run decision agent
   */
  decision: async (probability, tasksMissed, skills) => {
    const res = await fetchWithAuth(`${BASE_URL}/decision`, {
      method: 'POST',
      body: JSON.stringify({ probability, tasks_missed: tasksMissed, skills })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  },

  /**
   * Get admin dashboard data
   */
  getAdminData: async () => {
    const res = await fetchWithAuth(`${BASE_URL}/admin-data`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
  }
};

export default api;
