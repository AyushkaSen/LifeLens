import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def test_dashboard_analytics_structure():
    response = client.get("/api/analytics/dashboard?days=7")
    assert response.status_code == 200
    data = response.json()

    # 1. Verify 4 Metric Cards
    assert "cards" in data
    assert len(data["cards"]) == 4
    card_titles = [c["title"] for c in data["cards"]]
    assert "Tasks Completed" in card_titles
    assert "Focus Duration" in card_titles
    assert "Metabolic Fuel" in card_titles
    assert "Discipline Streak" in card_titles

    # 2. Verify 5 Plotly Plots
    assert "plots" in data
    plots = data["plots"]
    required_plots = [
        "weekly_velocity",
        "est_vs_actual",
        "focus_time",
        "meal_timing",
        "macro_split",
    ]
    for plot_key in required_plots:
        assert plot_key in plots, f"Missing plot: {plot_key}"
        assert "data" in plots[plot_key], f"Plotly data key missing in {plot_key}"
        assert "layout" in plots[plot_key], f"Plotly layout key missing in {plot_key}"
