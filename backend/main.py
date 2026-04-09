"""
main.py — PrepGenie FastAPI Backend (Production-Ready)
Unified backend serving all agent pipeline endpoints with auth + Supabase integration.
"""

import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import agents
from agents import planner, evaluator, decision, simulator, strategist
from utils.parser import parse_resume
from utils.storage import (
    upsert_student,
    get_student_by_id,
    load_students,
    update_student_field,
    get_supabase_client
)
from services.gemini import get_ai_response
from routers import chat

# ── Initialize FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title="PrepGenie AI Backend",
    description="Production-ready AI placement preparation API",
    version="2.0.0",
)

# ── CORS Configuration ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Models ────────────────────────────────────────────────────────────
class GenerateRoadmapRequest(BaseModel):
    resume_text: str
    goal: str = "SDE"
    name: str = ""

class SimulateRequest(BaseModel):
    skills: List[str]
    goal: str = "SDE"
    tasks_completed: int = 0
    tasks_missed: int = 0

class EvaluateRequest(BaseModel):
    student_id: str
    tasks_completed: int = 0
    tasks_missed: int = 0

class UpdateTasksRequest(BaseModel):
    student_id: str
    roadmap: List[dict]

class DecisionRequest(BaseModel):
    probability: int
    tasks_missed: int
    skills: List[str]

# ── Auth Helpers ──────────────────────────────────────────────────────────────
async def get_auth_user(authorization: Optional[str] = Header(None)):
    """
    Verify Supabase JWT token.
    Returns user dict if valid, raises HTTPException(401) if invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth failed: {str(e)[:100]}")

async def get_admin_user(user = Depends(get_auth_user)):
    """Verify user is admin."""
    try:
        supabase = get_supabase_client()
        profile = supabase.table('profiles').select('role').eq('id', user.id).execute()
        
        if not profile.data or profile.data[0].get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Role check failed: {str(e)[:100]}")

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "PrepGenie FastAPI Backend",
        "version": "2.0.0"
    }

# ── CORE ENDPOINT: Generate Roadmap ───────────────────────────────────────────
@app.post("/generate-roadmap")
async def generate_roadmap(
    request: GenerateRoadmapRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate a personalized roadmap from resume.
    Optional auth: if provided, links to user; if not, creates anonymous student.
    """
    resume_text = request.resume_text
    goal = request.goal
    name = request.name

    if not resume_text or not resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text is required")

    try:
        # Parse resume
        parsed = parse_resume(resume_text)
        skills = parsed["skills"]
        student_name = name or parsed["name"]

        # Get auth user if provided
        user_id = None
        user_email = None
        if authorization:
            try:
                user = await get_auth_user(authorization)
                user_id = user.id
                user_email = user.email
            except:
                pass  # Anonymous user allowed

        # Check if student already exists (if authenticated)
        existing_student = None
        if user_id:
            supabase = get_supabase_client()
            result = supabase.table('students').select('*').eq('user_id', user_id).execute()
            existing_student = result.data[0] if result.data else None

        # Use existing task counts or start fresh
        tasks_completed = existing_student.get("tasks_completed", 0) if existing_student else 0
        tasks_missed = existing_student.get("tasks_missed", 0) if existing_student else 0

        # Run agent pipeline
        plan_result = planner.run(skills, goal)
        eval_result = evaluator.run(skills, goal, tasks_completed, tasks_missed)
        dec_result = decision.run(eval_result["placement_probability"], tasks_missed, skills)
        strat_result = strategist.run(skills, goal)

        # Build student record
        student = {
            "user_id": user_id,  # None if anonymous
            "name": student_name,
            "email": user_email,
            "goal": goal,
            "skills": skills,
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "roadmap": plan_result["roadmap"],
            "status": dec_result["status"],
            "probability": eval_result["placement_probability"],
            "suggestions": [dec_result["recommendation"]],
            "alerts": dec_result["alerts"],
            "alternative_careers": strat_result.get("alternative_careers", []),
            "strategy": strat_result.get("strategy", ""),
            "explanation": eval_result["explanation"]
        }

        # If updating existing, set ID
        if existing_student:
            student["id"] = existing_student["id"]

        saved_student = upsert_student(student)

        return {
            "success": True,
            "student_id": saved_student["id"],
            "name": student_name,
            "skills": skills,
            "goal": goal,
            "roadmap": plan_result["roadmap"],
            "probability": eval_result["placement_probability"],
            "status": dec_result["status"],
            "explanation": eval_result["explanation"],
            "alternative_careers": strat_result.get("alternative_careers", []),
            "strategy": strat_result.get("strategy", ""),
            "alerts": dec_result["alerts"],
            "recommendation": dec_result["recommendation"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)[:200]}")

