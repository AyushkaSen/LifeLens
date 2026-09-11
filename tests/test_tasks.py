import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def test_task_crud_lifecycle():
    # 1. Create a task
    response = client.post(
        "/api/tasks",
        json={
            "title": "Build Architecture Plan",
            "category": "Work",
            "priority": "High",
            "estimated_duration_minutes": 45,
        },
    )
    assert response.status_code == 201
    data = response.json()
    task_id = data["id"]
    assert data["title"] == "Build Architecture Plan"
    assert data["status"] == "pending"
    assert data["estimated_duration_minutes"] == 45

    # 2. List tasks
    list_res = client.get("/api/tasks")
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert any(t["id"] == task_id for t in tasks)

    # 3. Toggle task completion
    toggle_res = client.patch(f"/api/tasks/{task_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["status"] == "completed"
    assert toggle_res.json()["completed_at"] is not None

    # Toggle back
    toggle_back = client.patch(f"/api/tasks/{task_id}/toggle")
    assert toggle_back.status_code == 200
    assert toggle_back.json()["status"] == "pending"

    # 4. Update task
    update_res = client.put(
        f"/api/tasks/{task_id}",
        json={"priority": "Urgent", "estimated_duration_minutes": 60},
    )
    assert update_res.status_code == 200
    assert update_res.json()["priority"] == "Urgent"
    assert update_res.json()["estimated_duration_minutes"] == 60

    # 5. Delete task
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200

    # Verify deleted
    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 404
