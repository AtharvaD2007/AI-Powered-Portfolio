import pytest
from backend.app import create_app
from backend.database import load_sample_data, get_full_portfolio

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            load_sample_data(clear_existing=True)
        yield client

def test_ai_organizer_flow(client):
    unstructured_note = """
    Jane Doe
    jane.doe@example.com
    (555) 987-6543
    https://github.com/janedoe

    Skills:
    - Docker
    - Go
    - PostgreSQL

    Projects:
    - Cloud Microservices: Built an API gateway using Go and Docker. Handled 500 req/s.

    Experience:
    - Acme Corp: Software Intern from 2023-05 to 2023-08. Worked on internal databases.
    """

    # 1. Organize unstructured text
    res = client.post("/api/ai/organize", json={"text": unstructured_note})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "history_id" in data
    assert "proposed_changes" in data

    proposed = data["proposed_changes"]
    history_id = data["history_id"]

    # Verify structured entity extraction
    assert proposed["profile"]["email"] == "jane.doe@example.com"
    assert any(s["name"] == "Docker" for s in proposed["skills"])

    # 2. Approve and commit changes
    approve_res = client.post("/api/ai/approve", json={
        "history_id": history_id,
        "approved_data": proposed
    })
    assert approve_res.status_code == 200
    summary = approve_res.get_json()["summary"]
    assert summary["skills_added"] >= 1

    # 3. Verify history preserves original submission
    hist_res = client.get("/api/ai/history")
    assert hist_res.status_code == 200
    history_items = hist_res.get_json()["data"]
    assert any(h["id"] == history_id for h in history_items)
