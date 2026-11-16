from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserProfile
from app.schemas import UserProfileUpdate, UserProfileOut
from app.routers.auth import get_current_user, require_auth_user

router = APIRouter(tags=["Learner Profile"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

def get_or_create_profile(db: Session, user: User) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

# ---------------- HTML Template Routes ----------------

@router.get("/profile", response_class=HTMLResponse)
def view_profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
    profile = get_or_create_profile(db, user)
    return templates.TemplateResponse(
        "profile/profile.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "success_msg": request.query_params.get("saved")
        }
    )

@router.post("/profile", response_class=HTMLResponse)
def update_profile_page(
    request: Request,
    stream: str = Form("CSE"),
    cgpa_range: str = Form("6–8"),
    practical_preference: str = Form("Yes"),
    logical_reasoning: str = Form("Good"),
    problem_solving: str = Form("Good"),
    programming_knowledge: str = Form("Intermediate"),
    communication_skills: str = Form("Good"),
    creativity_level: str = Form("Good"),
    primary_interest: str = Form("Software and Technology"),
    experience_level: str = Form("No experience"),
    projects_completed: str = Form("None"),
    certifications: str = Form("None"),
    preferred_career_type: str = Form("Technical role"),
    preferred_industry: str = Form("IT"),
    preferred_work_environment: str = Form("Hybrid"),
    career_goal: str = Form("Entry-level job"),
    bio: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    profile = get_or_create_profile(db, user)
    profile.stream = stream
    profile.cgpa_range = cgpa_range
    profile.practical_preference = practical_preference
    profile.logical_reasoning = logical_reasoning
    profile.problem_solving = problem_solving
    profile.programming_knowledge = programming_knowledge
    profile.communication_skills = communication_skills
    profile.creativity_level = creativity_level
    profile.primary_interest = primary_interest
    profile.experience_level = experience_level
    profile.projects_completed = projects_completed
    profile.certifications = certifications
    profile.preferred_career_type = preferred_career_type
    profile.preferred_industry = preferred_industry
    profile.preferred_work_environment = preferred_work_environment
    profile.career_goal = career_goal
    profile.bio = bio
    
    db.commit()
    db.refresh(profile)
    return RedirectResponse(url="/profile?saved=true", status_code=status.HTTP_302_FOUND)

# ---------------- REST API Routes ----------------

@router.get("/api/profile", response_model=UserProfileOut)
def api_get_profile(user: User = Depends(require_auth_user), db: Session = Depends(get_db)):
    return get_or_create_profile(db, user)

@router.put("/api/profile", response_model=UserProfileOut)
def api_update_profile(
    payload: UserProfileUpdate,
    user: User = Depends(require_auth_user),
    db: Session = Depends(get_db)
):
    profile = get_or_create_profile(db, user)
    for field, val in payload.dict(exclude_unset=True).items():
        setattr(profile, field, val)
    db.commit()
    db.refresh(profile)
    return profile
