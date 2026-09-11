import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def test_food_search_and_calculation():
    # 1. Search food database
    search_res = client.get("/api/nutrition/search?q=egg")
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) > 0
    assert any("egg" in item["name"].lower() for item in results)

    # 2. Calculate nutrition for 2 eggs
    calc_res = client.post(
        "/api/nutrition/calculate",
        json={"food_name": "egg", "quantity": 2.0, "unit": "egg"},
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["is_exact_match"] is True
    # 2 eggs ~ 100g -> ~143 kcal, ~12.6g protein
    assert 130 <= calc_data["calories"] <= 160
    assert 11 <= calc_data["protein_g"] <= 14


def test_meal_creation_and_rollups():
    # Log a breakfast with 2 items
    meal_payload = {
        "meal_type": "Breakfast",
        "notes": "Post-workout recovery fuel",
        "items": [
            {"food_name": "Whole Egg, Raw or Cooked", "quantity": 2.0, "unit": "egg"},
            {"food_name": "Rolled Oats / Oatmeal (Dry)", "quantity": 1.0, "unit": "cup"},
        ],
    }
    create_res = client.post("/api/meals", json=meal_payload)
    assert create_res.status_code == 201
    meal = create_res.json()
    assert meal["meal_type"] == "Breakfast"
    assert len(meal["items"]) == 2
    assert meal["total_calories"] > 300
    assert meal["total_protein_g"] >= 15.0

    # List meals
    list_res = client.get("/api/meals")
    assert list_res.status_code == 200
    meals = list_res.json()
    assert any(m["id"] == meal["id"] for m in meals)

    # Delete meal
    del_res = client.delete(f"/api/meals/{meal['id']}")
    assert del_res.status_code == 200
