import pytest
import io
from backend.app import create_app
from backend.database import load_sample_data, get_full_portfolio
from backend.services.resume_pdf_service import ResumePDFService
from backend.routes.resume_routes import assemble_resume_payload

@pytest.fixture
def sample_portfolio():
    app = create_app()
    with app.app_context():
        load_sample_data(clear_existing=True)
        return get_full_portfolio()

def test_generate_pdf_resume(sample_portfolio):
    pdf_service = ResumePDFService()
    resume_payload = assemble_resume_payload(
        selected_items={
            "education_ids": [1],
            "skill_ids": [1, 2, 3, 4, 5],
            "project_ids": [1, 2],
            "experience_ids": [1],
            "certification_ids": [1],
            "achievement_ids": [1]
        },
        custom_summary="Dedicated software and network systems engineer.",
        target_role="Junior Backend Developer"
    )

    pdf_bytes = pdf_service.generate_resume_pdf(resume_payload)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # Standard PDF magic header check
    assert pdf_bytes.startswith(b"%PDF-1.")

def test_resume_pdf_download_endpoint():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            load_sample_data(clear_existing=True)

        res = client.post("/api/resumes/download-pdf", json={
            "target_role": "Network Support Engineer",
            "custom_summary": "CCNA-certified engineer.",
            "selected_items": {}
        })

        assert res.status_code == 200
        assert res.mimetype == "application/pdf"
        assert res.data.startswith(b"%PDF-1.")
