# AI-Powered Portfolio Management & Resume Generator (CareerMatrix)

An enterprise-grade, full-stack application for managing a candidate portfolio, structuring messy information with Google Gemini AI, analyzing alignment against target job descriptions, generating ATS-compliant resumes with PDF export, and synchronizing portfolio tabs to Google Sheets.

---

## 🌟 Key Features

1. **Portfolio Database Management (SQLite Primary)**
   - Full CRUD functionality across 7 structured categories:
     - **Profile & Contact**: Name, headline, email, phone, location, GitHub, LinkedIn, portfolio link, summary.
     - **Education**: Degree, institution, field of study, GPA, coursework descriptions.
     - **Skills**: Categorized (Languages, Backend & APIs, Databases, Networking & Protocols, DevOps & Tools) with proficiency ratings.
     - **Certifications**: Industry credentials, issuers, verification IDs, issue/expiration dates.
     - **Projects**: Titles, roles, tech stacks, live links, repo URLs, and bulleted achievements.
     - **Work Experience / Internships**: Roles, companies, locations, dates, and impact bullets.
     - **Achievements & Publications**: Awards, symposium research, and academic honors.
   - Powered by parameterized SQLite queries with native JSON serialization.

2. **AI Portfolio Organizer (Google Gemini API)**
   - Enter messy, unstructured notes, LinkedIn clips, or bullet points.
   - Gemini parses the input into structured entities across all portfolio categories.
   - Displays a side-by-side proposal review allowing users to inspect or discard items before committing.
   - **Data Preservation Guarantee**: Stores raw inputs in an audit history log (`organizer_history`) so original notes are never destroyed.
   - **Fallback Engine**: If `GEMINI_API_KEY` is not provided, a deterministic regex and keyword parser automatically takes over so the feature works out-of-the-box.

3. **Job Description Analyzer**
   - Paste any target job description or click one of the two included sample jobs:
     - **Junior Backend Developer** (PayFlow FinTech) — Python, REST APIs, SQL, PostgreSQL, Docker, Git.
     - **Network Support Engineer** (GlobalNet Telecom) — TCP/IP, Subnetting, VLANs, OSPF, Wireshark, CCNA.
   - Extracts required skills, preferred bonuses, and core responsibilities.
   - Computes a transparent, explainable Match Score (70% Required Skills, 15% Preferred Skills, 15% Experience/Project Alignment).
   - Identifies verified matched skills and explicit **Missing Skills**.
   - Recommends the highest-relevance projects with clear justifications.
   - **Strict Non-Fabrication Rule**: Never claims or hallucinates qualifications not in the candidate's verified portfolio.

4. **Dynamic Resume Studio & ATS PDF Generator**
   - Select a target job to tailor against.
   - Interactive checkboxes for verified skills, projects, experience, and credentials.
   - AI-assisted tailored professional summary generator (strictly referencing verified items).
   - Real-time ATS paper document preview simulator.
   - Generates and downloads clean, ATS-compliant single/multi-page PDFs using **ReportLab** (`reportlab.platypus`).
   - Supports multiple job-specific resume versions stored in SQLite without altering the primary portfolio records.

5. **Google Sheets Synchronization**
   - Exports the master portfolio into 7 dedicated worksheets: `Profile`, `Education`, `Skills`, `Certifications`, `Projects`, `Experience`, and `Achievements`.
   - Google Service Account integration via `gspread` and `google-auth`.
   - Real-time connection testing, last-sync status logging, and direct links to the Google Sheet.
   - Formatted dry-run preview available even if Google Cloud credentials are not yet configured.

---

## 🛠️ Technology Stack

- **Frontend**: React 19 + Vite + Modern CSS (Responsive, Accessible `<dialog>` modals with scroll containment, Lucide Icons).
- **Backend**: Python 3 Flask REST API with Flask-CORS.
- **Database**: SQLite 3 with parameterized queries and row factory.
- **AI Engine**: Google Gemini API via official `google-genai` Python SDK.
- **Resume Export**: ReportLab PDF library (`reportlab.platypus`, `reportlab.lib.colors`).
- **Spreadsheets**: Google Sheets API & Google Drive API via `gspread` and `google-auth`.
- **Testing**: Pytest automated test suite.

