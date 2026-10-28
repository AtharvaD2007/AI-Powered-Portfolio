"""
AI Portfolio Organizer Routes.
Parses raw unstructured text, generates structured portfolio proposals,
shows changes for user approval, and preserves original information.
"""

import json
from flask import Blueprint, request, jsonify
from backend.database import get_db_connection
from backend.services.gemini_service import GeminiService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")
gemini_service = GeminiService()

@ai_bp.route("/organize", methods=["POST"])
def organize_text():
    """
    Accepts raw unstructured user text.
    Uses Gemini to organize it into structured portfolio categories.
    Stores the raw input and parsed output in organizer_history to preserve original information.
    """
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()

    if not raw_text:
        return jsonify({"success": False, "error": "Please provide some unstructured text to organize."}), 400

    # Call Gemini service (or fallback heuristic parser)
    result = gemini_service.parse_unstructured_portfolio(raw_text)
    if not result.get("success"):
        return jsonify(result), 400

    parsed_data = result.get("data", {})

    # Save to organizer_history to preserve original information
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO organizer_history (raw_input, parsed_output, status)
        VALUES (?, ?, 'pending')
        """,
        (raw_text, json.dumps(parsed_data)),
    )
    history_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "history_id": history_id,
        "proposed_changes": parsed_data,
        "source": result.get("source"),
        "warning": result.get("warning"),
        "message": "Information parsed successfully. Please review the proposed changes before saving."
    })

@ai_bp.route("/approve", methods=["POST"])
def approve_changes():
    """
    Approves and applies user-verified changes into the portfolio database.
    Does NOT wipe existing records; intelligently appends new skills/projects/education
    or merges profile fields with user consent.
    """
    data = request.get_json() or {}
    history_id = data.get("history_id")
    approved_payload = data.get("approved_data")

    if not approved_payload:
        return jsonify({"success": False, "error": "No approved data provided."}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    applied_summary = {
        "profile_updated": False,
        "education_added": 0,
        "skills_added": 0,
        "certifications_added": 0,
        "projects_added": 0,
        "experiences_added": 0,
        "achievements_added": 0
    }

    # 1. Profile updates (only if fields are non-empty)
    prof = approved_payload.get("profile", {})
    if any(prof.values()):
        cur.execute("SELECT * FROM profile ORDER BY id LIMIT 1")
        existing_prof = cur.fetchone()
        if existing_prof:
            # Only update fields that have content
            cur.execute(
                """
                UPDATE profile
                SET full_name = COALESCE(NULLIF(?, ''), full_name),
                    headline = COALESCE(NULLIF(?, ''), headline),
                    email = COALESCE(NULLIF(?, ''), email),
                    phone = COALESCE(NULLIF(?, ''), phone),
                    location = COALESCE(NULLIF(?, ''), location),
                    github_url = COALESCE(NULLIF(?, ''), github_url),
                    linkedin_url = COALESCE(NULLIF(?, ''), linkedin_url),
                    portfolio_url = COALESCE(NULLIF(?, ''), portfolio_url),
                    summary = COALESCE(NULLIF(?, ''), summary),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    prof.get("full_name", ""),
                    prof.get("headline", ""),
                    prof.get("email", ""),
                    prof.get("phone", ""),
                    prof.get("location", ""),
                    prof.get("github_url", ""),
                    prof.get("linkedin_url", ""),
                    prof.get("portfolio_url", ""),
                    prof.get("summary", ""),
                    existing_prof["id"]
                )
            )
        else:
            cur.execute(
                """
                INSERT INTO profile (full_name, headline, email, phone, location, github_url, linkedin_url, portfolio_url, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prof.get("full_name", ""),
                    prof.get("headline", ""),
                    prof.get("email", ""),
                    prof.get("phone", ""),
                    prof.get("location", ""),
                    prof.get("github_url", ""),
                    prof.get("linkedin_url", ""),
                    prof.get("portfolio_url", ""),
                    prof.get("summary", ""),
                )
            )
        applied_summary["profile_updated"] = True

    # 2. Education
    for edu in approved_payload.get("education", []):
        if edu.get("institution") and edu.get("degree"):
            cur.execute(
                """
                INSERT INTO education (institution, degree, field_of_study, start_date, end_date, gpa, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edu.get("institution"),
                    edu.get("degree"),
                    edu.get("field_of_study", ""),
                    edu.get("start_date", ""),
                    edu.get("end_date", ""),
                    edu.get("gpa", ""),
                    edu.get("description", "")
                )
            )
            applied_summary["education_added"] += 1

    # 3. Skills (Avoid exact name duplicates)
    for sk in approved_payload.get("skills", []):
        name = sk.get("name", "").strip()
        if name:
            cur.execute("SELECT id FROM skills WHERE LOWER(name) = LOWER(?)", (name,))
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO skills (name, category, proficiency, years_of_experience)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name, sk.get("category", "General"), sk.get("proficiency", "Intermediate"), float(sk.get("years_of_experience", 1.0)))
                )
                applied_summary["skills_added"] += 1

    # 4. Certifications
    for c in approved_payload.get("certifications", []):
        if c.get("name") and c.get("issuing_organization"):
            cur.execute(
                """
                INSERT INTO certifications (name, issuing_organization, issue_date, expiration_date, credential_id, credential_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    c.get("name"),
                    c.get("issuing_organization"),
                    c.get("issue_date", ""),
                    c.get("expiration_date", ""),
                    c.get("credential_id", ""),
                    c.get("credential_url", "")
                )
            )
            applied_summary["certifications_added"] += 1

    # 5. Projects
    for p in approved_payload.get("projects", []):
        if p.get("title") and p.get("description"):
            tech = p.get("tech_stack", [])
            if isinstance(tech, list):
                tech = json.dumps(tech)
            highlights = p.get("highlights", [])
            if isinstance(highlights, list):
                highlights = json.dumps(highlights)

            cur.execute(
                """
                INSERT INTO projects (title, description, tech_stack, role, highlights, live_url, repo_url, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p.get("title"),
                    p.get("description"),
                    tech,
                    p.get("role", "Developer"),
                    highlights,
                    p.get("live_url", ""),
                    p.get("repo_url", ""),
                    p.get("start_date", ""),
                    p.get("end_date", "")
                )
            )
            applied_summary["projects_added"] += 1

    # 6. Experiences
    for e in approved_payload.get("experiences", []):
        if e.get("company") and e.get("role"):
            highlights = e.get("highlights", [])
            if isinstance(highlights, list):
                highlights = json.dumps(highlights)

            cur.execute(
                """
                INSERT INTO experiences (company, role, location, start_date, end_date, is_current, description, highlights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    e.get("company"),
                    e.get("role"),
                    e.get("location", ""),
                    e.get("start_date", ""),
                    e.get("end_date", ""),
                    1 if e.get("is_current") else 0,
                    e.get("description", ""),
                    highlights
                )
            )
            applied_summary["experiences_added"] += 1

    # 7. Achievements
    for a in approved_payload.get("achievements", []):
        if a.get("title"):
            cur.execute(
                """
                INSERT INTO achievements (title, type, issuer_or_publisher, date, description, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    a.get("title"),
                    a.get("type", "Achievement"),
                    a.get("issuer_or_publisher", ""),
                    a.get("date", ""),
                    a.get("description", ""),
                    a.get("url", "")
                )
            )
            applied_summary["achievements_added"] += 1

    # Mark history status as approved
    if history_id:
        cur.execute("UPDATE organizer_history SET status = 'approved' WHERE id = ?", (history_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Approved items successfully incorporated into your portfolio.",
        "summary": applied_summary
    })

@ai_bp.route("/history", methods=["GET"])
def get_history():
    """Returns past organizer submissions to verify original data preservation."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, raw_input, status, created_at FROM organizer_history ORDER BY created_at DESC LIMIT 20")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})
