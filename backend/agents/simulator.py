"""
simulator.py - Simulator Agent (USP Feature)
Estimates placement probability before vs after improving skills.
Shows students the gap and motivates improvement.
"""

import os
from config import generate_text, GEMINI_API_KEY
from agents import evaluator


def simulate_improved_skills(skills: list, goal: str) -> list:
    """
    Simulate what happens when student improves key skills.
    Returns an enhanced skill list.
    """
    # Key skills to add based on goal
    IMPROVEMENT_MAP = {
        "SDE": ["dsa", "system design", "python", "sql", "git"],
        "Data Analyst": ["sql", "python", "statistics", "tableau", "excel"],
        "Full Stack Developer": ["react", "nodejs", "javascript", "sql", "git"],
        "Data Scientist": ["python", "machine learning", "statistics", "pandas", "sql"],
        "Product Manager": ["analytics", "sql", "agile", "excel"]
    }
    
    target_skills = IMPROVEMENT_MAP.get(goal, IMPROVEMENT_MAP["SDE"])
    
    # Add top 3 missing skills
    current_skills_lower = [s.lower() for s in skills]
    improvements = []
    for skill in target_skills:
        if skill not in current_skills_lower and len(improvements) < 3:
            improvements.append(skill)
    
    return list(set(skills + improvements))


def get_llm_simulation(skills: list, goal: str, current_prob: int, improved_prob: int, new_skills: list) -> str:
    """Get LLM narrative about the simulation."""
    try:
        added_skills = [s for s in new_skills if s.lower() not in [sk.lower() for sk in skills]]
        prompt = f"""You are a career coach. A student targeting {goal} has:

Current probability: {current_prob}%
If they learn {', '.join(added_skills)}: {improved_prob}%

Write 2 sentences explaining what specific improvement these skills will make and which companies they'd now qualify for. Be concrete and motivating."""

        result = generate_text(prompt)
        if result:
            return result
    except Exception as e:
        print(f"[Simulator] LLM error: {e}")
    return generate_rule_simulation_text(current_prob, improved_prob, new_skills)


def generate_rule_simulation_text(current_prob: int, improved_prob: int, new_skills: list) -> str:
    """Fallback text for simulation."""
    gain = improved_prob - current_prob
    if gain > 0:
        return f"By adding key skills, your placement probability increases by {gain}% to {improved_prob}%. This puts you in a much stronger position for your target companies."
    return f"Your current profile shows {current_prob}% readiness. Continue completing tasks to improve your score."


def run(skills: list, goal: str, tasks_completed: int = 5, tasks_missed: int = 1) -> dict:
    """
    Main entry point for Simulator Agent.
    Returns before/after probability comparison.
    """
    # Current probability
    current_eval = evaluator.run(skills, goal, tasks_completed, tasks_missed)
    current_prob = current_eval["placement_probability"]

    # Simulate improved skills
    improved_skills = simulate_improved_skills(skills, goal)
    improved_eval = evaluator.run(improved_skills, goal, tasks_completed, tasks_missed)
    improved_prob = improved_eval["placement_probability"]

    # Get skills added
    added_skills = [s for s in improved_skills if s not in skills]

    # Get narrative
    narrative = ""
    if GEMINI_API_KEY:
        narrative = get_llm_simulation(skills, goal, current_prob, improved_prob, improved_skills)
    else:
        narrative = generate_rule_simulation_text(current_prob, improved_prob, improved_skills)

    return {
        "current_probability": current_prob,
        "improved_probability": improved_prob,
        "probability_gain": improved_prob - current_prob,
        "skills_to_add": added_skills,
        "current_skills": skills,
        "improved_skills": improved_skills,
        "simulation_narrative": narrative,
        "agent": "SimulatorAgent"
    }
