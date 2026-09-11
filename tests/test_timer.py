import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def test_focus_session_recording():
    # 1. Create a task to tie the session to
    task_res = client.post(
        "/api/tasks",
        json={
            "title": "Deep Focus Sprint",
            "category": "Deep Work",
            "priority": "High",
            "estimated_duration_minutes": 25,
        },
    )
    task_id = task_res.json()["id"]

    # 2. Record a completed session
    session_res = client.post(
        "/api/timer/sessions",
        json={
            "task_id": task_id,
            "planned_duration_minutes": 25,
            "actual_duration_minutes": 25.0,
            "status": "completed",
            "notes": "Finished architecture draft with zero distraction",
        },
    )
    assert session_res.status_code == 201
    s_data = session_res.json()
    assert s_data["task_id"] == task_id
    assert s_data["task_title"] == "Deep Focus Sprint"
    assert s_data["actual_duration_minutes"] == 25.0
    assert s_data["status"] == "completed"

    # 3. Retrieve sessions list
    list_res = client.get("/api/timer/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert len(sessions) >= 1
    assert any(s["id"] == s_data["id"] for s in sessions)
