"""
parser.py - Resume/skill extraction utility
Parses free-text resume input to extract skills and keywords.
"""

import re

# Comprehensive skill dictionary organized by category
SKILL_KEYWORDS = {
    "programming": [
        "python", "java", "javascript", "js", "c++", "c#", "typescript", "golang", "go",
        "rust", "kotlin", "swift", "php", "ruby", "scala", "r lang", "matlab"
    ],
    "web": [
        "react", "angular", "vue", "nodejs", "node.js", "express", "django", "flask",
        "fastapi", "html", "css", "html5", "css3", "tailwind", "bootstrap", "next.js", "nextjs"
    ],
    "data": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "nosql", "pandas", "numpy",
        "matplotlib", "seaborn", "tableau", "power bi", "excel", "spark", "hadoop"
    ],
    "ml_ai": [
        "machine learning", "ml", "deep learning", "dl", "tensorflow", "pytorch", "keras",
        "scikit-learn", "sklearn", "nlp", "computer vision", "cv", "data science", "ai"
    ],
    "cs_fundamentals": [
        "dsa", "data structures", "algorithms", "system design", "os", "operating system",
        "dbms", "database", "networking", "oops", "object oriented", "design patterns"
    ],
    "tools": [
        "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux",
        "jenkins", "ci/cd", "postman", "jira", "agile", "scrum"
    ],
    "statistics": [
        "statistics", "probability", "linear algebra", "calculus", "regression",
        "classification", "clustering", "hypothesis testing"
    ]
}


def extract_skills(resume_text: str) -> list:
    """
    Extract skills from resume text using keyword matching.
    Returns a deduplicated list of matched skills.
    """
    text = resume_text.lower()
    found_skills = set()

    for category, skills in SKILL_KEYWORDS.items():
        for skill in skills:
            # Match whole word/phrase
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found_skills.add(skill)

    return list(found_skills)


def extract_name(resume_text: str) -> str:
    """
    Try to extract a name from resume text.
    Looks for a name at the very top of the resume.
    """
    lines = resume_text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) <= 4 and not any(c in line for c in ['@', ':', '.com', 'http']):
            words = line.split()
            if all(w[0].isupper() for w in words if w):
                return line
    return "Student"


def parse_resume(resume_text: str) -> dict:
    """
    Main parser function. Extracts name and skills from resume text.
    """
    skills = extract_skills(resume_text)
    name = extract_name(resume_text)

    return {
        "name": name,
        "skills": skills,
        "raw_text": resume_text[:500]  # Store preview
    }
