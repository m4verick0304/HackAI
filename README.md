# 🚀 PrepGenie — Agentic AI Placement Engine

> A full-stack hackathon MVP that autonomously manages a student's placement journey using 5 AI agents.

---

## 🏗️ Project Structure

```
PrepGenie/
├── frontend/                   # React frontend
│   └── src/
│       ├── App.js              # Main app with navbar + tab routing
│       ├── api.js              # Centralized API service
│       ├── index.css           # Full design system (dark theme)
│       └── components/
│           ├── StudentDashboard.js   # Resume input, roadmap, task tracker
│           ├── AdminDashboard.js     # Student table, stats, modals
│           └── InsightsPanel.js      # AI insights, simulator, tips
│
└── backend/                    # Flask backend
    ├── app.py                  # Main Flask app (all routes)
    ├── config.py               # API key + LLM client setup
    ├── requirements.txt
    ├── agents/
    │   ├── planner.py          # 7-day roadmap generator
    │   ├── evaluator.py        # Placement probability calculator
    │   ├── decision.py         # Status + action decision engine
    │   ├── simulator.py        # Before/after skill simulation (USP)
    │   └── strategist.py       # Alternative career suggestions (USP)
    ├── utils/
    │   ├── parser.py           # Resume skill extractor
    │   └── storage.py          # JSON-based persistence
    └── data/
        └── students.json       # Student data store
```

---

## ⚡ Quick Start

### 1. Start the Backend (Flask)

```bash
cd PrepGenie/backend

# Install dependencies (first time only)
pip3 install flask flask-cors google-generativeai

# (Optional) Set Gemini API key for LLM features
export GEMINI_API_KEY="your-key-here"

# Start server
python3 app.py
# Runs on: http://localhost:5001
```

### 2. Start the Frontend (React)

```bash
cd PrepGenie/frontend
npm install   # first time only
npm start
# Opens on: http://localhost:3000
```

---

## 🤖 AI Agent System

| Agent | Input | Output | Mode |
|-------|-------|--------|------|
| **PlannerAgent** | skills + goal | 7-day roadmap (JSON) | LLM / Rule-based fallback |
| **EvaluatorAgent** | skills + tasks | placement_probability + readiness_score | Formula + LLM explanation |
| **DecisionAgent** | probability + tasks_missed | status + action + alerts | Rule-based + LLM refinement |
| **SimulatorAgent** | current skills | before/after probability 🔥 | Formula + LLM narrative |
| **StrategistAgent** | profile | alternative careers + strategy 🔥 | Skill-matching + LLM |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Healthcheck |
| `POST` | `/generate-roadmap` | Parse resume → roadmap + probability |
| `POST` | `/simulate` | Before/after skill simulation |
| `POST` | `/evaluate` | Recalculate probability after task updates |
| `POST` | `/decision` | Run decision agent |
| `POST` | `/update-tasks` | Mark tasks done/missed → live updates |
| `GET`  | `/admin-data` | All students with stats |

---

## 📊 Data Format

```json
{
  "id": "student_xxx",
  "name": "Arjun Sharma",
  "goal": "SDE",
  "skills": ["python", "dsa", "sql"],
  "tasks_completed": 5,
  "tasks_missed": 2,
  "status": "Learning",
  "probability": 62,
  "roadmap": [...],
  "alerts": [],
  "suggestions": ["..."],
  "alternative_careers": [...],
  "strategy": "..."
}
```

---

## 🎯 Demo Flow

1. **Student** opens the app → pastes resume → selects goal → clicks **Generate My Plan**
2. AI extracts skills, generates 7-day roadmap, calculates placement probability
3. Student marks tasks **Done** / **Missed** → probability updates live
4. Click **Run Simulation** → see how upskilling would improve your score
5. **Admin** tab → see all students sorted by risk (At Risk → Learning → Ready)
6. Click **View Details** on any student → full AI analysis + recommendation

---

## 🔑 Gemini API Key (Optional)

Without an API key, PrepGenie runs in **rule-based mode** — all features work, just without LLM-generated text.

With a Gemini API key, you get:
- Personalized roadmap text (instead of templates)
- Natural language explanations of probability
- AI-generated career strategy narratives

Get a free key at: [aistudio.google.com](https://aistudio.google.com)

```bash
export GEMINI_API_KEY="AIza..."
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Create React App) |
| Styling | Vanilla CSS (dark theme, glassmorphism) |
| Backend | Python Flask |
| Data | JSON file (`students.json`) |
| AI | Google Gemini 1.5 Flash + rule-based fallback |
| Fonts | Inter + Space Grotesk (Google Fonts) |

---

*Built for Hackathon 2026 · PrepGenie Agentic AI*
