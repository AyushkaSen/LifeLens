import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'lifelens.db'}")
USDA_DATA_PATH = DATA_DIR / "usda_foods.json"

APP_TITLE = "LifeLens - Productivity & Nutrition Analytics"
APP_DESCRIPTION = (
    "Personal behavioral, productivity, and nutrition analytics dashboard. "
    "Designed for personal habit optimization and cognitive pacing."
)
