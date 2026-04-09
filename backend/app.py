"""
app.py - PrepGenie Flask Backend
Main application entry point with all API routes.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.parser import parse_resume
from utils.storage import load_students, upsert_student, update_student_field, get_student_by_id
from agents import planner, evaluator, decision, simulator, strategist

app = Flask(__name__)
CORS(app)  # Enable cross-origin for React frontend


# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "PrepGenie Backend", "version": "1.0.0"})


# ============================================================
# POST /generate-roadmap
# Input: resume_text, goal, name (optional)
# Output: roadmap, skills, student_id
# ============================================================
@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        goal = data.get('goal', 'SDE')
        student_name = data.get('name', '')

        if not resume_text:
            return jsonify({"error": "resume_text is required"}), 400

        # Step 1: Parse resume
        parsed = parse_resume(resume_text)
        skills = parsed['skills']
        name = student_name or parsed['name']

        # Step 2: Planner Agent → generate roadmap
        plan_result = planner.run(skills, goal)
        roadmap = plan_result['roadmap']

        # Step 3: Evaluate initial probability
        eval_result = evaluator.run(skills, goal, 0, 0)
        probability = eval_result['placement_probability']

        # Step 4: Decision Agent
        dec_result = decision.run(probability, 0, skills)
        status = dec_result['status']

        # Step 5: Strategist
        strat_result = strategist.run(skills, goal)

        # Build student record
        student = {
            "name": name,
            "goal": goal,
            "skills": skills,
            "tasks_completed": 0,
            "tasks_missed": 0,
            "roadmap": roadmap,
            "status": status,
            "probability": probability,
            "suggestions": [dec_result["recommendation"]],
            "alerts": dec_result["alerts"],
            "alternative_careers": strat_result["alternative_careers"],
            "strategy": strat_result["strategy"],
            "explanation": eval_result["explanation"]
        }

        # Step 6: Save to JSON
        saved_student = upsert_student(student)

        return jsonify({
            "success": True,
            "student_id": saved_student["id"],
            "name": name,
            "skills": skills,
            "goal": goal,
            "roadmap": roadmap,
            "probability": probability,
            "status": status,
            "explanation": eval_result["explanation"],
            "alternative_careers": strat_result["alternative_careers"],
            "strategy": strat_result["strategy"],
            "alerts": dec_result["alerts"],
            "recommendation": dec_result["recommendation"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# POST /simulate
# Input: skills, goal, tasks_completed, tasks_missed
# Output: before/after probability comparison
# ============================================================
@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        skills = data.get('skills', [])
        goal = data.get('goal', 'SDE')
        tasks_completed = data.get('tasks_completed', 5)
        tasks_missed = data.get('tasks_missed', 1)

        result = simulator.run(skills, goal, tasks_completed, tasks_missed)
        return jsonify({"success": True, **result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# POST /evaluate
# Input: student_id, tasks_completed, tasks_missed
# Output: updated probability, readiness_score, explanation
# ============================================================
@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        tasks_completed = data.get('tasks_completed', 0)
        tasks_missed = data.get('tasks_missed', 0)

        student = get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        skills = student.get('skills', [])
        goal = student.get('goal', 'SDE')

        # Run evaluator
        eval_result = evaluator.run(skills, goal, tasks_completed, tasks_missed)
        probability = eval_result['placement_probability']

        # Run decision agent
        dec_result = decision.run(probability, tasks_missed, skills)
        status = dec_result['status']

        # Update student record
        updated = update_student_field(student_id, {
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "probability": probability,
            "status": status,
            "alerts": dec_result["alerts"],
            "suggestions": [dec_result["recommendation"]]
        })

        return jsonify({
            "success": True,
            "student_id": student_id,
            "probability": probability,
            "readiness_score": eval_result["readiness_score"],
            "status": status,
            "explanation": eval_result["explanation"],
            "alerts": dec_result["alerts"],
            "recommendation": dec_result["recommendation"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# POST /decision
# Input: probability, tasks_missed, skills
# Output: status, action, alerts, recommendation
# ============================================================
@app.route('/decision', methods=['POST'])
def make_decision():
    try:
        data = request.get_json()
        probability = data.get('probability', 50)
        tasks_missed = data.get('tasks_missed', 0)
        skills = data.get('skills', [])

        result = decision.run(probability, tasks_missed, skills)
        return jsonify({"success": True, **result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# POST /update-tasks
# Input: student_id, roadmap (with completed/missed flags)
# Output: updated student data
# ============================================================
@app.route('/update-tasks', methods=['POST'])
def update_tasks():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        roadmap = data.get('roadmap', [])

        student = get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        # Count completions
        tasks_completed = sum(1 for t in roadmap if t.get('completed'))
        tasks_missed = sum(1 for t in roadmap if t.get('missed'))

        skills = student.get('skills', [])
        goal = student.get('goal', 'SDE')

        # Re-evaluate
        eval_result = evaluator.run(skills, goal, tasks_completed, tasks_missed)
        probability = eval_result['placement_probability']
        dec_result = decision.run(probability, tasks_missed, skills)
        status = dec_result['status']

        updated = update_student_field(student_id, {
            "roadmap": roadmap,
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "probability": probability,
            "status": status,
            "alerts": dec_result["alerts"],
            "suggestions": [dec_result["recommendation"]]
        })

        return jsonify({
            "success": True,
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "probability": probability,
            "status": status,
            "alerts": dec_result["alerts"],
            "recommendation": dec_result["recommendation"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# GET /admin-data
# Output: all students with status, probability, alerts
# ============================================================
@app.route('/admin-data', methods=['GET'])
def admin_data():
    try:
        students = load_students()
        
        # Enrich each student with decision summary
        enriched = []
        for s in students:
            enriched.append({
                "id": s.get("id"),
                "name": s.get("name", "Unknown"),
                "goal": s.get("goal", ""),
                "skills": s.get("skills", []),
                "status": s.get("status", "Learning"),
                "probability": s.get("probability", 0),
                "tasks_completed": s.get("tasks_completed", 0),
                "tasks_missed": s.get("tasks_missed", 0),
                "alerts": s.get("alerts", []),
                "suggestions": s.get("suggestions", []),
                "alternative_careers": s.get("alternative_careers", []),
                "strategy": s.get("strategy", ""),
                "explanation": s.get("explanation", ""),
                "risk_level": "high" if s.get("status") == "At Risk" else ("low" if s.get("status") == "Ready" else "medium")
            })
        
        # Sort: At Risk first
        enriched.sort(key=lambda x: (0 if x["status"] == "At Risk" else (1 if x["status"] == "Learning" else 2)))

        stats = {
            "total": len(enriched),
            "at_risk": sum(1 for s in enriched if s["status"] == "At Risk"),
            "learning": sum(1 for s in enriched if s["status"] == "Learning"),
            "ready": sum(1 for s in enriched if s["status"] == "Ready"),
            "avg_probability": round(sum(s["probability"] for s in enriched) / max(len(enriched), 1), 1)
        }

        return jsonify({
            "success": True,
            "students": enriched,
            "stats": stats
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# POST /strategy
# Input: student_id
# Output: career alternatives + strategy narrative
# ============================================================
@app.route('/strategy', methods=['POST'])
def get_strategy():
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        student = get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        result = strategist.run(student.get('skills', []), student.get('goal', 'SDE'))
        return jsonify({"success": True, **result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("  PrepGenie Backend Starting...")
    print("  API: http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)
