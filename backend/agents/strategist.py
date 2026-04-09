"""
strategist.py - Strategist Agent (USP Feature)
Suggests alternative career paths based on the student's current skill profile.
"""

import os
from config import generate_text, GEMINI_API_KEY


# Skill → career mapping for rule-based suggestions
CAREER_MAP = [
    {
        "role": "Backend Developer",
        "required_skills": ["python", "sql", "flask", "django", "nodejs"],
        "description": "Strong match for your Python + database skills.",
        "companies": ["Flipkart", "Paytm", "PhonePe", "Razorpay"]
    },
    {
        "role": "Data Engineer",
        "required_skills": ["python", "sql", "spark", "hadoop", "pandas"],
        "description": "Your data skills translate well to data engineering pipelines.",
        "companies": ["Amazon", "Swiggy", "Zomato", "CRED"]
    },
    {
        "role": "ML Engineer",
        "required_skills": ["python", "machine learning", "ml", "tensorflow", "pytorch", "deep learning"],
        "description": "Strong ML background makes you a great fit for applied AI teams.",
        "companies": ["Google", "Microsoft", "OLA", "Meesho"]
    },
    {
        "role": "DevOps Engineer",
        "required_skills": ["docker", "kubernetes", "aws", "linux", "git", "ci/cd"],
        "description": "Your tooling knowledge maps to high-demand DevOps roles.",
        "companies": ["Atlassian", "HashiCorp", "Nutanix", "VMware"]
    },
    {
        "role": "Business Analyst",
        "required_skills": ["excel", "sql", "statistics", "tableau", "power bi"],
        "description": "Your analytics skills are perfect for strategy and business analysis roles.",
        "companies": ["McKinsey", "Deloitte", "KPMG", "Accenture"]
    },
    {
        "role": "Frontend Developer",
        "required_skills": ["react", "javascript", "html", "css", "typescript"],
        "description": "Strong frontend skills open doors at product-focused companies.",
        "companies":["Notion", "Atlassian", "InMobi", "BookMyShow"]
    },
    {
        "role": "QA / Test Engineer",
        "required_skills": ["python", "java", "selenium", "testing", "git"],
        "description": "Solid programming skills are great for automated testing roles.",
        "companies": ["Infosys", "Wipro", "TCS", "Capgemini"]
    },
]


def find_alternative_careers(skills: list, current_goal: str) -> list:
    """Find career alternatives based on skill overlap."""
    skills_lower = set(s.lower() for s in skills)
    scored = []

    for career in CAREER_MAP:
        if career["role"] == current_goal:
            continue  # Skip current goal
        
        overlap = len(set(career["required_skills"]) & skills_lower)
        if overlap > 0:
            scored.append({"score": overlap, "career": career})

    # Sort by overlap score (integer key only — avoids dict comparison error)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [item["career"] for item in scored[:2]]  # Top 2 alternatives


def get_llm_strategy(skills: list, goal: str, alternatives: list) -> str:
    """Get LLM career strategy narrative."""
    try:
        alt_names = ", ".join([a["role"] for a in alternatives]) if alternatives else "various roles"
        skills_str = ", ".join(skills[:6]) if skills else "general skills"

        prompt = f"""A student wants to be a {goal} but their current skills are: {skills_str}.

Alternative career options identified: {alt_names}.

Give a 2-3 sentence strategic career advice message. Be specific about which path to take and why, based on their skills. Mention effort vs. reward tradeoff."""

        result = generate_text(prompt)
        return result if result else None
    except Exception as e:
        print(f"[Strategist] LLM error: {e}")
        return None


def run(skills: list, goal: str) -> dict:
    """
    Main entry point for Strategist Agent.
    Returns alternative career suggestions with reasoning.
    """
    alternatives = find_alternative_careers(skills, goal)

    # Get LLM strategy narrative
    strategy_narrative = None
    if GEMINI_API_KEY:
        strategy_narrative = get_llm_strategy(skills, goal, alternatives)

    if not strategy_narrative:
        if alternatives:
            alt_name = alternatives[0]["role"]
            strategy_narrative = f"Based on your current skill set, you show strong potential for {alt_name}. Consider diversifying your job search to include this role alongside your primary goal of {goal}."
        else:
            strategy_narrative = f"Keep focusing on building skills for {goal}. Your current trajectory shows good alignment with this goal."

    return {
        "primary_goal": goal,
        "current_skills": skills,
        "alternative_careers": alternatives,
        "strategy": strategy_narrative,
        "agent": "StrategistAgent"
    }