---

## 📁 Project Directory Structure

```
AI-powered_portfolio/
├── backend/
│   ├── app.py                      # Flask application factory and API routing
│   ├── config.py                   # Environment and credential management
│   ├── database.py                 # SQLite initialization and helpers
│   ├── database_schema.sql         # SQL schema definitions (11 tables)
│   ├── sample_data.py              # Dual-discipline sample candidate & jobs
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Template for environment secrets
│   ├── .env                        # Local environment configuration
│   ├── routes/
│   │   ├── portfolio_routes.py     # CRUD endpoints for all 7 portfolio sections
│   │   ├── ai_routes.py            # AI Organizer parsing & approval
│   │   ├── analyzer_routes.py      # Job requirements matching & scoring
│   │   ├── resume_routes.py        # Resume tailoring, preview, & PDF streaming
│   │   ├── sheets_routes.py        # Google Sheets status, test, & export
│   │   └── settings_routes.py      # Settings and health diagnostics
│   ├── services/
│   │   ├── gemini_service.py       # Google GenAI SDK integration & heuristic fallback
│   │   ├── analyzer_service.py     # Deterministic scoring engine & project ranker
│   │   ├── resume_pdf_service.py   # ReportLab ATS PDF generator
│   │   └── sheets_service.py       # Google Sheets exporter & preview generator
│   └── tests/
│       ├── test_portfolio.py       # Portfolio CRUD and reset tests
│       ├── test_analyzer.py        # Job match scoring & non-fabrication tests
│       ├── test_resume_pdf.py      # ReportLab binary PDF generation tests
│       └── test_ai_organizer.py    # Unstructured text parse & approval tests
├── frontend/
│   ├── index.html                  # HTML5 entry point
│   ├── package.json                # React, Vite, & Lucide dependencies
│   ├── vite.config.js              # Vite server & backend proxy configuration
│   └── src/
│       ├── main.jsx                # React root mount
│       ├── App.jsx                 # View state coordinator & toast manager
│       ├── index.css               # Modern dark theme & ATS paper simulator styles
│       ├── api/
│       │   └── api.js              # Centralized asynchronous API client
│       ├── components/
│       │   ├── Navbar.jsx          # Header with service status pills & reset button
│       │   ├── Sidebar.jsx         # 7-view navigation sidebar
│       │   ├── Modal.jsx           # Accessible native <dialog> modal component
│       │   └── Toast.jsx           # Floating notification toast
│       └── views/
│           ├── DashboardView.jsx   # Metrics & dual-track demonstration cards
│           ├── PortfolioView.jsx   # Tabbed database CRUD manager
│           ├── AIOrganizerView.jsx # Raw text input & proposed change review
│           ├── JobAnalyzerView.jsx # Match gauge, skill checklist, & project picks
│           ├── ResumeStudioView.jsx# Checkboxes, live paper preview, & PDF download
│           ├── GoogleSheetsView.jsx# Status, 7-tab preview, & sync controls
│           └── SettingsView.jsx    # API keys configuration & SQLite controls
├── README.md                       # Complete documentation
└── .gitignore                      # Git exclusion rules
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ and npm 9+ (Tested on Node v24)

### 1. Backend Setup
From the project root:

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment variables
cp backend/.env.example backend/.env

# 4. Run automated tests to verify setup
PYTHONPATH=. pytest backend/tests

# 5. Start Flask backend server
python3 -m backend.app
```
The backend starts on `http://127.0.0.1:5001`.

### 2. Frontend Setup
In a new terminal window:

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies (if not already installed)
npm install

# 3. Start Vite dev server
npm run dev
```
The frontend starts on `http://localhost:5173` with automatic API proxying to port 5001.

---

## 🔑 External Credentials Setup

