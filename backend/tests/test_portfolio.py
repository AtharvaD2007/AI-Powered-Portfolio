import pytest
import json
from backend.app import create_app
from backend.database import get_db_connection, load_sample_data, get_full_portfolio

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            load_sample_data(clear_existing=True)
        yield client

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "SQLite"

def test_get_portfolio(client):
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    portfolio = data["data"]
    assert "profile" in portfolio
    assert portfolio["profile"]["full_name"] == "Alex Morgan"
    assert len(portfolio["skills"]) > 0
    assert len(portfolio["projects"]) > 0
    assert len(portfolio["experiences"]) > 0

def test_skills_crud(client):
    # Add new skill
    new_skill = {
        "name": "GraphQL",
        "category": "Backend & APIs",
        "proficiency": "Intermediate",
        "years_of_experience": 1.5
    }
    post_res = client.post("/api/portfolio/skills", json=new_skill)
    assert post_res.status_code == 201
    skill_id = post_res.get_json()["id"]

    # Verify skill exists
    get_res = client.get("/api/portfolio/skills")
    skills = get_res.get_json()["data"]
    assert any(s["name"] == "GraphQL" for s in skills)

    # Update skill
    put_res = client.put(f"/api/portfolio/skills/{skill_id}", json={
        "name": "GraphQL APIs",
        "category": "Backend & APIs",
        "proficiency": "Advanced",
        "years_of_experience": 2.0
    })
    assert put_res.status_code == 200

    # Delete skill
    del_res = client.delete(f"/api/portfolio/skills/{skill_id}")
    assert del_res.status_code == 200
