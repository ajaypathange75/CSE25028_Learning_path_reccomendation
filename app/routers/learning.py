from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import (
    User, UserCareerSelection, UserProfile,
    LearningActivity, UserProject, LearnerCompetency
)
from app.routers.auth import get_current_user, require_auth_user
from app.services.knowledge_graph import knowledge_graph
from app.services.competency_service import competency_service
from app.services.learning_path_service import learning_path_service
from app.services.gemma_service import gemma_service

router = APIRouter(tags=["Learning & Practice"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# ---------------- HTML Template Routes ----------------

@router.get("/learning/roadmap", response_class=HTMLResponse)
def view_roadmap_page(request: Request, db: Session = Depends(get_db)):
    """Stage 16 & 17: Interactive Career Roadmap & Gemma Guidance."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    active_selection = db.query(UserCareerSelection).filter(
        UserCareerSelection.user_id == user.id,
        UserCareerSelection.is_active == True
    ).first()

    if not active_selection:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    target_career = active_selection.selected_career
    roadmap = learning_path_service.generate_career_roadmap(db, user.id, target_career)
    skill_gaps = learning_path_service.analyze_skill_gaps(db, user.id, target_career)

    # Optional Gemma guidance fetch if requested
    fetch_ai = request.query_params.get("ai_guidance") == "true"
    ai_guidance = None
    ai_error = None

    if fetch_ai:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        prefs = {
            "stream": profile.stream if profile else "Engineering",
            "preferred_work_environment": profile.preferred_work_environment if profile else "Hybrid",
            "primary_interest": profile.primary_interest if profile else "Technology"
        }
        gemma_res = gemma_service.generate_personalized_guidance(
            career_name=target_career,
            competencies_summary={},
            skill_gaps=skill_gaps,
            user_preferences=prefs
        )
        if gemma_res["available"]:
            ai_guidance = gemma_res["guidance"]
        else:
            ai_error = gemma_res["error_message"]

    return templates.TemplateResponse(
        "learning/roadmap.html",
        {
            "request": request,
            "user": user,
            "target_career": target_career,
            "roadmap": roadmap,
            "ai_guidance": ai_guidance,
            "ai_error": ai_error,
            "fetch_ai": fetch_ai
        }
    )

@router.get("/learning/concept/{concept_id}", response_class=HTMLResponse)
def view_concept_page(concept_id: str, request: Request, db: Session = Depends(get_db)):
    """Stage 19: Concept Learning and Practice View."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    c_meta = knowledge_graph.concepts.get(concept_id)
    if not c_meta:
        raise HTTPException(status_code=404, detail="Concept not found in knowledge catalog")

    comp = competency_service.get_or_create_competency(db, user.id, concept_id)
    prereqs = [
        knowledge_graph.concepts.get(p, {}).get("title", p)
        for p in knowledge_graph.get_prerequisites(concept_id)
    ]
    curated_resources = [
        knowledge_graph.resources[r]
        for r in knowledge_graph.resource_concepts.get(concept_id, [])
    ]

    # Optional Gemma technical explanation
    fetch_explanation = request.query_params.get("explain") == "true"
    explanation = None
    explanation_error = None

    if fetch_explanation:
        gemma_res = gemma_service.explain_concept(c_meta["title"], c_meta["career"])
        if gemma_res["available"]:
            explanation = gemma_res["explanation"]
        else:
            explanation_error = gemma_res["error_message"]

    # Existing activity status
    activity = db.query(LearningActivity).filter(
        LearningActivity.user_id == user.id,
        LearningActivity.concept_id == concept_id
    ).first()

    return templates.TemplateResponse(
        "learning/concept_detail.html",
        {
            "request": request,
            "user": user,
            "concept_id": concept_id,
            "concept": c_meta,
            "competency": comp,
            "prerequisites": prereqs,
            "curated_resources": curated_resources,
            "explanation": explanation,
            "explanation_error": explanation_error,
            "activity": activity
        }
    )

@router.post("/learning/activity/update", response_class=HTMLResponse)
def update_learning_activity(
    request: Request,
    concept_id: str = Form(...),
    activity_status: str = Form(...),  # 'pending', 'in_progress', 'completed'
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Stage 19: Record learning progress on a concept."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    activity = db.query(LearningActivity).filter(
        LearningActivity.user_id == user.id,
        LearningActivity.concept_id == concept_id
    ).first()

    c_meta = knowledge_graph.concepts.get(concept_id, {})

    if not activity:
        activity = LearningActivity(
            user_id=user.id,
            concept_id=concept_id,
            title=f"Study: {c_meta.get('title', concept_id)}",
            status=activity_status,
            notes=notes
        )
        db.add(activity)
    else:
        activity.status = activity_status
        if notes:
            activity.notes = notes
        activity.updated_at = datetime.utcnow()

    db.commit()
    return RedirectResponse(url=f"/learning/concept/{concept_id}", status_code=status.HTTP_302_FOUND)

@router.get("/learning/projects", response_class=HTMLResponse)
def view_projects_page(request: Request, db: Session = Depends(get_db)):
    """Stage 19: Capstone Projects Directory & Submission."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    active_selection = db.query(UserCareerSelection).filter(
        UserCareerSelection.user_id == user.id,
        UserCareerSelection.is_active == True
    ).first()

    target_career = active_selection.selected_career if active_selection else "Software Engineer"
    
    recommended_projects = [
        p for p in knowledge_graph.projects.values() if p.get("career") == target_career
    ]
    user_projects = db.query(UserProject).filter(UserProject.user_id == user.id).all()

    return templates.TemplateResponse(
        "learning/projects.html",
        {
            "request": request,
            "user": user,
            "target_career": target_career,
            "recommended_projects": recommended_projects,
            "user_projects": user_projects
        }
    )

@router.post("/learning/projects/submit", response_class=HTMLResponse)
def submit_project(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    career_target: str = Form(...),
    submission_link: Optional[str] = Form(None),
    mark_completed: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    proj = UserProject(
        user_id=user.id,
        title=title,
        description=description,
        career_target=career_target,
        submission_link=submission_link,
        status="completed" if mark_completed else "in_progress",
        completed_at=datetime.utcnow() if mark_completed else None
    )
    db.add(proj)
    db.commit()

    return RedirectResponse(url="/learning/projects", status_code=status.HTTP_302_FOUND)
