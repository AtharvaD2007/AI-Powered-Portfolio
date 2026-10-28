"""
Gemini AI Service integration using the official google-genai SDK.
Provides fallback mechanisms when external API credentials are not provided or unavailable.
"""

import json
import logging
import re
from backend.config import Config

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None

    def get_client(self):
        if not self.api_key:
            return None
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")
                self._client = None
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def parse_unstructured_portfolio(self, raw_text: str) -> dict:
        """
        Parses unstructured user input into structured portfolio entities.
        Returns a dict containing proposed updates/additions for:
        profile, education, skills, certifications, projects, experiences, achievements.
        """
        if not raw_text or not raw_text.strip():
            return {
                "success": False,
                "error": "Input text is empty",
                "data": None,
                "source": "validation"
            }

        client = self.get_client()
        if client:
            try:
                prompt = f"""You are an expert AI Portfolio Organizer.
Analyze the following unstructured user information and organize it into the correct portfolio categories.
Strictly return a valid JSON object with the following schema:

{{
  "profile": {{
    "full_name": "string or empty",
    "headline": "string or empty",
    "email": "string or empty",
    "phone": "string or empty",
    "location": "string or empty",
    "github_url": "string or empty",
    "linkedin_url": "string or empty",
    "portfolio_url": "string or empty",
    "summary": "concise professional summary or empty"
  }},
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string",
      "start_date": "YYYY or YYYY-MM",
      "end_date": "YYYY or YYYY-MM or Expected YYYY",
      "gpa": "string or empty",
      "description": "string or empty"
    }}
  ],
  "skills": [
    {{
      "name": "string (e.g. Python, Docker, TCP/IP)",
      "category": "Languages | Backend & APIs | Databases | Networking & Protocols | DevOps & Tools | Soft Skills",
      "proficiency": "Beginner | Intermediate | Advanced | Expert"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuing_organization": "string",
      "issue_date": "YYYY or YYYY-MM",
      "expiration_date": "YYYY or empty",
      "credential_id": "string or empty",
      "credential_url": "string or empty"
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "description": "string",
      "tech_stack": ["string", "string"],
      "role": "string or empty",
      "highlights": ["bullet point 1", "bullet point 2"],
      "live_url": "string or empty",
      "repo_url": "string or empty",
      "start_date": "YYYY-MM or empty",
      "end_date": "YYYY-MM or empty"
    }}
  ],
  "experiences": [
    {{
      "company": "string",
      "role": "string",
      "location": "string or empty",
      "start_date": "YYYY-MM or empty",
      "end_date": "YYYY-MM or empty",
      "is_current": false,
      "description": "string",
      "highlights": ["achievement or responsibility 1", "bullet point 2"]
    }}
  ],
  "achievements": [
    {{
      "title": "string",
      "type": "Achievement | Publication | Award | Honor",
      "issuer_or_publisher": "string or empty",
      "date": "YYYY or YYYY-MM",
      "description": "string",
      "url": "string or empty"
    }}
  ]
}}

Rules:
1. Preserve all factual user information faithfully. Do not invent false dates, employers, or institutions.
2. Only populate fields for which there is evident information in the input. If a category has no items in the input, return an empty array [] or empty object.
3. Return ONLY valid JSON, with no markdown code fences or conversational text.

User Input:
\"\"\"
{raw_text}
\"\"\"
"""
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                raw_content = response.text.strip()
                # Remove markdown fences if model returned them
                if raw_content.startswith("```"):
                    raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
                    raw_content = re.sub(r"\s*```$", "", raw_content)
                parsed_json = json.loads(raw_content)
                return {
                    "success": True,
                    "data": parsed_json,
                    "source": "gemini",
                    "model": self.model_name
                }
            except Exception as e:
                logger.warning(f"Gemini API call failed ({e}). Falling back to heuristic organizer.")
                fallback_result = self._heuristic_parse_portfolio(raw_text)
                fallback_result["warning"] = f"Gemini API was unavailable ({str(e)}). Used local heuristic parser."
                return fallback_result

        # Fallback when no API key is provided
        fallback_result = self._heuristic_parse_portfolio(raw_text)
        fallback_result["warning"] = "Gemini API key is not configured. Results organized using built-in heuristic pattern extractor. Configure GEMINI_API_KEY in Settings for AI enhancement."
        return fallback_result

    def _heuristic_parse_portfolio(self, raw_text: str) -> dict:
        """
        Smart deterministic fallback parser when Gemini is unavailable.
        Extracts contact emails, phone, URLs, skills, certifications, and projects.
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        # Email & URLs regex
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)
        github_match = re.search(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_\-]+", raw_text, re.IGNORECASE)
        linkedin_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+", raw_text, re.IGNORECASE)
        url_match = re.search(r"https?://[^\s<>\"']+", raw_text)

        profile = {
            "full_name": lines[0] if lines and not lines[0].startswith("http") and not "@" in lines[0] else "",
            "headline": "",
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "location": "",
            "github_url": github_match.group(0) if github_match else "",
            "linkedin_url": linkedin_match.group(0) if linkedin_match else "",
            "portfolio_url": url_match.group(0) if url_match and url_match.group(0) != (github_match and github_match.group(0)) else "",
            "summary": ""
        }

        # Known skill dictionary for heuristic extraction
        known_skills = [
            ("Python", "Languages"), ("JavaScript", "Languages"), ("TypeScript", "Languages"),
            ("SQL", "Languages"), ("C++", "Languages"), ("Java", "Languages"), ("Go", "Languages"),
            ("Bash", "Languages"), ("Flask", "Backend & APIs"), ("Django", "Backend & APIs"),
            ("FastAPI", "Backend & APIs"), ("REST", "Backend & APIs"), ("GraphQL", "Backend & APIs"),
            ("PostgreSQL", "Databases"), ("SQLite", "Databases"), ("MySQL", "Databases"),
            ("MongoDB", "Databases"), ("Redis", "Databases"), ("Docker", "DevOps & Tools"),
            ("Kubernetes", "DevOps & Tools"), ("Git", "DevOps & Tools"), ("GitHub", "DevOps & Tools"),
            ("Linux", "DevOps & Tools"), ("TCP/IP", "Networking & Protocols"),
            ("VLANs", "Networking & Protocols"), ("Subnetting", "Networking & Protocols"),
            ("OSPF", "Networking & Protocols"), ("BGP", "Networking & Protocols"),
            ("Wireshark", "Networking & Protocols"), ("DNS", "Networking & Protocols"),
            ("DHCP", "Networking & Protocols"), ("AWS", "DevOps & Tools"), ("Azure", "DevOps & Tools")
        ]

        found_skills = []
        lower_raw = raw_text.lower()
        for skill_name, category in known_skills:
            pattern = r"\b" + re.escape(skill_name.lower()) + r"\b"
            if re.search(pattern, lower_raw):
                found_skills.append({
                    "name": skill_name,
                    "category": category,
                    "proficiency": "Intermediate"
                })

        # Heuristic Project/Experience detection
        projects = []
        experiences = []
        certifications = []
        education = []

        current_section = None
        for line in lines:
            llow = line.lower()
            if any(k in llow for k in ["project", "projects:"]):
                current_section = "projects"
                continue
            elif any(k in llow for k in ["experience", "employment", "internship"]):
                current_section = "experience"
                continue
            elif any(k in llow for k in ["education", "degree", "university", "college"]):
                current_section = "education"
                continue
            elif any(k in llow for k in ["certif", "license", "ccna", "pcap", "aws cert"]):
                current_section = "certification"
                continue

            if current_section == "projects" and len(line) > 10:
                projects.append({
                    "title": line.split(":")[0].strip("- *•"),
                    "description": line,
                    "tech_stack": [s["name"] for s in found_skills if s["name"].lower() in line.lower()][:4],
                    "role": "Developer",
                    "highlights": [line],
                    "live_url": "",
                    "repo_url": "",
                    "start_date": "",
                    "end_date": ""
                })
            elif current_section == "experience" and len(line) > 10:
                experiences.append({
                    "company": line.split("-")[0].strip("- *•"),
                    "role": "Team Member",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "is_current": False,
                    "description": line,
                    "highlights": [line]
                })
            elif current_section == "certification" and len(line) > 5:
                certifications.append({
                    "name": line.strip("- *•"),
                    "issuing_organization": "Accredited Provider",
                    "issue_date": "",
                    "expiration_date": "",
                    "credential_id": "",
                    "credential_url": ""
                })
            elif current_section == "education" and any(k in llow for k in ["university", "college", "bachelor", "master", "bs", "ba", "degree"]):
                education.append({
                    "institution": line.strip("- *•"),
                    "degree": "Degree",
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": "",
                    "gpa": "",
                    "description": line
                })

        return {
            "success": True,
            "data": {
                "profile": profile,
                "education": education,
                "skills": found_skills,
                "certifications": certifications,
                "projects": projects[:5],
                "experiences": experiences[:5],
                "achievements": []
            },
            "source": "heuristic"
        }

    def generate_tailored_summary(self, target_role: str, job_description: str, verified_profile: dict, verified_skills: list, verified_projects: list) -> str:
        """
        Generates an ATS-tailored professional summary for the resume.
        CRITICAL CONSTRAINT: Uses ONLY verified portfolio details.
        Never hallucinates skills or credentials.
        """
        client = self.get_client()
        skills_str = ", ".join([s.get("name", "") for s in verified_skills[:12]])
        project_titles = ", ".join([p.get("title", "") for p in verified_projects[:3]])

        if client:
            try:
                prompt = f"""You are an executive resume writer. Write a concise, impactful 2-3 sentence professional summary for a candidate applying for the target role: "{target_role}".

STRICT ETHICAL RULE:
You MUST ONLY reference skills, credentials, and projects explicitly verified in the candidate's portfolio below.
NEVER claim or imply skills, experience, degrees, or certifications that are not present.

Target Role: {target_role}
Job Context: {job_description[:400]}

Candidate Verified Information:
- Current Headline: {verified_profile.get('headline', '')}
- Verified Skills: {skills_str}
- Verified Projects: {project_titles}
- Existing Summary: {verified_profile.get('summary', '')}

Output only the 2-3 sentence summary text, with no preamble or quotes.
"""
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return response.text.strip().strip('"')
            except Exception as e:
                logger.warning(f"Gemini summary generation failed: {e}. Using deterministic fallback.")

        # High-quality deterministic summary fallback
        headline = verified_profile.get("headline", "Motivated professional")
        base_summary = verified_profile.get("summary", "")
        if base_summary:
            return f"Results-driven {target_role} with strong hands-on background in {skills_str}. {base_summary}"
        return f"Target-oriented {target_role} specializing in {skills_str}. Dedicated to applying verified engineering and analytical practices to deliver scalable, reliable infrastructure and software solutions."
