"""
evaluator.py - Evaluator Agent
Calculates placement probability and readiness score based on student profile.
Uses weighted formula + optional LLM explanation.
"""

import os
from config import generate_text, GEMINI_API_KEY

# Skill weights per role (how important each skill category is)
SKILL_WEIGHTS = {
    "SDE": {
        "dsa": 30, "data structures": 30, "algorithms": 30,
        "system design": 20, "python": 15, "java": 15,
        "javascript": 10, "sql": 10, "git": 5, "oops": 10,
        "c++": 15, "os": 8, "networking": 8, "dbms": 8
    },
    "Data Analyst": {
        "sql": 30, "python": 20, "pandas": 20, "excel": 15,
        "statistics": 20, "tableau": 10, "power bi": 10,
        "data visualization": 10, "numpy": 10, "matplotlib": 5
    },
    "Full Stack Developer": {
        "javascript": 25, "react": 20, "nodejs": 20, "sql": 10,
        "html": 10, "css": 10, "git": 10, "express": 15,
        "mongodb": 10, "python": 10, "docker": 5
    },
    "Data Scientist": {
        "python": 20, "machine learning": 30, "ml": 30, "statistics": 20,
        "pandas": 15, "numpy": 10, "scikit-learn": 15, "tensorflow": 10,
        "pytorch": 10, "sql": 10, "deep learning": 15
    },
    "Product Manager": {
        "analytics": 15, "sql": 15, "excel": 10, "communication": 20,
        "product": 20, "agile": 10, "scrum": 10, "figma": 10
    }
}


def calculate_skill_score(skills: list, goal: str) -> int:
    """Calculate skill match score (0-50 points)."""
    weights = SKILL_WEIGHTS.get(goal, SKILL_WEIGHTS["SDE"])
    total_possible = sum(sorted(weights.values(), reverse=True)[:5])  # Top 5 skills
    
    earned = 0
    skills_lower = [s.lower() for s in skills]
    
    for skill in skills_lower:
        if skill in weights:
            earned += weights[skill]

    # Normalize to 0-50
    score = min(50, int((earned / max(total_possible, 1)) * 50))
    return score


def calculate_activity_score(tasks_completed: int, tasks_missed: int) -> int:
    """Calculate activity/engagement score (0-35 points)."""
    total = tasks_completed + tasks_missed
    if total == 0:
        return 15  # Neutral score for new students
    
    completion_rate = tasks_completed / total
    base_score = int(completion_rate * 35)
    
    # Penalty for high missed count
    if tasks_missed > 5:
        base_score = max(0, base_score - 10)
    
    return base_score


def calculate_consistency_bonus(tasks_completed: int) -> int:
    """Bonus points for consistent task completion (0-15 points)."""
    if tasks_completed >= 10:
        return 15
    elif tasks_completed >= 7:
        return 10
    elif tasks_completed >= 5:
        return 7
    elif tasks_completed >= 3:
        return 4
    return 0


def get_llm_explanation(skills: list, goal: str, probability: int, tasks_missed: int) -> str:
    """Get LLM-generated explanation of the probability."""
    try:
        prompt = f"""You are a placement counselor. Explain in 2 sentences why this student has a {probability}% placement probability.

Student Skills: {', '.join(skills)}
Target Role: {goal}
Tasks Missed: {tasks_missed}
Placement Probability: {probability}%

Be specific, encouraging but honest. Return only the 2-sentence explanation."""

        result = generate_text(prompt)
        if result:
            return result
    except Exception as e:
        print(f"[Evaluator] LLM error: {e}")
    return generate_rule_explanation(probability, tasks_missed)


def generate_rule_explanation(probability: int, tasks_missed: int) -> str:
    """Rule-based fallback explanation."""
    if probability >= 75:
        return f"Strong skill alignment with target role and consistent task completion. Keep the momentum — you're on track for placement!"
    elif probability >= 50:
        return f"Good foundational skills but need more consistency. Completing missed tasks and strengthening core skills will significantly boost your chances."
    else:
        missed_note = f" Missed {tasks_missed} tasks is hurting your score." if tasks_missed > 3 else ""
        return f"Currently underprepared for the target role.{missed_note} Focus on core skill building and daily task completion."


def run(skills: list, goal: str, tasks_completed: int, tasks_missed: int) -> dict:
    """
    Main entry point for Evaluator Agent.
    Returns placement probability, readiness score, and explanation.
    """
    skill_score = calculate_skill_score(skills, goal)
    activity_score = calculate_activity_score(tasks_completed, tasks_missed)
    consistency_bonus = calculate_consistency_bonus(tasks_completed)

    probability = min(100, skill_score + activity_score + consistency_bonus)
    readiness_score = round((probability / 100) * 10, 1)  # Scale to 10

    explanation = get_llm_explanation(skills, goal, probability, tasks_missed)

    return {
        "placement_probability": probability,
        "readiness_score": readiness_score,
        "skill_score": skill_score,
        "activity_score": activity_score,
        "consistency_bonus": consistency_bonus,
        "explanation": explanation,
        "agent": "EvaluatorAgent"
    }
