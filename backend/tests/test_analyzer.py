import pytest
from backend.app import create_app
from backend.database import load_sample_data, get_full_portfolio
from backend.services.analyzer_service import AnalyzerService
from backend.sample_data import SAMPLE_JOB_DESCRIPTIONS

@pytest.fixture
def sample_portfolio():
    app = create_app()
    with app.app_context():
        load_sample_data(clear_existing=True)
        return get_full_portfolio()

def test_backend_developer_job_analysis(sample_portfolio):
    analyzer = AnalyzerService()
    backend_jd = SAMPLE_JOB_DESCRIPTIONS[0] # Junior Backend Developer
    
    result = analyzer.analyze_job_against_portfolio(
        job_text=backend_jd["raw_text"],
        portfolio=sample_portfolio,
        job_title=backend_jd["title"]
    )
    
    assert result["success"] is True
    assert result["overall_score"] > 60
    assert "score_breakdown" in result
    
    # Must have matched Python, REST APIs, SQL, Git
    matched_skills = [m["job_skill"].lower() for m in result["skills_analysis"]["matched_required"]]
    assert any("python" in s for s in matched_skills)
    assert any("sql" in s or "rest" in s for s in matched_skills)
    
    # Check recommended projects
    rec_projects = result["recommended_projects"]
    assert len(rec_projects) > 0
    # Top recommended project should be backend related (Task Queue or Gateway)
    top_project_title = rec_projects[0]["title"]
    assert "Task Queue" in top_project_title or "Gateway" in top_project_title

def test_network_engineer_job_analysis(sample_portfolio):
    analyzer = AnalyzerService()
    net_jd = SAMPLE_JOB_DESCRIPTIONS[1] # Network Support Engineer
    
    result = analyzer.analyze_job_against_portfolio(
        job_text=net_jd["raw_text"],
        portfolio=sample_portfolio,
        job_title=net_jd["title"]
    )
    
    assert result["success"] is True
    assert result["overall_score"] > 60
    
    # Must match networking skills
    matched_skills = [m["job_skill"].lower() for m in result["skills_analysis"]["matched_required"]]
    assert any("tcp/ip" in s or "vlan" in s or "subnetting" in s or "wireshark" in s for s in matched_skills)
    
    # Top recommended project should be network related
    rec_projects = result["recommended_projects"]
    assert len(rec_projects) > 0
    top_project_title = rec_projects[0]["title"]
    assert "Network" in top_project_title or "Sniffer" in top_project_title

def test_missing_skills_accuracy(sample_portfolio):
    """Verifies that nonexistent skills are accurately marked missing and NOT fabricated."""
    analyzer = AnalyzerService()
    fake_job = """
    Job: Quantum Cryptography Specialist
    Requirements:
    - Haskell
    - Kubernetes
    - Quantum Key Distribution
    - Rust
    """
    result = analyzer.analyze_job_against_portfolio(fake_job, sample_portfolio, "Quantum Specialist")
    assert result["success"] is True
    missing = [m.lower() for m in result["skills_analysis"]["missing_required"]]
    assert any("quantum" in m or "haskell" in m or "rust" in m for m in missing)
    # The score should be appropriately low because user does not have these verified skills
    assert result["overall_score"] < 50
