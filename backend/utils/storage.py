"""
storage.py - JSON-based data persistence utility
Handles reading and writing student data to/from the local JSON file.
"""

import json
import os
import uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'students.json')


def load_students():
    """Load all students from JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_students(students):
    """Save all students to JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(students, f, indent=2)


def get_student_by_id(student_id):
    """Find a student by their ID."""
    students = load_students()
    for student in students:
        if student.get('id') == student_id:
            return student
    return None


def upsert_student(student_data):
    """Insert or update a student record. Returns the student with ID."""
    students = load_students()
    
    # Check if student already exists
    student_id = student_data.get('id')
    if student_id:
        for i, s in enumerate(students):
            if s.get('id') == student_id:
                students[i] = student_data
                save_students(students)
                return student_data
    
    # New student — create ID
    student_data['id'] = f"student_{uuid.uuid4().hex[:8]}"
    student_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
    students.append(student_data)
    save_students(students)
    return student_data


def update_student_field(student_id, fields: dict):
    """Update specific fields for a student by ID."""
    students = load_students()
    for i, s in enumerate(students):
        if s.get('id') == student_id:
            students[i].update(fields)
            save_students(students)
            return students[i]
    return None
