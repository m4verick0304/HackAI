"""
routers/chat.py — Chat endpoints for PrepGenie
  POST /chat/analyze  — resume + GitHub + LeetCode → AI analysis
  POST /chat/message  — conversational AI placement coach
"""

import json
import io
import httpx
import asyncio
from typing import Optional

from fastapi import APIRouter, Form, UploadFile, File, HTTPException

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from services.gemini import get_ai_response

router = APIRouter()

# ── LeetCode GraphQL Query ────────────────────────────────────────────────────
LEETCODE_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
      reputation
      starRating
    }
    languageProblemCount {
      languageName
      problemsSolved
    }
  }
}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _parse_pdf(file: UploadFile) -> str:
    """Extract plain text from an uploaded PDF using pdfplumber."""
    if not PDF_AVAILABLE:
        return "[pdfplumber not installed — pip install pdfplumber]"
    try:
        contents = await file.read()
        text_pages = []
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)
        return "\n".join(text_pages).strip() or "[No text found in PDF]"
    except Exception as e:
        return f"[PDF parse error: {e}]"


async def _fetch_github(username: str) -> dict:
    """Fetch basic GitHub profile and top repos."""
    result = {"profile": {}, "repos": [], "error": None}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            profile_resp, repos_resp = await asyncio.gather(
                client.get(
                    f"https://api.github.com/users/{username}",
                    headers={"Accept": "application/vnd.github+json"},
                ),
                client.get(
                    f"https://api.github.com/users/{username}/repos",
                    params={"sort": "updated", "per_page": 10},
                    headers={"Accept": "application/vnd.github+json"},
                ),
            )
        if profile_resp.status_code == 200:
            p = profile_resp.json()
            result["profile"] = {
                "name": p.get("name"),
                "public_repos": p.get("public_repos"),
                "followers": p.get("followers"),
                "bio": p.get("bio"),
                "company": p.get("company"),
                "location": p.get("location"),
            }
        else:
            result["error"] = f"GitHub API {profile_resp.status_code}"

        if repos_resp.status_code == 200:
            repos = repos_resp.json()
            result["repos"] = [
                {
                    "name": r["name"],
                    "language": r.get("language"),
                    "stars": r.get("stargazers_count", 0),
                    "description": r.get("description", ""),
                }
                for r in repos
                if not r.get("fork")
            ][:8]  # Keep top 8 original repos
    except Exception as e:
        result["error"] = str(e)
    return result


async def _fetch_leetcode(username: str) -> dict:
    """Fetch LeetCode stats via their public GraphQL endpoint."""
    result = {"stats": {}, "error": None}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://leetcode.com/graphql",
                json={"query": LEETCODE_QUERY, "variables": {"username": username}},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                },
            )
        if resp.status_code == 200:
            data = resp.json()
            user = (data.get("data") or {}).get("matchedUser")
            if user:
                submission_stats = {
                    item["difficulty"]: item["count"]
                    for item in (user.get("submitStats") or {}).get("acSubmissionNum", [])
                }
                result["stats"] = {
                    "ranking": (user.get("profile") or {}).get("ranking"),
                    "easy_solved": submission_stats.get("Easy", 0),
                    "medium_solved": submission_stats.get("Medium", 0),
                    "hard_solved": submission_stats.get("Hard", 0),
                    "top_languages": [
                        lp["languageName"]
                        for lp in (user.get("languageProblemCount") or [])[:3]
                    ],
                }
            else:
                result["error"] = "LeetCode user not found"
        else:
            result["error"] = f"LeetCode API {resp.status_code}"
    except Exception as e:
        result["error"] = str(e)
    return result


def _build_analyze_context(
    resume_text: str,
    github_data: Optional[dict],
    leetcode_data: Optional[dict],
) -> str:
    """Combine all data sources into a single context string for Gemini."""
    parts = []

    if resume_text:
        parts.append(f"=== RESUME ===\n{resume_text[:4000]}")

    if github_data and not github_data.get("error"):
        p = github_data["profile"]
        repos_summary = "\n".join(
            f"  - {r['name']} ({r['language'] or 'unknown'}) ★{r['stars']}: {r['description'][:80]}"
            for r in github_data.get("repos", [])
        )
        parts.append(
            f"=== GITHUB PROFILE ===\n"
            f"Name: {p.get('name')}\n"
            f"Public Repos: {p.get('public_repos')}\n"
            f"Followers: {p.get('followers')}\n"
            f"Bio: {p.get('bio')}\n"
            f"Top Repos:\n{repos_summary}"
        )
    elif github_data and github_data.get("error"):
        parts.append(f"=== GITHUB === [Error: {github_data['error']}]")

    if leetcode_data and not leetcode_data.get("error"):
        s = leetcode_data["stats"]
        parts.append(
            f"=== LEETCODE STATS ===\n"
            f"Global Ranking: {s.get('ranking')}\n"
            f"Easy Solved: {s.get('easy_solved')}\n"
            f"Medium Solved: {s.get('medium_solved')}\n"
            f"Hard Solved: {s.get('hard_solved')}\n"
            f"Top Languages: {', '.join(s.get('top_languages', []))}"
        )
    elif leetcode_data and leetcode_data.get("error"):
        parts.append(f"=== LEETCODE === [Error: {leetcode_data['error']}]")

    return "\n\n".join(parts) if parts else "No data provided."


