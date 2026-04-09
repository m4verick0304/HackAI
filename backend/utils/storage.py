"""
storage.py - Supabase integration for student data persistence.
Provides CRUD functions for the students table in Supabase.
"""

import os
from datetime import datetime
from supabase import create_client, Client

# ── Supabase Configuration ────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase_client: Client = None

def get_supabase_client() -> Client:
    """Lazy-load Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
            )
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client

# ── CRUD Operations ──────────────────────────────────────────────────────────
def get_student_by_id(student_id: str) -> dict:
    """Fetch a student record by ID."""
    try:
        supabase = get_supabase_client()
        result = supabase.table('students').select('*').eq('id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"[Storage] Error fetching student: {e}")
        return None

def load_students() -> list:
    """
    Fetch all students (admin use).
    Consider pagination for large result sets.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table('students').select('*').execute()
        return result.data or []
    except Exception as e:
        print(f"[Storage] Error loading students: {e}")
        return []

def upsert_student(student_data: dict) -> dict:
    """
    Insert or update a student record.
    If 'id' is not provided, Supabase will auto-generate one.
    """
    try:
        supabase = get_supabase_client()
        
        # Set timestamps
        now = datetime.utcnow().isoformat() + 'Z'
        if 'id' not in student_data or not student_data['id']:
            student_data['created_at'] = now
        student_data['updated_at'] = now

        result = supabase.table('students').upsert(student_data).execute()
        if result.data:
            return result.data[0]
        raise Exception("Upsert returned no data")
    except Exception as e:
        print(f"[Storage] Error upserting student: {e}")
        raise

def update_student_field(student_id: str, fields: dict) -> dict:
    """Update specific fields for a student by ID."""
    try:
        supabase = get_supabase_client()
        
        fields['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        result = supabase.table('students').update(fields).eq('id', student_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[Storage] Error updating student: {e}")
        raise

def get_students_by_status(status: str) -> list:
    """Fetch all students with a specific status."""
    try:
        supabase = get_supabase_client()
        result = supabase.table('students').select('*').eq('status', status).execute()
        return result.data or []
    except Exception as e:
        print(f"[Storage] Error fetching students by status: {e}")
        return []

def get_admin_stats() -> dict:
    """Get dashboard stats for admin."""
    try:
        students = load_students()
        return {
            "total": len(students),
            "by_status": {
                "Ready": len([s for s in students if s.get("status") == "Ready"]),
                "Learning": len([s for s in students if s.get("status") == "Learning"]),
                "At Risk": len([s for s in students if s.get("status") == "At Risk"])
            }
        }
    except Exception as e:
        print(f"[Storage] Error getting stats: {e}")
        return {"total": 0, "by_status": {}}
