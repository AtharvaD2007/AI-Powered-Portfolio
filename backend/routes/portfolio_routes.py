"""
Portfolio CRUD Routes.
Manages Profile, Education, Skills, Certifications, Projects, Experiences, Achievements.
"""

import json
from flask import Blueprint, request, jsonify
from backend.database import get_db_connection, get_full_portfolio, load_sample_data

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")

@portfolio_bp.route("", methods=["GET"])
def get_portfolio():
    """Returns the entire portfolio structure."""
    try:
        data = get_full_portfolio()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@portfolio_bp.route("/reset-sample", methods=["POST"])
def reset_to_sample():
    """Resets the entire portfolio to the rich dual-skill sample candidate."""
    try:
        load_sample_data(clear_existing=True)
        data = get_full_portfolio()
        return jsonify({"success": True, "message": "Portfolio reset to sample candidate successfully.", "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------- Profile -----------------
@portfolio_bp.route("/profile", methods=["GET"])
def get_profile():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profile ORDER BY id LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return jsonify({"success": True, "data": dict(row) if row else {}})

@portfolio_bp.route("/profile", methods=["PUT", "POST"])
def update_profile():
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM profile ORDER BY id LIMIT 1")
    existing = cur.fetchone()

    if existing:
        cur.execute(
            """
            UPDATE profile
            SET full_name = ?, headline = ?, email = ?, phone = ?, location = ?,
                github_url = ?, linkedin_url = ?, portfolio_url = ?, summary = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                data.get("full_name", ""),
                data.get("headline", ""),
                data.get("email", ""),
                data.get("phone", ""),
                data.get("location", ""),
                data.get("github_url", ""),
                data.get("linkedin_url", ""),
                data.get("portfolio_url", ""),
                data.get("summary", ""),
                existing["id"],
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO profile (full_name, headline, email, phone, location, github_url, linkedin_url, portfolio_url, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("full_name", ""),
                data.get("headline", ""),
                data.get("email", ""),
                data.get("phone", ""),
                data.get("location", ""),
                data.get("github_url", ""),
                data.get("linkedin_url", ""),
                data.get("portfolio_url", ""),
                data.get("summary", ""),
            ),
        )

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Profile updated successfully."})

# ----------------- Education -----------------
@portfolio_bp.route("/education", methods=["GET"])
def get_education():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM education ORDER BY order_index, start_date DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/education", methods=["POST"])
def add_education():
    data = request.get_json() or {}
    if not data.get("institution") or not data.get("degree"):
        return jsonify({"success": False, "error": "Institution and degree are required."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO education (institution, degree, field_of_study, start_date, end_date, gpa, description, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("institution"),
            data.get("degree"),
            data.get("field_of_study", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
            data.get("gpa", ""),
            data.get("description", ""),
            data.get("order_index", 0),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Education record added."}), 201

@portfolio_bp.route("/education/<int:item_id>", methods=["PUT"])
def update_education(item_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE education
        SET institution = ?, degree = ?, field_of_study = ?, start_date = ?, end_date = ?,
            gpa = ?, description = ?, order_index = ?
        WHERE id = ?
        """,
        (
            data.get("institution"),
            data.get("degree"),
            data.get("field_of_study", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
            data.get("gpa", ""),
            data.get("description", ""),
            data.get("order_index", 0),
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Education updated."})

@portfolio_bp.route("/education/<int:item_id>", methods=["DELETE"])
def delete_education(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM education WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Education deleted."})

# ----------------- Skills -----------------
@portfolio_bp.route("/skills", methods=["GET"])
def get_skills():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM skills ORDER BY category, name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/skills", methods=["POST"])
def add_skill():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("category"):
        return jsonify({"success": False, "error": "Skill name and category are required."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO skills (name, category, proficiency, years_of_experience)
        VALUES (?, ?, ?, ?)
        """,
        (
            data.get("name").strip(),
            data.get("category").strip(),
            data.get("proficiency", "Intermediate"),
            float(data.get("years_of_experience", 1.0)),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Skill added."}), 201

@portfolio_bp.route("/skills/<int:item_id>", methods=["PUT"])
def update_skill(item_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE skills
        SET name = ?, category = ?, proficiency = ?, years_of_experience = ?
        WHERE id = ?
        """,
        (
            data.get("name", "").strip(),
            data.get("category", "").strip(),
            data.get("proficiency", "Intermediate"),
            float(data.get("years_of_experience", 1.0)),
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Skill updated."})

@portfolio_bp.route("/skills/<int:item_id>", methods=["DELETE"])
def delete_skill(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM skills WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Skill deleted."})

# ----------------- Certifications -----------------
@portfolio_bp.route("/certifications", methods=["GET"])
def get_certifications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM certifications ORDER BY issue_date DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/certifications", methods=["POST"])
def add_certification():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("issuing_organization"):
        return jsonify({"success": False, "error": "Certification name and organization are required."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO certifications (name, issuing_organization, issue_date, expiration_date, credential_id, credential_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("issuing_organization"),
            data.get("issue_date", ""),
            data.get("expiration_date", ""),
            data.get("credential_id", ""),
            data.get("credential_url", ""),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Certification added."}), 201

@portfolio_bp.route("/certifications/<int:item_id>", methods=["PUT"])
def update_certification(item_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE certifications
        SET name = ?, issuing_organization = ?, issue_date = ?, expiration_date = ?, credential_id = ?, credential_url = ?
        WHERE id = ?
        """,
        (
            data.get("name"),
            data.get("issuing_organization"),
            data.get("issue_date", ""),
            data.get("expiration_date", ""),
            data.get("credential_id", ""),
            data.get("credential_url", ""),
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Certification updated."})

@portfolio_bp.route("/certifications/<int:item_id>", methods=["DELETE"])
def delete_certification(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM certifications WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Certification deleted."})

# ----------------- Projects -----------------
@portfolio_bp.route("/projects", methods=["GET"])
def get_projects():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY start_date DESC")
    rows = []
    for r in cur.fetchall():
        d = dict(r)
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
        rows.append(d)
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/projects", methods=["POST"])
def add_project():
    data = request.get_json() or {}
    if not data.get("title") or not data.get("description"):
        return jsonify({"success": False, "error": "Project title and description are required."}), 400

    tech_stack = data.get("tech_stack")
    if isinstance(tech_stack, list):
        tech_stack = json.dumps(tech_stack)

    highlights = data.get("highlights")
    if isinstance(highlights, list):
        highlights = json.dumps(highlights)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (title, description, tech_stack, role, highlights, live_url, repo_url, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("title"),
            data.get("description"),
            tech_stack,
            data.get("role", "Developer"),
            highlights,
            data.get("live_url", ""),
            data.get("repo_url", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Project added."}), 201

@portfolio_bp.route("/projects/<int:item_id>", methods=["PUT"])
def update_project(item_id):
    data = request.get_json() or {}
    tech_stack = data.get("tech_stack")
    if isinstance(tech_stack, list):
        tech_stack = json.dumps(tech_stack)

    highlights = data.get("highlights")
    if isinstance(highlights, list):
        highlights = json.dumps(highlights)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects
        SET title = ?, description = ?, tech_stack = ?, role = ?, highlights = ?,
            live_url = ?, repo_url = ?, start_date = ?, end_date = ?
        WHERE id = ?
        """,
        (
            data.get("title"),
            data.get("description"),
            tech_stack,
            data.get("role", "Developer"),
            highlights,
            data.get("live_url", ""),
            data.get("repo_url", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Project updated."})

@portfolio_bp.route("/projects/<int:item_id>", methods=["DELETE"])
def delete_project(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Project deleted."})

# ----------------- Experiences -----------------
@portfolio_bp.route("/experiences", methods=["GET"])
def get_experiences():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM experiences ORDER BY is_current DESC, start_date DESC")
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        if d.get("highlights"):
            try:
                d["highlights_list"] = json.loads(d["highlights"])
            except Exception:
                d["highlights_list"] = [d["highlights"]]
        else:
            d["highlights_list"] = []
        rows.append(d)
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/experiences", methods=["POST"])
def add_experience():
    data = request.get_json() or {}
    if not data.get("company") or not data.get("role"):
        return jsonify({"success": False, "error": "Company and role are required."}), 400

    highlights = data.get("highlights")
    if isinstance(highlights, list):
        highlights = json.dumps(highlights)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO experiences (company, role, location, start_date, end_date, is_current, description, highlights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("company"),
            data.get("role"),
            data.get("location", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
            1 if data.get("is_current") else 0,
            data.get("description", ""),
            highlights,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Experience added."}), 201

@portfolio_bp.route("/experiences/<int:item_id>", methods=["PUT"])
def update_experience(item_id):
    data = request.get_json() or {}
    highlights = data.get("highlights")
    if isinstance(highlights, list):
        highlights = json.dumps(highlights)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE experiences
        SET company = ?, role = ?, location = ?, start_date = ?, end_date = ?,
            is_current = ?, description = ?, highlights = ?
        WHERE id = ?
        """,
        (
            data.get("company"),
            data.get("role"),
            data.get("location", ""),
            data.get("start_date", ""),
            data.get("end_date", ""),
            1 if data.get("is_current") else 0,
            data.get("description", ""),
            highlights,
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Experience updated."})

@portfolio_bp.route("/experiences/<int:item_id>", methods=["DELETE"])
def delete_experience(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM experiences WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Experience deleted."})

# ----------------- Achievements -----------------
@portfolio_bp.route("/achievements", methods=["GET"])
def get_achievements():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM achievements ORDER BY date DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": rows})

@portfolio_bp.route("/achievements", methods=["POST"])
def add_achievement():
    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"success": False, "error": "Achievement title is required."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO achievements (title, type, issuer_or_publisher, date, description, url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("title"),
            data.get("type", "Achievement"),
            data.get("issuer_or_publisher", ""),
            data.get("date", ""),
            data.get("description", ""),
            data.get("url", ""),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Achievement added."}), 201

@portfolio_bp.route("/achievements/<int:item_id>", methods=["PUT"])
def update_achievement(item_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE achievements
        SET title = ?, type = ?, issuer_or_publisher = ?, date = ?, description = ?, url = ?
        WHERE id = ?
        """,
        (
            data.get("title"),
            data.get("type", "Achievement"),
            data.get("issuer_or_publisher", ""),
            data.get("date", ""),
            data.get("description", ""),
            data.get("url", ""),
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Achievement updated."})

@portfolio_bp.route("/achievements/<int:item_id>", methods=["DELETE"])
def delete_achievement(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM achievements WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Achievement deleted."})
