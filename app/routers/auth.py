from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserOut
from app.services.auth_service import (
    create_user, authenticate_user, create_session,
    get_user_from_session, revoke_session
)

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# Dependency to retrieve current authenticated user
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Retrieves authenticated user from session cookie or Authorization header."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None
    return get_user_from_session(db, token)

def require_auth_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Enforces authentication; raises 401 if unauthenticated."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user

# ---------------- HTML Template Routes ----------------

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})

@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        user = create_user(db, username=username, email=email, password=password, full_name=full_name)
        session_obj = create_session(db, user.id)
        
        redirect = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
        redirect.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=session_obj.session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            samesite="lax"
        )
        return redirect
    except ValueError as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": str(e), "username": username, "email": email, "full_name": full_name},
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username_or_email=username_or_email, password=password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid username/email or password.", "username_or_email": username_or_email},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    session_obj = create_session(db, user.id)
    redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_obj.session_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax"
    )
    return redirect

@router.get("/logout")
def logout_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    revoke_session(db, token)
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(settings.SESSION_COOKIE_NAME)
    return redirect

# ---------------- JSON REST API Routes ----------------

@router.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def api_register(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        user = create_user(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/api/auth/login")
def api_login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username_or_email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    session_obj = create_session(db, user.id)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_obj.session_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax"
    )
    return {
        "status": "success",
        "session_token": session_obj.session_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/api/auth/logout")
def api_logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    revoke_session(db, token)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return {"status": "success", "message": "Logged out successfully"}

@router.get("/api/auth/me", response_model=UserOut)
def api_me(user: User = Depends(require_auth_user)):
    return user
