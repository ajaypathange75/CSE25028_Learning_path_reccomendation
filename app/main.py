from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import init_db
from app.routers import (
    auth, profile, career,
    learning, assessment, dashboard
)
from app.services.ml_service import ml_service
from app.services.gemma_service import gemma_service

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Career Path Recommendation and Personalized Learning System integrating "
        "Trained Machine Learning Models, Career Knowledge Graph, Bayesian Knowledge Tracing (BKT), "
        "and Mandatory Gemma 3:1B LLM Guidance."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Static files and Templates
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Register Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(career.router)
app.include_router(learning.router)
app.include_router(assessment.router)
app.include_router(dashboard.router)

# Startup Hook
@app.on_event("startup")
def on_startup():
    """Initializes SQLite database tables on application start."""
    init_db()

# System Diagnostic & Health Check Endpoints
@app.get("/api/health", tags=["System"])
def system_health():
    """Returns application health and subsystem statuses."""
    gemma_status = gemma_service.check_health()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "sqlite_connected",
        "ml_model": {
            "status": ml_service.model_load_status,
            "diagnostic": ml_service.diagnostic_message
        },
        "gemma_llm": gemma_status
    }

# Friendly 404 handler
@app.exception_handler(404)
def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request, "detail": str(exc.detail if hasattr(exc, "detail") else "Page not found")},
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
