"""
Google Sheets Integration Service.
Exports portfolio data into separate tabs: Profile, Education, Skills,
Certifications, Projects, Experience, and Achievements.
Uses Google Service Account credentials from environment variables.
"""

import json
import logging
import os
from datetime import datetime
from backend.config import Config

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.credentials_json = Config.GOOGLE_SHEETS_CREDENTIALS_JSON
        self.app_credentials = Config.GOOGLE_APPLICATION_CREDENTIALS
        self._client = None

    def get_status(self) -> dict:
        """Returns the connection and configuration status of Google Sheets."""
        has_creds = Config.is_google_sheets_configured()
        has_sheet_id = bool(self.sheet_id and len(self.sheet_id.strip()) > 5)

        service_account_email = "Not Configured"
        if has_creds:
            try:
                if self.credentials_json and os.path.exists(self.credentials_json):
                    with open(self.credentials_json, "r") as f:
                        data = json.load(f)
                        service_account_email = data.get("client_email", "Found in file")
                elif self.credentials_json:
                    data = json.loads(self.credentials_json)
                    service_account_email = data.get("client_email", "Configured via JSON string")
                elif self.app_credentials and os.path.exists(self.app_credentials):
                    with open(self.app_credentials, "r") as f:
                        data = json.load(f)
                        service_account_email = data.get("client_email", "Found in GOOGLE_APPLICATION_CREDENTIALS")
            except Exception:
                service_account_email = "Configured (Unable to parse client email)"

        sheet_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit" if has_sheet_id else ""

        return {
            "configured": has_creds and has_sheet_id,
            "has_credentials": has_creds,
            "has_sheet_id": has_sheet_id,
            "service_account_email": service_account_email,
            "sheet_id": self.sheet_id,
            "sheet_url": sheet_url,
            "setup_instructions": {
                "step1": "Create a Google Cloud Project with the Google Sheets API and Google Drive API enabled.",
                "step2": "Create a Service Account, generate a JSON Key, and save it.",
                "step3": "Share your target Google Sheet with your service account email (Editor permissions).",
                "step4": "Add GOOGLE_SHEETS_CREDENTIALS_JSON and GOOGLE_SHEET_ID in backend/.env."
            }
        }

    def _get_gspread_client(self):
        """Initializes and returns an authenticated gspread client."""
        if self._client:
            return self._client

        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        if self.credentials_json:
            if os.path.exists(self.credentials_json):
                creds = Credentials.from_service_account_file(self.credentials_json, scopes=scopes)
            else:
                data = json.loads(self.credentials_json)
                creds = Credentials.from_service_account_info(data, scopes=scopes)
        elif self.app_credentials and os.path.exists(self.app_credentials):
            creds = Credentials.from_service_account_file(self.app_credentials, scopes=scopes)
        else:
            raise ValueError("No valid Google Service Account credentials found.")

        self._client = gspread.authorize(creds)
        return self._client

    def test_connection(self) -> dict:
        """Tests live access to the configured Google Sheet."""
        status = self.get_status()
        if not status["configured"]:
            return {
                "success": False,
                "error": "Google Sheets is not fully configured. Missing credentials or GOOGLE_SHEET_ID.",
                "status": status
            }

        try:
            client = self._get_gspread_client()
            sheet = client.open_by_key(self.sheet_id)
            return {
                "success": True,
                "message": f"Successfully connected to Google Sheet '{sheet.title}'!",
                "sheet_title": sheet.title,
                "sheet_id": self.sheet_id,
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit",
                "worksheets": [w.title for w in sheet.worksheets()]
            }
        except Exception as e:
            logger.error(f"Google Sheets test connection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Ensure the service account has been added as an 'Editor' to the Google Sheet."
            }

    def export_portfolio(self, portfolio: dict) -> dict:
        """
        Exports all portfolio sections into separate tabs:
        Profile, Education, Skills, Certifications, Projects, Experience, Achievements.
        """
        if not Config.is_google_sheets_configured() or not self.sheet_id:
            # Return dry-run / formatted preview data so the user can inspect what gets exported
            preview_data = self._generate_export_tables(portfolio)
            return {
                "success": False,
                "is_dry_run": True,
                "message": "Google Sheets API credentials are not yet configured. Here is the formatted export payload ready for sync.",
                "tabs": list(preview_data.keys()),
                "preview": preview_data,
                "status": self.get_status()
            }

        try:
            client = self._get_gspread_client()
            spreadsheet = client.open_by_key(self.sheet_id)
            export_data = self._generate_export_tables(portfolio)

            synced_tabs = []
            for tab_name, rows in export_data.items():
                try:
                    worksheet = spreadsheet.worksheet(tab_name)
                    worksheet.clear()
                except Exception:
                    # Tab does not exist yet; create it
                    worksheet = spreadsheet.add_worksheet(title=tab_name, rows=max(len(rows) + 5, 20), cols=12)

                if rows:
                    worksheet.update(values=rows)
                    # Format header row
                    try:
                        worksheet.format("A1:Z1", {
                            "textFormat": {"bold": True},
                            "backgroundColor": {"red": 0.9, "green": 0.94, "blue": 0.98}
                        })
                    except Exception:
                        pass
                synced_tabs.append(tab_name)

            return {
                "success": True,
                "synced_tabs": synced_tabs,
                "synced_at": datetime.now().isoformat(),
                "sheet_id": self.sheet_id,
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit",
                "message": f"Successfully exported {len(synced_tabs)} portfolio tabs to Google Sheets."
            }
        except Exception as e:
            logger.error(f"Google Sheets export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Export failed. Please check permissions and service account credentials."
            }

    def _generate_export_tables(self, portfolio: dict) -> dict:
        """Formats the portfolio dictionary into 2D tables suitable for spreadsheet cells."""
        tables = {}

        # 1. Profile Tab
        prof = portfolio.get("profile", {})
        profile_rows = [
            ["Attribute", "Value"],
            ["Full Name", prof.get("full_name", "")],
            ["Headline", prof.get("headline", "")],
            ["Email", prof.get("email", "")],
            ["Phone", prof.get("phone", "")],
            ["Location", prof.get("location", "")],
            ["GitHub URL", prof.get("github_url", "")],
            ["LinkedIn URL", prof.get("linkedin_url", "")],
            ["Portfolio URL", prof.get("portfolio_url", "")],
            ["Professional Summary", prof.get("summary", "")],
            ["Export Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        tables["Profile"] = profile_rows

        # 2. Education Tab
        edu_rows = [["Institution", "Degree", "Field of Study", "Start Date", "End Date", "GPA", "Description"]]
        for edu in portfolio.get("education", []):
            edu_rows.append([
                edu.get("institution", ""),
                edu.get("degree", ""),
                edu.get("field_of_study", ""),
                edu.get("start_date", ""),
                edu.get("end_date", ""),
                edu.get("gpa", ""),
                edu.get("description", "")
            ])
        tables["Education"] = edu_rows

        # 3. Skills Tab
        skills_rows = [["Skill Name", "Category", "Proficiency", "Years of Experience"]]
        for sk in portfolio.get("skills", []):
            skills_rows.append([
                sk.get("name", ""),
                sk.get("category", ""),
                sk.get("proficiency", ""),
                str(sk.get("years_of_experience", 1.0))
            ])
        tables["Skills"] = skills_rows

        # 4. Certifications Tab
        cert_rows = [["Certification Name", "Issuing Organization", "Issue Date", "Expiration Date", "Credential ID", "Verification URL"]]
        for c in portfolio.get("certifications", []):
            cert_rows.append([
                c.get("name", ""),
                c.get("issuing_organization", ""),
                c.get("issue_date", ""),
                c.get("expiration_date", ""),
                c.get("credential_id", ""),
                c.get("credential_url", "")
            ])
        tables["Certifications"] = cert_rows

        # 5. Projects Tab
        proj_rows = [["Project Title", "Role", "Tech Stack", "Live URL", "Repository URL", "Start Date", "End Date", "Description", "Highlights"]]
        for p in portfolio.get("projects", []):
            tech = p.get("tech_stack", "")
            if isinstance(tech, list):
                tech = ", ".join(tech)
            highlights = p.get("highlights", "")
            if isinstance(highlights, list):
                highlights = " | ".join(highlights)
            proj_rows.append([
                p.get("title", ""),
                p.get("role", ""),
                tech,
                p.get("live_url", ""),
                p.get("repo_url", ""),
                p.get("start_date", ""),
                p.get("end_date", ""),
                p.get("description", ""),
                highlights
            ])
        tables["Projects"] = proj_rows

        # 6. Experience Tab
        exp_rows = [["Company", "Role", "Location", "Start Date", "End Date", "Current", "Description", "Highlights"]]
        for e in portfolio.get("experiences", []):
            highlights = e.get("highlights", "")
            if isinstance(highlights, list):
                highlights = " | ".join(highlights)
            exp_rows.append([
                e.get("company", ""),
                e.get("role", ""),
                e.get("location", ""),
                e.get("start_date", ""),
                e.get("end_date", ""),
                "Yes" if e.get("is_current") else "No",
                e.get("description", ""),
                highlights
            ])
        tables["Experience"] = exp_rows

        # 7. Achievements Tab
        ach_rows = [["Title", "Type", "Issuer / Publisher", "Date", "Description", "URL"]]
        for a in portfolio.get("achievements", []):
            ach_rows.append([
                a.get("title", ""),
                a.get("type", ""),
                a.get("issuer_or_publisher", ""),
                a.get("date", ""),
                a.get("description", ""),
                a.get("url", "")
            ])
        tables["Achievements"] = ach_rows

        return tables
