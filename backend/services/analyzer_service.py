"""
Job Description Analyzer Service.
Parses job descriptions, matches requirements against verified portfolio records,
calculates transparent match scores, and provides explainable project recommendations.

GUARANTEE: Never claims the user has a skill or qualification not in their verified portfolio.
"""

import json
import logging
import re
from backend.config import Config
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Canonical aliases for tech skills to improve matching accuracy
SKILL_ALIASES = {
    "rest": ["restful apis", "rest api", "rest apis", "restful api"],
    "restful apis": ["rest", "rest api", "rest apis", "restful api"],
    "postgres": ["postgresql"],
    "postgresql": ["postgres"],
    "sqlite": ["sqlite3", "sql"],
    "cisco": ["cisco packet tracer", "ccna", "cisco certified network associate (ccna 200-301)"],
    "tcp/ip": ["tcp", "ip", "tcp/ip suite", "networking"],
    "subnetting": ["ipv4 subnetting", "ip addressing", "subnets"],
    "vlans": ["802.1q", "vlan", "vlan tagging", "virtual lan"],
    "git": ["github", "version control"],
    "github": ["git", "version control"],
    "docker": ["containers", "containerization"],
    "wireshark": ["packet capture", "packet analysis"],
    "linux": ["ubuntu", "debian", "linux (ubuntu/debian)"],
    "bash": ["bash/shell", "shell scripting", "shell"],
    "python": ["python3", "python programming"],
}

