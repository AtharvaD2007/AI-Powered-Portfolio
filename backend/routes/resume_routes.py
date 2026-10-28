"""
Dynamic Resume Generator Routes.
Allows selecting verified portfolio items via checkboxes,
generates ATS-optimized summaries, produces live previews,
and exports clean ReportLab PDFs.
Supports multiple job-specific resume versions without modifying the primary portfolio.
"""

import json
from flask import Blueprint, request, jsonify, send_file, Response
import io
from backend.database import get_db_connection, get_full_portfolio
from backend.services.resume_pdf_service import ResumePDFService
from backend.services.gemini_service import GeminiService

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resumes")
pdf_service = ResumePDFService()
gemini_service = GeminiService()

def assemble_resume_payload(selected_items: dict, custom_summary: str = "", target_role: str = ""):
    """
    Filters the master portfolio to only include items selected by the user.
    selected_items is a dict like:
    {
      "include_profile": true,
      "education_ids": [1],
      "skill_ids": [1, 2, 4],
      "project_ids": [1, 3],
      "experience_ids": [1],
      "certification_ids": [1, 2],
      "achievement_ids": [1]
    }
    """
    portfolio = get_full_portfolio()

    # Filter Education
    edu_ids = set(selected_items.get("education_ids", []))
    filtered_edu = [e for e in portfolio.get("education", []) if e.get("id") in edu_ids] if edu_ids else portfolio.get("education", [])

    # Filter Skills
    sk_ids = set(selected_items.get("skill_ids", []))
    filtered_skills = [s for s in portfolio.get("skills", []) if s.get("id") in sk_ids] if sk_ids else portfolio.get("skills", [])

    # Filter Projects
    proj_ids = set(selected_items.get("project_ids", []))
    filtered_projects = [p for p in portfolio.get("projects", []) if p.get("id") in proj_ids] if proj_ids else portfolio.get("projects", [])

    # Filter Experiences
    exp_ids = set(selected_items.get("experience_ids", []))
    filtered_experiences = [e for e in portfolio.get("experiences", []) if e.get("id") in exp_ids] if exp_ids else portfolio.get("experiences", [])

    # Filter Certifications
    cert_ids = set(selected_items.get("certification_ids", []))
    filtered_certs = [c for c in portfolio.get("certifications", []) if c.get("id") in cert_ids] if cert_ids else portfolio.get("certifications", [])

    # Filter Achievements
    ach_ids = set(selected_items.get("achievement_ids", []))
    filtered_achievements = [a for a in portfolio.get("achievements", []) if a.get("id") in ach_ids] if ach_ids else portfolio.get("achievements", [])

    return {
        "profile": portfolio.get("profile", {}),
        "target_role": target_role,
        "custom_summary": custom_summary,
        "education": filtered_edu,
        "skills": filtered_skills,
        "projects": filtered_projects,
        "experiences": filtered_experiences,
        "certifications": filtered_certs,
        "achievements": filtered_achievements,
    }

@resume_bp.route("", methods=["GET"])
def list_resumes():
    """Lists saved resume versions."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.id, r.title, r.target_role, r.job_description_id, r.created_at, r.updated_at,
               j.title as job_title, j.company as job_company
        FROM resumes r
        LEFT JOIN job_descriptions j ON r.job_description_id = j.id
        ORDER BY r.updated_at DESC
        """
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@resume_bp.route("/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    """Retrieves a specific saved resume."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Resume not found."}), 404

    d = dict(row)
    if d.get("selected_items"):
        try:
            d["selected_items"] = json.loads(d["selected_items"])
        except Exception:
            pass
    if d.get("generated_content"):
        try:
            d["generated_content"] = json.loads(d["generated_content"])
        except Exception:
            pass

    return jsonify({"success": True, "data": d})

@resume_bp.route("/generate-summary", methods=["POST"])
def generate_tailored_summary():
    """Generates an ATS-optimized summary strictly from verified portfolio data."""
    data = request.get_json() or {}
    target_role = data.get("target_role", "Software Engineer")
    job_description = data.get("job_description", "")
    selected_items = data.get("selected_items", {})

    assembled = assemble_resume_payload(selected_items, target_role=target_role)

    summary = gemini_service.generate_tailored_summary(
        target_role=target_role,
        job_description=job_description,
        verified_profile=assembled["profile"],
        verified_skills=assembled["skills"],
        verified_projects=assembled["projects"]
    )

    return jsonify({"success": True, "summary": summary})

@resume_bp.route("/preview", methods=["POST"])
def preview_resume():
    """Assembles and returns a preview payload of the tailored resume."""
    data = request.get_json() or {}
    selected_items = data.get("selected_items", {})
    custom_summary = data.get("custom_summary", "")
    target_role = data.get("target_role", "")

    assembled = assemble_resume_payload(selected_items, custom_summary=custom_summary, target_role=target_role)
    return jsonify({"success": True, "preview": assembled})

@resume_bp.route("/save", methods=["POST"])
def save_resume():
    """Saves a job-specific resume configuration to SQLite."""
    data = request.get_json() or {}
    title = data.get("title", "Tailored Resume")
    target_role = data.get("target_role", "")
    job_description_id = data.get("job_description_id")
    custom_summary = data.get("custom_summary", "")
    selected_items = data.get("selected_items", {})

    assembled = assemble_resume_payload(selected_items, custom_summary=custom_summary, target_role=target_role)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resumes (title, job_description_id, target_role, custom_summary, selected_items, generated_content)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            job_description_id,
            target_role,
            custom_summary,
            json.dumps(selected_items),
            json.dumps(assembled),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"success": True, "id": new_id, "message": "Resume version saved successfully."}), 201

@resume_bp.route("/download-pdf", methods=["POST"])
def download_resume_pdf():
    """Generates and streams the ReportLab PDF for download."""
    data = request.get_json() or {}
    selected_items = data.get("selected_items", {})
    custom_summary = data.get("custom_summary", "")
    target_role = data.get("target_role", "")

    assembled = assemble_resume_payload(selected_items, custom_summary=custom_summary, target_role=target_role)

    try:
        pdf_bytes = pdf_service.generate_resume_pdf(assembled)
        candidate_name = assembled["profile"].get("full_name", "Candidate").replace(" ", "_")
        role_slug = target_role.replace(" ", "_") if target_role else "Resume"
        filename = f"{candidate_name}_{role_slug}_Resume.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate PDF: {str(e)}"}), 500

@resume_bp.route("/<int:resume_id>/download-pdf", methods=["GET"])
def download_saved_resume_pdf(resume_id):
    """Downloads a saved resume by ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Resume not found."}), 404

    d = dict(row)
    assembled = None
    if d.get("generated_content"):
        try:
            assembled = json.loads(d["generated_content"])
        except Exception:
            pass

    if not assembled and d.get("selected_items"):
        try:
            selected_items = json.loads(d["selected_items"])
            assembled = assemble_resume_payload(
                selected_items,
                custom_summary=d.get("custom_summary", ""),
                target_role=d.get("target_role", "")
            )
        except Exception:
            pass

    if not assembled:
        assembled = assemble_resume_payload({})

    try:
        pdf_bytes = pdf_service.generate_resume_pdf(assembled)
        candidate_name = assembled["profile"].get("full_name", "Candidate").replace(" ", "_")
        filename = f"{candidate_name}_{d.get('target_role', 'Resume').replace(' ', '_')}.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate PDF: {str(e)}"}), 500
