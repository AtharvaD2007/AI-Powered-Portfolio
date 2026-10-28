"""
Google Sheets Integration Routes.
Status check, test connection, and export portfolio tabs.
"""

from flask import Blueprint, request, jsonify
from backend.database import get_full_portfolio, get_db_connection
from backend.services.sheets_service import GoogleSheetsService

sheets_bp = Blueprint("sheets", __name__, url_prefix="/api/sheets")
sheets_service = GoogleSheetsService()

@sheets_bp.route("/status", methods=["GET"])
def get_sheets_status():
    """Returns configuration and connection status for Google Sheets."""
    status = sheets_service.get_status()
    # Check last sync log in SQLite
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sync_logs WHERE service = 'google_sheets' ORDER BY timestamp DESC LIMIT 1")
    last_sync = cur.fetchone()
    conn.close()

    status["last_sync"] = dict(last_sync) if last_sync else None
    return jsonify({"success": True, "status": status})

@sheets_bp.route("/test", methods=["POST"])
def test_sheets_connection():
    """Tests connection to Google Sheets."""
    result = sheets_service.test_connection()
    return jsonify(result)

@sheets_bp.route("/export", methods=["POST"])
def export_portfolio():
    """Exports portfolio to Google Sheets (or returns dry-run preview if credentials missing)."""
    portfolio = get_full_portfolio()
    result = sheets_service.export_portfolio(portfolio)

    # Log sync event in SQLite
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sync_logs (service, status, message, synced_records_count)
        VALUES ('google_sheets', ?, ?, ?)
        """,
        (
            "success" if result.get("success") else "failed",
            result.get("message", result.get("error", "Unknown sync result")),
            len(result.get("synced_tabs", [])),
        )
    )
    conn.commit()
    conn.close()

    return jsonify(result)
