from pathlib import Path
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User, UserCareerSelection, CareerPrediction,
    QuizAttempt, UserProject, LearningActivity
)
from app.routers.auth import get_current_user, require_auth_user
from app.services.knowledge_graph import knowledge_graph
from app.services.competency_service import competency_service
from app.services.learning_path_service import learning_path_service
from app.services.gemma_service import gemma_service

router = APIRouter(tags=["Personalized Dashboard"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
def index_redirect(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("home.html", {"request": request, "user": None})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Stage 18 & 27: Personalized Learning Dashboard."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Fetch active target career selection
    active_selection = db.query(UserCareerSelection).filter(
        UserCareerSelection.user_id == user.id,
        UserCareerSelection.is_active == True
    ).order_by(UserCareerSelection.id.desc()).first()

    # Fetch latest prediction
    latest_prediction = db.query(CareerPrediction).filter(
        CareerPrediction.user_id == user.id
    ).order_by(CareerPrediction.id.desc()).first()

    if not active_selection:
        # User has not selected a career yet
        return templates.TemplateResponse(
            "dashboard/onboarding.html",
            {
                "request": request,
                "user": user,
                "latest_prediction": latest_prediction
            }
        )

    target_career = active_selection.selected_career

    # Compute skill gaps and competency states
    skill_gaps = learning_path_service.analyze_skill_gaps(db, user.id, target_career)
    
    # Prerequisite-aware learning path
    learning_path = learning_path_service.generate_personalized_learning_path(db, user.id, target_career)
    
    # 6-Tier Career Roadmap
    roadmap = learning_path_service.generate_career_roadmap(db, user.id, target_career)
    
    # Single recommended next activity
    next_activity = learning_path_service.get_recommended_next_activity(db, user.id, target_career)
    
    # Career Readiness Tracking
    readiness = learning_path_service.calculate_career_readiness(db, user.id, target_career)

    # Activity & Quiz metrics
    recent_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user.id
    ).order_by(QuizAttempt.attempted_at.desc()).limit(5).all()

    user_projects = db.query(UserProject).filter(
        UserProject.user_id == user.id
    ).order_by(UserProject.created_at.desc()).all()

    # Check Ollama / Gemma service health
    gemma_health = gemma_service.check_health()

    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "user": user,
            "target_career": target_career,
            "active_selection": active_selection,
            "latest_prediction": latest_prediction,
            "skill_gaps": skill_gaps,
            "learning_path": learning_path,
            "roadmap": roadmap,
            "next_activity": next_activity,
            "readiness": readiness,
            "recent_quizzes": recent_quizzes,
            "user_projects": user_projects,
            "gemma_health": gemma_health
        }
    )

# ---------------- REST API Routes ----------------

@router.get("/api/dashboard/summary")
def api_dashboard_summary(user: User = Depends(require_auth_user), db: Session = Depends(get_db)):
    active_selection = db.query(UserCareerSelection).filter(
        UserCareerSelection.user_id == user.id,
        UserCareerSelection.is_active == True
    ).first()

    if not active_selection:
        return {"status": "onboarding_required", "message": "No active career selected yet"}

    target_career = active_selection.selected_career
    skill_gaps = learning_path_service.analyze_skill_gaps(db, user.id, target_career)
    readiness = learning_path_service.calculate_career_readiness(db, user.id, target_career)
    next_act = learning_path_service.get_recommended_next_activity(db, user.id, target_career)

    return {
        "status": "active",
        "selected_career": target_career,
        "selection_type": active_selection.selection_type,
        "readiness": readiness,
        "skill_gaps": {
            "mastered_count": len(skill_gaps["mastered_concepts"]),
            "developing_count": len(skill_gaps["developing_concepts"]),
            "weak_count": len(skill_gaps["weak_concepts"]),
            "unassessed_count": len(skill_gaps["unassessed_concepts"]),
        },
        "next_recommended_activity": next_act
    }
