"""
ReportLab ATS-Friendly Resume PDF Generator Service.
Produces cleanly formatted, machine-readable, ATS-optimized PDFs.
Uses single-column semantic flowables, standard fonts (Helvetica),
high-contrast hierarchy, and cleanly delineated sections.
"""

import io
import json
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

logger = logging.getLogger(__name__)

class ResumePDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        # Base colors
        self.primary_color = colors.HexColor("#1A202C")     # Dark Slate / Charcoal for ATS readability
        self.secondary_color = colors.HexColor("#2B6CB0")   # Professional navy blue accent
        self.neutral_dark = colors.HexColor("#2D3748")
        self.neutral_muted = colors.HexColor("#4A5568")
        self.line_color = colors.HexColor("#CBD5E0")

        # Name / Header Style
        self.styles.add(ParagraphStyle(
            name="ResumeName",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=self.primary_color,
            alignment=1, # Centered
            spaceAfter=2,
        ))

        # Subtitle / Headline
        self.styles.add(ParagraphStyle(
            name="ResumeHeadline",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=self.secondary_color,
            alignment=1,
            spaceAfter=4,
        ))

        # Contact Info Bar
        self.styles.add(ParagraphStyle(
            name="ResumeContact",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=self.neutral_muted,
            alignment=1,
            spaceAfter=8,
        ))

        # Section Header Style
        self.styles.add(ParagraphStyle(
            name="ResumeSectionHeader",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=self.secondary_color,
            spaceBefore=6,
            spaceAfter=2,
            textTransform="uppercase",
            keepWithNext=True,
        ))

        # Item Title (Company, Project, Institution)
        self.styles.add(ParagraphStyle(
            name="ItemTitleLeft",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=self.primary_color,
        ))

        # Item Right (Date / Location)
        self.styles.add(ParagraphStyle(
            name="ItemTitleRight",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=self.neutral_muted,
            alignment=2, # Right-aligned
        ))

        # Item Subtitle (Role, Degree, Tech Stack)
        self.styles.add(ParagraphStyle(
            name="ItemSubtitleLeft",
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=11.5,
            textColor=self.neutral_dark,
        ))

        # Item Subtitle Right (Location)
        self.styles.add(ParagraphStyle(
            name="ItemSubtitleRight",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=self.neutral_muted,
            alignment=2,
        ))

        # Body text / Summary
        self.styles.add(ParagraphStyle(
            name="ResumeBody",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=self.neutral_dark,
            spaceAfter=4,
        ))

        # Bullet point text
        self.styles.add(ParagraphStyle(
            name="ResumeBullet",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=self.neutral_dark,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=1.5,
        ))

        # Skill category bold label
        self.styles.add(ParagraphStyle(
            name="SkillCategoryLabel",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11.5,
            textColor=self.primary_color,
        ))

    def _section_heading(self, title: str):
        """Creates an ATS-standard section header with an underline."""
        return [
            Paragraph(title, self.styles["ResumeSectionHeader"]),
            HRFlowable(
                width="100%",
                thickness=0.75,
                color=self.line_color,
                spaceBefore=1,
                spaceAfter=4
            )
        ]

    def generate_resume_pdf(self, resume_data: dict) -> bytes:
        """
        Builds an ATS-friendly resume PDF in memory and returns raw PDF bytes.
        
        resume_data structure:
        {
            "profile": dict,
            "target_role": str,
            "custom_summary": str,
            "skills": list of dict,
            "experiences": list of dict,
            "projects": list of dict,
            "education": list of dict,
            "certifications": list of dict,
            "achievements": list of dict
        }
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,  # 0.5 inch margins
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        profile = resume_data.get("profile", {})
        target_role = resume_data.get("target_role", "")
        summary = resume_data.get("custom_summary") or profile.get("summary", "")

        # 1. Contact Header
        full_name = profile.get("full_name", "Candidate Name")
        headline = target_role or profile.get("headline", "")
        
        story.append(Paragraph(full_name, self.styles["ResumeName"]))
        if headline:
            story.append(Paragraph(headline, self.styles["ResumeHeadline"]))

        # Build contact items
        contact_parts = []
        if profile.get("email"):
            contact_parts.append(profile["email"])
        if profile.get("phone"):
            contact_parts.append(profile["phone"])
        if profile.get("location"):
            contact_parts.append(profile["location"])
        if profile.get("linkedin_url"):
            # Clean URL for display
            display_linkedin = profile["linkedin_url"].replace("https://", "").replace("www.", "")
            contact_parts.append(display_linkedin)
        if profile.get("github_url"):
            display_github = profile["github_url"].replace("https://", "").replace("www.", "")
            contact_parts.append(display_github)
        if profile.get("portfolio_url"):
            display_portfolio = profile["portfolio_url"].replace("https://", "").replace("www.", "")
            contact_parts.append(display_portfolio)

        contact_line = "  •  ".join(contact_parts)
        story.append(Paragraph(contact_line, self.styles["ResumeContact"]))

        # 2. Professional Summary
        if summary and summary.strip():
            story.extend(self._section_heading("Professional Summary"))
            story.append(Paragraph(summary.strip(), self.styles["ResumeBody"]))
            story.append(Spacer(1, 3))

        # 3. Technical Skills (Grouped by Category)
        skills = resume_data.get("skills", [])
        if skills:
            story.extend(self._section_heading("Technical Skills"))
            # Group skills by category
            categories = {}
            for sk in skills:
                cat = sk.get("category", "Core Skills")
                categories.setdefault(cat, []).append(sk.get("name", ""))

            for cat, skill_names in categories.items():
                skills_line = f"<b>{cat}:</b> " + ", ".join(skill_names)
                story.append(Paragraph(skills_line, self.styles["ResumeBody"]))
            story.append(Spacer(1, 3))

        # 4. Work Experience
        experiences = resume_data.get("experiences", [])
        if experiences:
            story.extend(self._section_heading("Work Experience"))
            for exp in experiences:
                company = exp.get("company", "")
                role = exp.get("role", "")
                location = exp.get("location", "")
                start = exp.get("start_date", "")
                end = "Present" if exp.get("is_current") else exp.get("end_date", "")
                date_str = f"{start} – {end}" if start or end else ""

                # Header table with Company on Left, Date on Right
                header_data = [
                    [
                        Paragraph(f"<b>{role}</b> | {company}", self.styles["ItemTitleLeft"]),
                        Paragraph(f"{date_str}", self.styles["ItemTitleRight"])
                    ]
                ]
                if location:
                    header_data.append([
                        Paragraph(f"", self.styles["ItemSubtitleLeft"]),
                        Paragraph(f"{location}", self.styles["ItemSubtitleRight"])
                    ])

                header_table = Table(header_data, colWidths=[380, 160])
                header_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))

                item_flowables = [header_table]

                if exp.get("description") and not exp.get("highlights_list"):
                    item_flowables.append(Paragraph(exp["description"], self.styles["ResumeBody"]))

                # Bullets
                highlights = exp.get("highlights_list", [])
                if not highlights and exp.get("highlights"):
                    try:
                        highlights = json.loads(exp["highlights"])
                    except Exception:
                        highlights = [exp["highlights"]]

                for h in highlights:
                    if h.strip():
                        item_flowables.append(Paragraph(f"• {h.strip()}", self.styles["ResumeBullet"]))

                item_flowables.append(Spacer(1, 4))
                story.append(KeepTogether(item_flowables))

        # 5. Technical Projects
        projects = resume_data.get("projects", [])
        if projects:
            story.extend(self._section_heading("Technical Projects"))
            for proj in projects:
                title = proj.get("title", "")
                role = proj.get("role", "")
                start = proj.get("start_date", "")
                end = proj.get("end_date", "")
                date_str = f"{start} – {end}" if start or end else ""

                # Tech stack
                tech_list = proj.get("tech_stack_list", [])
                if not tech_list and proj.get("tech_stack"):
                    try:
                        tech_list = json.loads(proj["tech_stack"])
                    except Exception:
                        tech_list = [t.strip() for t in proj["tech_stack"].split(",") if t.strip()]
                tech_str = f" ({', '.join(tech_list)})" if tech_list else ""

                header_data = [
                    [
                        Paragraph(f"<b>{title}</b>{tech_str}", self.styles["ItemTitleLeft"]),
                        Paragraph(f"{date_str}", self.styles["ItemTitleRight"])
                    ]
                ]
                header_table = Table(header_data, colWidths=[400, 140])
                header_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))

                proj_flowables = [header_table]

                if proj.get("description"):
                    proj_flowables.append(Paragraph(proj["description"], self.styles["ResumeBody"]))

                highlights = proj.get("highlights_list", [])
                if not highlights and proj.get("highlights"):
                    try:
                        highlights = json.loads(proj["highlights"])
                    except Exception:
                        highlights = [proj["highlights"]]

                for h in highlights:
                    if h.strip():
                        proj_flowables.append(Paragraph(f"• {h.strip()}", self.styles["ResumeBullet"]))

                proj_flowables.append(Spacer(1, 4))
                story.append(KeepTogether(proj_flowables))

        # 6. Education
        education = resume_data.get("education", [])
        if education:
            story.extend(self._section_heading("Education"))
            for edu in education:
                inst = edu.get("institution", "")
                degree = edu.get("degree", "")
                field = edu.get("field_of_study", "")
                gpa = edu.get("gpa", "")
                start = edu.get("start_date", "")
                end = edu.get("end_date", "")
                date_str = f"{start} – {end}" if start or end else ""

                deg_field = f"{degree} in {field}" if field else degree
                if gpa:
                    deg_field += f" (GPA: {gpa})"

                edu_data = [
                    [
                        Paragraph(f"<b>{inst}</b>", self.styles["ItemTitleLeft"]),
                        Paragraph(f"{date_str}", self.styles["ItemTitleRight"])
                    ],
                    [
                        Paragraph(f"{deg_field}", self.styles["ItemSubtitleLeft"]),
                        Paragraph("", self.styles["ItemSubtitleRight"])
                    ]
                ]
                edu_table = Table(edu_data, colWidths=[400, 140])
                edu_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))
                edu_flowables = [edu_table]
                if edu.get("description"):
                    edu_flowables.append(Paragraph(edu["description"], self.styles["ResumeBody"]))
                edu_flowables.append(Spacer(1, 3))
                story.append(KeepTogether(edu_flowables))

        # 7. Certifications
        certifications = resume_data.get("certifications", [])
        if certifications:
            story.extend(self._section_heading("Certifications"))
            for cert in certifications:
                name = cert.get("name", "")
                org = cert.get("issuing_organization", "")
                issue = cert.get("issue_date", "")
                cid = cert.get("credential_id", "")
                
                cid_str = f" (ID: {cid})" if cid else ""
                cert_data = [
                    [
                        Paragraph(f"<b>{name}</b> – {org}{cid_str}", self.styles["ItemTitleLeft"]),
                        Paragraph(f"{issue}", self.styles["ItemTitleRight"])
                    ]
                ]
                cert_table = Table(cert_data, colWidths=[420, 120])
                cert_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))
                story.append(cert_table)
            story.append(Spacer(1, 3))

        # 8. Achievements & Publications
        achievements = resume_data.get("achievements", [])
        if achievements:
            story.extend(self._section_heading("Achievements & Publications"))
            for ach in achievements:
                title = ach.get("title", "")
                issuer = ach.get("issuer_or_publisher", "")
                date_str = ach.get("date", "")
                desc = ach.get("description", "")
                
                issuer_str = f" | {issuer}" if issuer else ""
                ach_data = [
                    [
                        Paragraph(f"<b>{title}</b>{issuer_str}", self.styles["ItemTitleLeft"]),
                        Paragraph(f"{date_str}", self.styles["ItemTitleRight"])
                    ]
                ]
                ach_table = Table(ach_data, colWidths=[420, 120])
                ach_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))
                ach_flowables = [ach_table]
                if desc:
                    ach_flowables.append(Paragraph(desc, self.styles["ResumeBody"]))
                ach_flowables.append(Spacer(1, 2))
                story.append(KeepTogether(ach_flowables))

        # Build document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
