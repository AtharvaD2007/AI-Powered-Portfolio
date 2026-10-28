"""
Settings and Environment Diagnostic Routes.
Checks configuration status, updates keys dynamically, and exposes health status.
"""

import os
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.services.gemini_service import GeminiService
from backend.services.sheets_service import GoogleSheetsService

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

@settings_bp.route("/status", methods=["GET"])
def get_settings_status():
    """Returns status of external credentials and models without revealing secrets."""
    gemini_key = Config.GEMINI_API_KEY
    masked_gemini_key = f"{gemini_key[:4]}...{gemini_key[-4:]}" if gemini_key and len(gemini_key) > 8 else ("Configured" if gemini_key else "Not Set")

    sheets_service = GoogleSheetsService()
    sheets_status = sheets_service.get_status()

    return jsonify({
        "success": True,
        "gemini": {
            "configured": Config.is_gemini_configured(),
            "model": Config.GEMINI_MODEL,
            "masked_key": masked_gemini_key,
            "status_message": "Ready" if Config.is_gemini_configured() else "Missing GEMINI_API_KEY. Built-in heuristic parser active."
        },
        "google_sheets": sheets_status,
        "database": {
            "path": Config.DATABASE_PATH,
            "engine": "SQLite"
        }
    })

@settings_bp.route("/update", methods=["POST"])
def update_settings():
    """Allows setting GEMINI_API_KEY or GOOGLE_SHEET_ID dynamically for runtime usage."""
    data = request.get_json() or {}
    
    if "gemini_api_key" in data and data["gemini_api_key"].strip():
        Config.GEMINI_API_KEY = data["gemini_api_key"].strip()
        os.environ["GEMINI_API_KEY"] = data["gemini_api_key"].strip()

    if "gemini_model" in data and data["gemini_model"].strip():
        Config.GEMINI_MODEL = data["gemini_model"].strip()
        os.environ["GEMINI_MODEL"] = data["gemini_model"].strip()

    if "google_sheet_id" in data and data["google_sheet_id"].strip():
        Config.GOOGLE_SHEET_ID = data["google_sheet_id"].strip()
        os.environ["GOOGLE_SHEET_ID"] = data["google_sheet_id"].strip()

    return jsonify({
        "success": True,
        "message": "Settings updated for current session."
    })
