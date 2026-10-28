"""
Flask Application Entry Point.
Initializes database, registers blueprints, configures CORS, and exposes REST APIs.
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

# Add root folder to sys.path so backend modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import Config
from backend.database import init_db
from backend.routes.portfolio_routes import portfolio_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.analyzer_routes import analyzer_bp
from backend.routes.resume_routes import resume_bp
from backend.routes.sheets_routes import sheets_bp
from backend.routes.settings_routes import settings_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend Vite dev server (typically port 5173 or 3000)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Database Schema & Sample Data
    with app.app_context():
        init_db()

    # Register Blueprints
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(settings_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "database": "SQLite",
            "gemini_configured": Config.is_gemini_configured(),
            "sheets_configured": Config.is_google_sheets_configured(),
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 AI Portfolio & Resume Generator API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
