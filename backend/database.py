import sqlite3
import json
from pathlib import Path
from backend.config import Config
from backend.sample_data import (
    SAMPLE_PROFILE,
    SAMPLE_EDUCATION,
    SAMPLE_SKILLS,
    SAMPLE_CERTIFICATIONS,
    SAMPLE_PROJECTS,
    SAMPLE_EXPERIENCE,
    SAMPLE_ACHIEVEMENTS,
    SAMPLE_JOB_DESCRIPTIONS,
)

SCHEMA_FILE = Path(__file__).resolve().parent / "database_schema.sql"

def get_db_connection():
    """Returns a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force_sample_data=False):
    """Initializes the database schema and loads sample data if empty."""
    conn = get_db_connection()
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()

    # Check if profile table is empty
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profile")
    profile_count = cur.fetchone()[0]

    if profile_count == 0 or force_sample_data:
        load_sample_data(conn, clear_existing=force_sample_data)

    conn.close()

def load_sample_data(conn=None, clear_existing=False):
    """Loads rich sample candidate data and job descriptions into the database."""
    close_when_done = False
    if conn is None:
        conn = get_db_connection()
        close_when_done = True

    cur = conn.cursor()

    if clear_existing:
        tables = [
            "resumes",
            "job_descriptions",
            "achievements",
            "experiences",
            "projects",
            "certifications",
            "skills",
            "education",
            "profile",
            "organizer_history",
        ]
        for t in tables:
            cur.execute(f"DELETE FROM {t}")

    # 1. Profile
    cur.execute("SELECT COUNT(*) FROM profile")
    if cur.fetchone()[0] == 0:
        cur.execute(
            """
            INSERT INTO profile (full_name, headline, email, phone, location, github_url, linkedin_url, portfolio_url, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                SAMPLE_PROFILE["full_name"],
                SAMPLE_PROFILE["headline"],
                SAMPLE_PROFILE["email"],
                SAMPLE_PROFILE["phone"],
                SAMPLE_PROFILE["location"],
                SAMPLE_PROFILE["github_url"],
                SAMPLE_PROFILE["linkedin_url"],
                SAMPLE_PROFILE["portfolio_url"],
                SAMPLE_PROFILE["summary"],
            ),
        )

    # 2. Education
    cur.execute("SELECT COUNT(*) FROM education")
    if cur.fetchone()[0] == 0:
        for edu in SAMPLE_EDUCATION:
            cur.execute(
                """
                INSERT INTO education (institution, degree, field_of_study, start_date, end_date, gpa, description, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edu["institution"],
                    edu["degree"],
                    edu["field_of_study"],
                    edu["start_date"],
                    edu["end_date"],
                    edu["gpa"],
                    edu["description"],
                    edu["order_index"],
                ),
            )

    # 3. Skills
    cur.execute("SELECT COUNT(*) FROM skills")
    if cur.fetchone()[0] == 0:
        for sk in SAMPLE_SKILLS:
            cur.execute(
                """
                INSERT INTO skills (name, category, proficiency, years_of_experience)
                VALUES (?, ?, ?, ?)
                """,
                (sk["name"], sk["category"], sk["proficiency"], sk["years_of_experience"]),
            )

    # 4. Certifications
    cur.execute("SELECT COUNT(*) FROM certifications")
    if cur.fetchone()[0] == 0:
        for cert in SAMPLE_CERTIFICATIONS:
            cur.execute(
                """
                INSERT INTO certifications (name, issuing_organization, issue_date, expiration_date, credential_id, credential_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cert["name"],
                    cert["issuing_organization"],
                    cert["issue_date"],
                    cert["expiration_date"],
                    cert["credential_id"],
                    cert["credential_url"],
                ),
            )

    # 5. Projects
    cur.execute("SELECT COUNT(*) FROM projects")
    if cur.fetchone()[0] == 0:
        for proj in SAMPLE_PROJECTS:
            cur.execute(
                """
                INSERT INTO projects (title, description, tech_stack, role, highlights, live_url, repo_url, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proj["title"],
                    proj["description"],
                    proj["tech_stack"],
                    proj["role"],
                    proj["highlights"],
                    proj["live_url"],
                    proj["repo_url"],
                    proj["start_date"],
                    proj["end_date"],
                ),
            )

    # 6. Experiences
    cur.execute("SELECT COUNT(*) FROM experiences")
    if cur.fetchone()[0] == 0:
        for exp in SAMPLE_EXPERIENCE:
            cur.execute(
                """
                INSERT INTO experiences (company, role, location, start_date, end_date, is_current, description, highlights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exp["company"],
                    exp["role"],
                    exp["location"],
                    exp["start_date"],
                    exp["end_date"],
                    exp["is_current"],
                    exp["description"],
                    exp["highlights"],
                ),
            )

    # 7. Achievements
    cur.execute("SELECT COUNT(*) FROM achievements")
    if cur.fetchone()[0] == 0:
        for ach in SAMPLE_ACHIEVEMENTS:
            cur.execute(
                """
                INSERT INTO achievements (title, type, issuer_or_publisher, date, description, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ach["title"],
                    ach["type"],
                    ach["issuer_or_publisher"],
                    ach["date"],
                    ach["description"],
                    ach["url"],
                ),
            )

    # 8. Sample Job Descriptions
    cur.execute("SELECT COUNT(*) FROM job_descriptions")
    if cur.fetchone()[0] == 0:
        for jd in SAMPLE_JOB_DESCRIPTIONS:
            cur.execute(
                """
                INSERT INTO job_descriptions (title, company, target_role, raw_text)
                VALUES (?, ?, ?, ?)
                """,
                (jd["title"], jd["company"], jd["target_role"], jd["raw_text"]),
            )

    conn.commit()
    if close_when_done:
        conn.close()

def get_full_portfolio():
    """Retrieves all portfolio sections as a dictionary of native Python data structures."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Profile
    cur.execute("SELECT * FROM profile ORDER BY id LIMIT 1")
    profile_row = cur.fetchone()
    profile = dict(profile_row) if profile_row else {}

    # Education
    cur.execute("SELECT * FROM education ORDER BY order_index, start_date DESC")
    education = [dict(row) for row in cur.fetchall()]

    # Skills
    cur.execute("SELECT * FROM skills ORDER BY category, name")
    skills = [dict(row) for row in cur.fetchall()]

    # Certifications
    cur.execute("SELECT * FROM certifications ORDER BY issue_date DESC")
    certifications = [dict(row) for row in cur.fetchall()]

    # Projects
    cur.execute("SELECT * FROM projects ORDER BY start_date DESC")
    projects = []
    for row in cur.fetchall():
        d = dict(row)
        if d.get("tech_stack"):
            try:
                d["tech_stack_list"] = json.loads(d["tech_stack"])
            except Exception:
                d["tech_stack_list"] = [t.strip() for t in d["tech_stack"].split(",") if t.strip()]
        else:
            d["tech_stack_list"] = []
        if d.get("highlights"):
            try:
                d["highlights_list"] = json.loads(d["highlights"])
            except Exception:
                d["highlights_list"] = [d["highlights"]]
        else:
            d["highlights_list"] = []
        projects.append(d)

    # Experiences
    cur.execute("SELECT * FROM experiences ORDER BY is_current DESC, start_date DESC")
    experiences = []
    for row in cur.fetchall():
        d = dict(row)
        if d.get("highlights"):
            try:
                d["highlights_list"] = json.loads(d["highlights"])
            except Exception:
                d["highlights_list"] = [d["highlights"]]
        else:
            d["highlights_list"] = []
        experiences.append(d)

    # Achievements
    cur.execute("SELECT * FROM achievements ORDER BY date DESC")
    achievements = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "profile": profile,
        "education": education,
        "skills": skills,
        "certifications": certifications,
        "projects": projects,
        "experiences": experiences,
        "achievements": achievements,
    }