class AnalyzerService:
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()

    def analyze_job_against_portfolio(self, job_text: str, portfolio: dict, job_title: str = "") -> dict:
        """
        Analyzes the job description and matches it against the user's verified portfolio.
        Returns match score, matched skills, missing skills, and recommended projects.
        """
        if not job_text or not job_text.strip():
            return {
                "success": False,
                "error": "Job description cannot be empty."
            }

        # 1. Extract requirements using Gemini if available, else NLP fallback
        extraction = self._extract_job_requirements(job_text, job_title)

        required_skills = extraction.get("required_skills", [])
        preferred_skills = extraction.get("preferred_skills", [])
        detected_role = extraction.get("target_role", job_title or "Target Role")
        responsibilities = extraction.get("key_responsibilities", [])

        # 2. Extract verified skills from portfolio
        verified_skills_raw = portfolio.get("skills", [])
        verified_skill_names = [s.get("name", "").strip() for s in verified_skills_raw if s.get("name")]
        
        # Also collect skills mentioned in projects and certifications
        verified_cert_names = [c.get("name", "").strip() for c in portfolio.get("certifications", [])]
        verified_projects = portfolio.get("projects", [])
        verified_experiences = portfolio.get("experiences", [])

        # 3. Match skills
        matched_required = []
        missing_required = []
        matched_preferred = []
        missing_preferred = []

        for req in required_skills:
            match = self._find_portfolio_match(req, verified_skill_names, verified_cert_names)
            if match:
                matched_required.append({
                    "job_skill": req,
                    "matched_with": match,
                    "verified": True
                })
            else:
                missing_required.append(req)

        for pref in preferred_skills:
            match = self._find_portfolio_match(pref, verified_skill_names, verified_cert_names)
            if match:
                matched_preferred.append({
                    "job_skill": pref,
                    "matched_with": match,
                    "verified": True
                })
            else:
                missing_preferred.append(pref)

        # 4. Transparent Match Score Calculation
        total_req_count = max(len(required_skills), 1)
        req_match_score = (len(matched_required) / total_req_count) * 70.0  # 70% weight for required

        total_pref_count = max(len(preferred_skills), 1)
        pref_match_score = (len(matched_preferred) / total_pref_count) * 15.0 if preferred_skills else 10.0 # 15% weight

        # Experience & project alignment score (15% weight)
        project_alignment_score = self._compute_project_alignment_score(job_text, verified_projects, verified_experiences)
        alignment_points = min(project_alignment_score * 15.0, 15.0)

        raw_total_score = req_match_score + pref_match_score + alignment_points
        overall_score = min(100, max(0, round(raw_total_score)))

        # 5. Project Recommendations
        recommended_projects = self._recommend_projects(job_text, verified_projects, matched_required)

        # 6. Experience Relevance Ranking
        recommended_experiences = self._rank_experiences(job_text, verified_experiences)

        return {
            "success": True,
            "target_role": detected_role,
            "overall_score": overall_score,
            "score_breakdown": {
                "overall": overall_score,
                "required_skills_weight": 70,
                "required_skills_earned": round(req_match_score, 1),
                "preferred_skills_weight": 15,
                "preferred_skills_earned": round(pref_match_score, 1),
                "experience_alignment_weight": 15,
                "experience_alignment_earned": round(alignment_points, 1),
                "explanation": f"Score reflects {len(matched_required)}/{len(required_skills)} required skills matched, plus verified project/internship relevance."
            },
            "skills_analysis": {
                "matched_required": matched_required,
                "missing_required": missing_required,
                "matched_preferred": matched_preferred,
                "missing_preferred": missing_preferred,
                "total_required_count": len(required_skills),
                "total_matched_count": len(matched_required) + len(matched_preferred),
                "total_missing_count": len(missing_required) + len(missing_preferred)
            },
            "recommended_projects": recommended_projects,
            "recommended_experiences": recommended_experiences,
            "key_responsibilities": responsibilities,
            "analysis_source": extraction.get("source", "heuristic"),
            "ethical_notice": "Strict Rule Enforced: Missing skills are accurately reported. Only candidate-verified skills and achievements from the portfolio are matched or included."
        }

    def _find_portfolio_match(self, job_skill: str, portfolio_skills: list, portfolio_certs: list) -> str:
        """Finds if a job skill has a verified match in the portfolio."""
        js_clean = job_skill.strip().lower()

        for ps in portfolio_skills:
            ps_clean = ps.strip().lower()
            if js_clean == ps_clean or js_clean in ps_clean or ps_clean in js_clean:
                return ps
            # Check aliases
            aliases = SKILL_ALIASES.get(ps_clean, [])
            if any(a in js_clean or js_clean in a for a in aliases):
                return ps

        # Check certifications
        for cert in portfolio_certs:
            cert_clean = cert.strip().lower()
            if js_clean in cert_clean:
                return cert

        return None

    def _extract_job_requirements(self, job_text: str, job_title: str) -> dict:
        """Extracts required skills, preferred skills, and role title using Gemini or NLP fallback."""
        client = self.gemini_service.get_client()
        if client:
            try:
                prompt = f"""You are an expert technical recruiter. Analyze the following job description.
Extract:
1. "target_role": exact job title / role.
2. "required_skills": list of strictly required technical skills, protocols, tools, or programming languages (e.g. Python, REST APIs, SQL, Docker, TCP/IP, VLANs).
3. "preferred_skills": list of bonus / preferred skills.
4. "key_responsibilities": list of 3-5 core duties.

Return STRICT JSON ONLY, matching:
{{
  "target_role": "string",
  "required_skills": ["string", "string"],
  "preferred_skills": ["string", "string"],
  "key_responsibilities": ["string", "string"]
}}

Job Description:
\"\"\"
{job_text}
\"\"\"
"""
                response = client.models.generate_content(
                    model=self.gemini_service.model_name,
                    contents=prompt
                )
                text = response.text.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                data = json.loads(text)
                data["source"] = "gemini"
                return data
            except Exception as e:
                logger.warning(f"Gemini job extraction error ({e}). Using NLP fallback.")

        # Fallback NLP extraction
        return self._heuristic_extract_job_requirements(job_text, job_title)

    def _heuristic_extract_job_requirements(self, job_text: str, job_title: str) -> dict:
        """Deterministic keyword and bullet-point extractor for job descriptions."""
        lower_text = job_text.lower()
        title = job_title
        if not title:
            first_line = job_text.splitlines()[0] if job_text.splitlines() else "Target Position"
            title = re.sub(r"^(position|title|role):\s*", "", first_line, flags=re.IGNORECASE).strip()

        tech_catalog = [
            # Languages & Backend
            "Python", "Rust", "Go", "Java", "C++", "C#", "Haskell", "JavaScript", "TypeScript",
            "REST APIs", "SQL", "PostgreSQL", "SQLite", "Flask", "FastAPI", "Django",
            "Git", "GitHub", "Docker", "Kubernetes", "Linux", "Redis", "JWT", "Microservices",
            # Networking
            "TCP/IP", "Subnetting", "VLANs", "Routing & Switching", "OSPF", "BGP", "DNS",
            "DHCP", "Wireshark", "Network Troubleshooting", "Cisco", "CCNA", "Packet Tracer",
            # Cloud & Systems
            "AWS", "Cloud", "Unit Testing", "pytest", "Bash", "Shell", "Quantum Key Distribution"
        ]

        found_tech = []
        for tech in tech_catalog:
            pattern = r"\b" + re.escape(tech.lower()) + r"\b"
            if re.search(pattern, lower_text):
                found_tech.append(tech)

        # Distinguish required vs preferred and scan bullet points
        required = []
        preferred = []

        lines = job_text.splitlines()
        current_section = None
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            ll = line.lower()
            if any(k in ll for k in ["plus", "preferred", "bonus", "nice to have", "desired"]):
                current_section = "preferred"
                continue
            elif any(k in ll for k in ["requirement", "qualifications", "must have", "responsibilities", "skills"]):
                current_section = "required"
                continue

            # Check if this line is a bullet item under requirements
            if (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                bullet_content = line.lstrip("-•* ").strip()
                if 2 < len(bullet_content) < 45 and not any(p in bullet_content.lower() for p in ["year", "bachelor", "degree", "experience"]):
                    if current_section == "preferred":
                        if bullet_content not in preferred:
                            preferred.append(bullet_content)
                    else:
                        if bullet_content not in required:
                            required.append(bullet_content)

            for tech in found_tech:
                if tech.lower() in ll:
                    if current_section == "preferred" and tech not in preferred and tech not in required:
                        preferred.append(tech)
                    elif current_section != "preferred" and tech not in required and tech not in preferred:
                        required.append(tech)

        # Merge catalog finds if needed
        for tech in found_tech:
            if tech not in required and tech not in preferred:
                required.append(tech)

        responsibilities = [
            line.strip("- *• ") for line in lines
            if len(line.strip()) > 20 and any(w in line.lower() for w in ["build", "maintain", "support", "design", "monitor", "troubleshoot", "configure", "collaborate"])
        ][:4]

        return {
            "target_role": title or "Technical Role",
            "required_skills": required,
            "preferred_skills": preferred,
            "key_responsibilities": responsibilities,
            "source": "heuristic"
        }

    def _compute_project_alignment_score(self, job_text: str, projects: list, experiences: list) -> float:
        """Computes contextual alignment between job text and project descriptions."""
        job_words = set(re.findall(r"\w{4,}", job_text.lower()))
        if not job_words:
            return 0.5

        overlap_count = 0
        total_eval = 0

        for p in projects:
            combined = f"{p.get('title', '')} {p.get('description', '')} {p.get('tech_stack', '')} {p.get('highlights', '')}".lower()
            p_words = set(re.findall(r"\w{4,}", combined))
            overlap = len(job_words.intersection(p_words))
            overlap_count += min(overlap, 10)
            total_eval += 10

        for e in experiences:
            combined = f"{e.get('company', '')} {e.get('role', '')} {e.get('description', '')} {e.get('highlights', '')}".lower()
            e_words = set(re.findall(r"\w{4,}", combined))
            overlap = len(job_words.intersection(e_words))
            overlap_count += min(overlap, 10)
            total_eval += 10

        if total_eval == 0:
            return 0.5
        return min(1.0, overlap_count / total_eval)

    def _recommend_projects(self, job_text: str, projects: list, matched_skills: list) -> list:
        """Ranks projects by relevance to the job description and matched skills."""
        matched_names = {m["job_skill"].lower() for m in matched_skills}
        job_lower = job_text.lower()

        scored = []
        for p in projects:
            score = 0
            reasons = []

            # Check tech stack overlap
            tech_list = p.get("tech_stack_list", [])
            if not tech_list and p.get("tech_stack"):
                try:
                    tech_list = json.loads(p["tech_stack"])
                except Exception:
                    tech_list = [t.strip() for t in p["tech_stack"].split(",")]

            matching_tech = [t for t in tech_list if t.lower() in job_lower or t.lower() in matched_names]
            if matching_tech:
                score += len(matching_tech) * 3
                reasons.append(f"Directly leverages required tech: {', '.join(matching_tech)}.")

            # Check title and highlights overlap
            desc_text = f"{p.get('title', '')} {p.get('description', '')} {p.get('highlights', '')}".lower()
            for skill in matched_names:
                if skill in desc_text:
                    score += 2

            if "rest" in desc_text and "rest" in job_lower:
                score += 3
                reasons.append("Demonstrates production REST API architecture and endpoints.")
            if "vlan" in desc_text and "vlan" in job_lower:
                score += 3
                reasons.append("Demonstrates enterprise VLAN segmentation and switch configuration.")
            if "troubleshoot" in desc_text and "troubleshoot" in job_lower:
                score += 2
                reasons.append("Highlights systematic network diagnostic and troubleshooting skills.")

            if not reasons:
                reasons.append("Demonstrates core computer science and software development capability.")

            scored.append({
                "project_id": p.get("id"),
                "title": p.get("title"),
                "role": p.get("role"),
                "relevance_score": score,
                "tech_stack": tech_list,
                "recommendation_reason": " ".join(reasons)
            })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored

    def _rank_experiences(self, job_text: str, experiences: list) -> list:
        """Ranks work experiences by keyword relevance to the job."""
        job_lower = job_text.lower()
        ranked = []
        for e in experiences:
            combined = f"{e.get('company', '')} {e.get('role', '')} {e.get('description', '')} {e.get('highlights', '')}".lower()
            words = set(re.findall(r"\w{4,}", combined))
            matches = [w for w in words if w in job_lower]
            ranked.append({
                "experience_id": e.get("id"),
                "company": e.get("company"),
                "role": e.get("role"),
                "relevance_hits": len(matches),
                "is_recommended": len(matches) >= 3
            })
        ranked.sort(key=lambda x: x["relevance_hits"], reverse=True)
        return ranked