### A. Google Gemini API (Recommended)
1. Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Open `backend/.env` and paste your key:
   ```env
   GEMINI_API_KEY=AIzaSy...
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. Alternatively, you can paste the key directly in the application's **Settings** tab for runtime usage.
> **Note**: If no Gemini API key is configured, the application remains fully functional using its built-in heuristic NLP parsing engine.

### B. Google Sheets API Integration
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Google Sheets API** and **Google Drive API**.
3. Under **IAM & Admin > Service Accounts**, create a service account and click **Manage Keys > Add Key > Create New Key (JSON)**.
4. Save the downloaded JSON file as `backend/service_account.json`.
5. Create a new Google Spreadsheet in your personal Google Drive and copy the Sheet ID from its URL:
   `https://docs.google.com/spreadsheets/d/<GOOGLE_SHEET_ID>/edit`
6. **Important**: Click **Share** on your Google Sheet and add your service account's `client_email` (e.g. `career-service@your-project.iam.gserviceaccount.com`) as an **Editor**.
7. In `backend/.env`, configure:
   ```env
   GOOGLE_SHEETS_CREDENTIALS_JSON=backend/service_account.json
   GOOGLE_SHEET_ID=your_sheet_id_here
   ```
8. In the **Google Sheets** view in the UI, click **Test Connection** and **Export to Google Sheets**.

---

## 🎯 Dual-Discipline Demonstration Walkthrough

CareerMatrix includes rich fictional sample data for **Alex Morgan**, a candidate with hands-on capability in both Software Development and Network Engineering:

- **Software Projects**: Distributed Task Queue & REST API Platform (Python, Flask, Redis, PostgreSQL), Cloud Microservices Gateway.
- **Networking Projects**: Enterprise Campus Network & VLAN Topology (Cisco Packet Tracer, 802.1Q, OSPF, Wireshark), Real-Time Packet Sniffer.
- **Experience**: Backend Engineering Intern at TechNova Systems; Network Support Specialist at Campus IT.
- **Certifications**: Cisco CCNA (200-301), Python PCAP, AWS Certified Cloud Practitioner.

### Demonstration 1: Junior Backend Developer
1. Go to the **Job Analyzer** view.
2. Click the preset button **Junior Backend Developer** (PayFlow Systems).
3. Click **Analyze Job Alignment**.
   - Matched skills: Python, REST APIs, SQL, PostgreSQL, Docker, Git.
   - Recommended project: *Distributed Task Queue & REST API Platform*.
4. Click **Build Tailored Resume**.
5. Notice that the Resume Studio automatically selects backend skills and projects.
6. Click **Download ATS PDF** to receive `Alex_Morgan_Junior_Backend_Developer_Resume.pdf`.

### Demonstration 2: Network Support Engineer
1. Return to the **Job Analyzer** view.
2. Click the preset button **Network Support Engineer** (GlobalNet Telecom).
3. Click **Analyze Job Alignment**.
   - Matched skills: TCP/IP, Subnetting, VLANs, OSPF, Routing, Wireshark, CCNA.
   - Recommended project: *Enterprise Campus Network & VLAN Topology*.
4. Click **Build Tailored Resume**.
5. Notice that the exact same master portfolio now generates a networking-tailored resume highlighting the CCNA and Campus IT experience.
6. Click **Download ATS PDF** to receive `Alex_Morgan_Network_Support_Engineer_Resume.pdf`.

Both resumes are generated without modifying or duplicating the master database records!

---

## 🧪 Automated Testing

Run the full automated test suite anytime with:

```bash
PYTHONPATH=. pytest backend/tests -v
```

**Test Coverage**:
- `test_portfolio.py`: Verifies SQLite schema creation, full portfolio retrieval, and CRUD mutations.
- `test_analyzer.py`: Verifies match scoring for both Backend and Networking jobs, checks transparent score formulas, and asserts strict non-fabrication of unverified skills.
- `test_resume_pdf.py`: Verifies ReportLab ATS layout assembly, PDF magic header (`%PDF-1.`), and binary streaming.
- `test_ai_organizer.py`: Verifies entity extraction, approval workflow, and audit log persistence.

---

## 🔒 Security & Privacy

- External credentials (`GEMINI_API_KEY`, `GOOGLE_SHEETS_CREDENTIALS_JSON`) are isolated on the backend in `.env` and never exposed to the frontend or committed to git.
- All database queries use parameterized SQL execution (`?` placeholders) to prevent SQL injection.
- The ATS Resume Generator strictly enforces truth: Missing skills are reported as missing and never hallucinated into resumes.
