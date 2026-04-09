"""
planner.py - Planner Agent
Generates a 7-day personalized learning roadmap based on skills and goal.
Uses LLM if API key is available, falls back to rule-based generation.
"""

import os
import json
from config import generate_text, GEMINI_API_KEY

# Goal-based default task templates
TASK_TEMPLATES = {
    "SDE": [
        {"day": 1, "task": "Revise Arrays & Strings — Solve 3 LeetCode Easy problems", "topic": "DSA"},
        {"day": 2, "task": "Study Linked Lists & Recursion — Implement from scratch", "topic": "DSA"},
        {"day": 3, "task": "Trees & Graph traversal — BFS/DFS practice", "topic": "DSA"},
        {"day": 4, "task": "Dynamic Programming basics — Fibonacci, Knapsack", "topic": "DSA"},
        {"day": 5, "task": "System Design concepts — CAP theorem, Load Balancing", "topic": "System Design"},
        {"day": 6, "task": "Mock Interview simulation — 2 problems in 45 minutes", "topic": "Interview Prep"},
        {"day": 7, "task": "Resume polish + Apply to 5 SDE roles on LinkedIn/Naukri", "topic": "Job Hunt"},
    ],
    "Data Analyst": [
        {"day": 1, "task": "SQL deep dive — JOINs, GROUP BY, Window Functions", "topic": "SQL"},
        {"day": 2, "task": "Python Pandas — Load, clean, and analyze a dataset", "topic": "Python"},
        {"day": 3, "task": "Data visualization — Build 3 charts using Matplotlib/Tableau", "topic": "Visualization"},
        {"day": 4, "task": "Statistics fundamentals — Mean, Median, Standard Deviation, p-values", "topic": "Statistics"},
        {"day": 5, "task": "Excel advanced — VLOOKUP, Pivot Tables, Macros", "topic": "Excel"},
        {"day": 6, "task": "Build a mini-dashboard project using real dataset", "topic": "Project"},
        {"day": 7, "task": "Portfolio update + Apply to 5 Data Analyst roles", "topic": "Job Hunt"},
    ],
    "Full Stack Developer": [
        {"day": 1, "task": "HTML/CSS review — Build a responsive landing page", "topic": "Frontend"},
        {"day": 2, "task": "JavaScript ES6+ — Promises, async/await, fetch API", "topic": "JavaScript"},
        {"day": 3, "task": "React components & hooks — Build a CRUD app", "topic": "React"},
        {"day": 4, "task": "Node.js + Express API — REST endpoints with JSON", "topic": "Backend"},
        {"day": 5, "task": "Database integration — MongoDB or PostgreSQL with your API", "topic": "Database"},
        {"day": 6, "task": "Deploy a full-stack project to Vercel/Render", "topic": "DevOps"},
        {"day": 7, "task": "Portfolio update + Apply to 5 Full Stack roles", "topic": "Job Hunt"},
    ],
    "Data Scientist": [
        {"day": 1, "task": "Python for ML — Pandas, NumPy, Scikit-learn setup", "topic": "Python"},
        {"day": 2, "task": "Supervised learning — Linear & Logistic Regression", "topic": "ML"},
        {"day": 3, "task": "Classification models — Decision Trees, Random Forest", "topic": "ML"},
        {"day": 4, "task": "Model evaluation — Accuracy, Precision, Recall, F1, ROC-AUC", "topic": "ML Metrics"},
        {"day": 5, "task": "Feature engineering & dimensionality reduction (PCA)", "topic": "ML"},
        {"day": 6, "task": "End-to-end ML project — Train, evaluate, and present model", "topic": "Project"},
        {"day": 7, "task": "Kaggle competition submission + Apply to 5 DS roles", "topic": "Job Hunt"},
    ],
    "Product Manager": [
        {"day": 1, "task": "PM frameworks — RICE, MoSCoW, and OKRs study", "topic": "Frameworks"},
        {"day": 2, "task": "User research basics — Surveys, Interviews, Persona creation", "topic": "Research"},
        {"day": 3, "task": "Product analytics — Define KPIs, retention, activation metrics", "topic": "Analytics"},
        {"day": 4, "task": "Wireframing — Create mockups for a product feature in Figma", "topic": "Design"},
        {"day": 5, "task": "Practice PM case interviews — 3 product design cases", "topic": "Interview"},
        {"day": 6, "task": "Market analysis — Competitor research for a product you love", "topic": "Strategy"},
        {"day": 7, "task": "Update PM portfolio + Apply to 5 PM roles", "topic": "Job Hunt"},
    ],
}


def generate_roadmap_rule_based(skills: list, goal: str) -> list:
    """Fallback: rule-based roadmap generation."""
    template = TASK_TEMPLATES.get(goal, TASK_TEMPLATES["SDE"])
    roadmap = []
    for item in template:
        roadmap.append({
            "day": item["day"],
            "task": item["task"],
            "topic": item["topic"],
            "completed": False,
            "missed": False
        })
    return roadmap


def generate_roadmap_llm(skills: list, goal: str) -> list:
    """LLM-powered roadmap generation using Gemini."""
    try:
        skills_str = ", ".join(skills) if skills else "beginner"
        prompt = f"""You are a placement coach AI. Generate a 7-day personalized learning roadmap.

Student Skills: {skills_str}
Target Role: {goal}

Return ONLY a valid JSON array with exactly 7 objects. Each object must have:
- "day": (integer 1-7)
- "task": (specific, actionable task string, max 100 chars)
- "topic": (short category like "DSA", "System Design", "SQL", etc.)

Focus on gaps in skills and what's needed for {goal} interviews. Be specific and practical.
Return ONLY the JSON array, no explanation."""

        text = generate_text(prompt)
        if not text:
            return generate_roadmap_rule_based(skills, goal)

        # Extract JSON array from response
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            roadmap_data = json.loads(text[start:end])
            result = []
            for item in roadmap_data[:7]:
                result.append({
                    "day": item.get("day", len(result) + 1),
                    "task": item.get("task", "Complete study session"),
                    "topic": item.get("topic", "General"),
                    "completed": False,
                    "missed": False
                })
            return result
    except Exception as e:
        print(f"[Planner] LLM error: {e}, falling back to rule-based")

    return generate_roadmap_rule_based(skills, goal)


def run(skills: list, goal: str) -> dict:
    """
    Main entry point for Planner Agent.
    Returns a structured roadmap with 7-day tasks.
    """
    if GEMINI_API_KEY:
        roadmap = generate_roadmap_llm(skills, goal)
    else:
        roadmap = generate_roadmap_rule_based(skills, goal)

    return {
        "goal": goal,
        "skills_detected": skills,
        "roadmap": roadmap,
        "total_days": len(roadmap),
        "agent": "PlannerAgent"
    }