ANALYZE_PROMPT_TEMPLATE = """
You are PrepGenie, an expert AI placement coach. Analyze the following student data and provide a comprehensive placement readiness report.

{context}

Based on this data, provide a structured JSON response with EXACTLY these fields:
{{
  "skill_assessment": "2–3 sentence assessment of the student's current technical skills",
  "readiness_score": <integer 0–100>,
  "readiness_label": "one of: Beginner / Developing / Intermediate / Advanced / Job-Ready",
  "top_companies": ["Company 1", "Company 2", "Company 3"],
  "skill_gaps": ["gap 1", "gap 2", "gap 3", "gap 4"],
  "thirty_day_plan": [
    {{"week": 1, "focus": "...", "tasks": ["task1", "task2", "task3"]}},
    {{"week": 2, "focus": "...", "tasks": ["task1", "task2", "task3"]}},
    {{"week": 3, "focus": "...", "tasks": ["task1", "task2", "task3"]}},
    {{"week": 4, "focus": "...", "tasks": ["task1", "task2", "task3"]}}
  ],
  "practice_problems": [
    {{"title": "...", "difficulty": "Easy|Medium|Hard", "topic": "...", "url": "https://leetcode.com/problems/..."}},
    {{"title": "...", "difficulty": "Easy|Medium|Hard", "topic": "...", "url": "https://leetcode.com/problems/..."}},
    {{"title": "...", "difficulty": "Easy|Medium|Hard", "topic": "...", "url": "https://leetcode.com/problems/..."}},
    {{"title": "...", "difficulty": "Easy|Medium|Hard", "topic": "...", "url": "https://leetcode.com/problems/..."}},
    {{"title": "...", "difficulty": "Easy|Medium|Hard", "topic": "...", "url": "https://leetcode.com/problems/..."}}
  ],
  "immediate_next_step": "One specific, actionable thing the student should do TODAY"
}}

Return ONLY the JSON object. No markdown fences, no extra text.
""".strip()

COACH_SYSTEM_PROMPT = """
You are PrepGenie, an expert AI placement coach specializing in helping students land software engineering jobs.
You have deep knowledge of DSA, system design, behavioral interviews, resume writing, and company hiring processes.
Your tone is encouraging, specific, and action-oriented.
Keep answers concise (under 250 words unless the user asks for detail).
Always end with one concrete action the student can take right now.
""".strip()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze(
    resume: Optional[UploadFile] = File(None),
    github_username: Optional[str] = Form(None),
    leetcode_username: Optional[str] = Form(None),
):
    """
    Analyze student data from resume PDF, GitHub, and LeetCode.
    Returns a structured AI assessment.
    """
    if not resume and not github_username and not leetcode_username:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: resume, github_username, leetcode_username",
        )

    # Gather all data concurrently
    tasks = []

    resume_task = _parse_pdf(resume) if resume else asyncio.coroutine(lambda: "")()
    github_task = _fetch_github(github_username) if github_username else asyncio.coroutine(lambda: None)()
    leetcode_task = _fetch_leetcode(leetcode_username) if leetcode_username else asyncio.coroutine(lambda: None)()

    resume_text, github_data, leetcode_data = await asyncio.gather(
        _parse_pdf(resume) if resume else _noop(""),
        _fetch_github(github_username) if github_username else _noop(None),
        _fetch_leetcode(leetcode_username) if leetcode_username else _noop(None),
    )

    context = _build_analyze_context(resume_text, github_data, leetcode_data)
    prompt = ANALYZE_PROMPT_TEMPLATE.format(context=context)

    ai_response = await get_ai_response(prompt)

    # Parse the JSON the model returns
    try:
        # Strip potential markdown fences just in case
        clean = ai_response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        analysis = json.loads(clean)
    except json.JSONDecodeError:
        # Return raw text if parsing fails
        analysis = {"raw_response": ai_response, "parse_error": True}

    return {
        "success": True,
        "analysis": analysis,
        "sources": {
            "resume_parsed": bool(resume_text and not resume_text.startswith("[")),
            "github_fetched": bool(github_data and not github_data.get("error")),
            "leetcode_fetched": bool(leetcode_data and not leetcode_data.get("error")),
        },
    }


@router.post("/message")
async def message(
    message: str = Form(...),
    history: str = Form(default="[]"),
    student_context: str = Form(default=""),
):
    """
    Conversational AI placement coach endpoint.
    Accepts a message + JSON history array + optional student context string.
    """
    try:
        history_list: list[dict] = json.loads(history)
    except (json.JSONDecodeError, ValueError):
        history_list = []

    # Prepend student context to the user message if provided
    full_prompt = message
    if student_context:
        full_prompt = (
            f"[Student context: {student_context[:1000]}]\n\n"
            f"Student question: {message}"
        )

    ai_response = await get_ai_response(
        prompt=full_prompt,
        history=history_list,
        system=COACH_SYSTEM_PROMPT,
    )

    return {
        "success": True,
        "reply": ai_response,
        "role": "model",
    }


# ── Utility ───────────────────────────────────────────────────────────────────

async def _noop(value):
    """Async no-op that returns a constant value."""
    return value
