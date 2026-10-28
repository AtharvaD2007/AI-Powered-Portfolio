"""
Job Description Analyzer Routes.
Extracts requirements, evaluates verified portfolio records,
calculates transparent match scores, and recommends projects.
"""

from flask import Blueprint, request, jsonify
from backend.database import get_db_connection, get_full_portfolio
from backend.services.analyzer_service import AnalyzerService

analyzer_bp = Blueprint("analyzer", __name__, url_prefix="/api/analyzer")
analyzer_service = AnalyzerService()

@analyzer_bp.route("/jobs", methods=["GET"])
def get_jobs():
    """Returns saved job descriptions including the sample ones."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, company, target_role, raw_text, created_at FROM job_descriptions ORDER BY id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@analyzer_bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Job description not found."}), 404
    return jsonify({"success": True, "data": dict(row)})

@analyzer_bp.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    raw_text = data.get("raw_text", "").strip()

    if not title or not raw_text:
        return jsonify({"success": False, "error": "Title and job description text are required."}), 400

    company = data.get("company", "").strip()
    target_role = data.get("target_role", title).strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO job_descriptions (title, company, raw_text, target_role)
        VALUES (?, ?, ?, ?)
        """,
        (title, company, raw_text, target_role),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Job description saved."}), 201

@analyzer_bp.route("/match", methods=["POST"])
def analyze_and_match():
    """
    Accepts job_text (or job_id) and analyzes it against the current portfolio.
    Returns transparent match score, matched skills, missing skills, and recommended projects.
    """
    data = request.get_json() or {}
    job_text = data.get("raw_text", "")
    job_title = data.get("title", "")
    job_id = data.get("job_id")

    if job_id and not job_text:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
        job_row = cur.fetchone()
        conn.close()
        if job_row:
            job_text = job_row["raw_text"]
            job_title = job_row["title"]

    if not job_text or not job_text.strip():
        return jsonify({"success": False, "error": "Please provide job description text to analyze."}), 400

    portfolio = get_full_portfolio()
    result = analyzer_service.analyze_job_against_portfolio(job_text, portfolio, job_title)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify({"success": True, "analysis": result})