# ── ENDPOINT: Simulate ────────────────────────────────────────────────────────
@app.post("/simulate")
async def simulate(request: SimulateRequest):
    """
    Run Simulator Agent: show before/after probability with skill improvements.
    """
    try:
        result = simulator.run(
            request.skills,
            request.goal,
            request.tasks_completed,
            request.tasks_missed
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)[:200]}")

# ── ENDPOINT: Evaluate ────────────────────────────────────────────────────────
@app.post("/evaluate")
async def evaluate(request: EvaluateRequest):
    """
    Run Evaluator Agent: calculate placement probability.
    """
    try:
        student = get_student_by_id(request.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        result = evaluator.run(
            student["skills"],
            student["goal"],
            request.tasks_completed,
            request.tasks_missed
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)[:200]}")

# ── ENDPOINT: Update Tasks ────────────────────────────────────────────────────
@app.post("/update-tasks")
async def update_tasks(request: UpdateTasksRequest):
    """
    Update roadmap task states and recalculate probability.
    """
    try:
        student = get_student_by_id(request.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Count task states
        tasks_completed = sum(1 for t in request.roadmap if t.get("completed"))
        tasks_missed = sum(1 for t in request.roadmap if t.get("missed"))

        # Re-evaluate
        eval_result = evaluator.run(
            student["skills"],
            student["goal"],
            tasks_completed,
            tasks_missed
        )

        # Determine status
        probability = eval_result["placement_probability"]
        if probability >= 70:
            status = "Ready"
        elif probability >= 40:
            status = "Learning"
        else:
            status = "At Risk"

        # Update student
        updated = update_student_field(request.student_id, {
            "roadmap": request.roadmap,
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "probability": probability,
            "status": status,
            "alerts": eval_result.get("alerts", [])
        })

        return {
            "success": True,
            "probability": probability,
            "status": status,
            "tasks_completed": tasks_completed,
            "tasks_missed": tasks_missed,
            "alerts": eval_result.get("alerts", []),
            "recommendation": eval_result.get("explanation", "")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task update failed: {str(e)[:200]}")

# ── ENDPOINT: Decision ────────────────────────────────────────────────────────
@app.post("/decision")
async def run_decision(request: DecisionRequest):
    """
    Run Decision Agent: recommend actions based on status.
    """
    try:
        result = decision.run(
            request.probability,
            request.tasks_missed,
            request.skills
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision failed: {str(e)[:200]}")

# ── ENDPOINT: Admin Dashboard ─────────────────────────────────────────────────
@app.get("/admin-data")
async def admin_data(user = Depends(get_admin_user)):
    """
    Get all students for admin dashboard (requires admin role).
    """
    try:
        students = load_students()
        
        return {
            "success": True,
            "students": students,
            "total": len(students),
            "by_status": {
                "Ready": len([s for s in students if s.get("status") == "Ready"]),
                "Learning": len([s for s in students if s.get("status") == "Learning"]),
                "At Risk": len([s for s in students if s.get("status") == "At Risk"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin data: {str(e)[:200]}")

# ── Include Chat Router ───────────────────────────────────────────────────────
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
