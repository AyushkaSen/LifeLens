from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import APP_TITLE, APP_DESCRIPTION, STATIC_DIR
from app.database import engine, Base, SessionLocal
from app.services.nutrition_service import seed_food_reference_db
from app.routers import tasks, timer, meals, nutrition, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables & seed USDA food reference data
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_food_reference_db(db)
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(tasks.router)
app.include_router(timer.router)
app.include_router(meals.router)
app.include_router(nutrition.router)
app.include_router(analytics.router)

# Mount static directory
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serve the single page application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "LifeLens API running", "docs_url": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
