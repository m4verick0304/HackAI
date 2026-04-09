"""
decision.py - Decision Agent (Core Agentic Logic)
Determines student status and recommends actions based on probability and behavior.
Rule-based logic first, LLM refinement optionally.
"""

from config import generate_text, GEMINI_API_KEY


def determine_status_rule_based(probability: int, tasks_missed: int, skills: list) -> str:
    """Rule-based status determination."""
    # At Risk: Low probability OR too many missed tasks
    if probability < 40 or tasks_missed >= 5:
        return "At Risk"
    # Ready: High probability AND few missed tasks
    elif probability >= 70 and tasks_missed <= 2:
        return "Ready"
    # Default: Learning
    else:
        return "Learning"


def determine_action(status: str, probability: int, tasks_missed: int, skills: list) -> dict:
    """Determine the recommended action based on status."""
    if status == "At Risk":
        return {
            "type": "alert",
            "label": "Urgent: Intervention Needed",
            "description": f"Student is at risk with {probability}% probability and {tasks_missed} missed tasks. Assign remedial practice and schedule counseling."
        }
    elif status == "Ready":
        return {
            "type": "suggest_job",
            "label": "Job Ready",
            "description": f"Student is job-ready at {probability}% probability. Suggest applying to top companies and schedule mock interviews."
        }
    else:
        return {
            "type": "assign_practice",
            "label": "Continue Learning",
            "description": f"Student is progressing. Assign additional practice problems to boost from {probability}% to 70%+."
        }


def get_llm_refined_action(status: str, probability: int, tasks_missed: int, skills: list) -> str:
    """Use LLM to generate a refined, personalized action recommendation."""
    try:
        skills_str = ", ".join(skills[:5]) if skills else "no skills listed"
        prompt = f"""You are an AI placement advisor. A student has:
- Status: {status}
- Placement Probability: {probability}%
- Tasks Missed: {tasks_missed}
- Current Skills: {skills_str}

Give ONE specific, actionable recommendation in 1-2 sentences. Be direct and practical."""

        result = generate_text(prompt)
        return result if result else None
    except Exception as e:
        print(f"[Decision] LLM error: {e}")
        return None


def generate_alerts(tasks_missed: int, probability: int, skills: list) -> list:
    """Generate alert messages for the student."""
    alerts = []
    if tasks_missed >= 5:
        alerts.append(f"⚠️ You've missed {tasks_missed} tasks — this is hurting your placement score!")
    elif tasks_missed >= 3:
        alerts.append(f"⚠️ {tasks_missed} missed tasks detected — try to stay consistent.")

    if probability < 40:
        alerts.append("🔴 Placement probability is critically low. Immediate action required.")
    elif probability < 60:
        alerts.append("🟡 Below target score. Focus on skill-building this week.")

    if len(skills) < 3:
        alerts.append("📚 Very few skills detected — add more to your profile.")

    return alerts


def run(probability: int, tasks_missed: int, skills: list) -> dict:
    """
    Main entry point for Decision Agent.
    Returns status, action, alerts, and AI recommendation.
    """
    status = determine_status_rule_based(probability, tasks_missed, skills)
    action = determine_action(status, probability, tasks_missed, skills)
    alerts = generate_alerts(tasks_missed, probability, skills)

    # Try to get LLM refinement
    llm_recommendation = None
    if GEMINI_API_KEY:
        llm_recommendation = get_llm_refined_action(status, probability, tasks_missed, skills)

    final_recommendation = llm_recommendation or action["description"]

    return {
        "status": status,
        "action": action,
        "alerts": alerts,
        "recommendation": final_recommendation,
        "risk_level": "high" if status == "At Risk" else ("low" if status == "Ready" else "medium"),
        "agent": "DecisionAgent"
    }
