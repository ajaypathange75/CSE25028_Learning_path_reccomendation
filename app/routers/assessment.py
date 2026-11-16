from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import (
    User, UserCareerSelection, QuizAttempt,
    LearnerCompetency
)
from app.schemas import QuizSubmitRequest, QuizEvaluationOut
from app.routers.auth import get_current_user, require_auth_user
from app.services.knowledge_graph import knowledge_graph
from app.services.competency_service import competency_service
from app.services.gemma_service import gemma_service

router = APIRouter(tags=["AI Quizzes & Assessments"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# Temporary cache for active in-flight quizzes to enable server-side scoring
ACTIVE_QUIZ_CACHE: Dict[str, Dict[str, Any]] = {}
ACTIVE_RESULT_CACHE: Dict[str, Dict[str, Any]] = {}

# ---------------- HTML Template Routes ----------------

@router.get("/assessment/quiz/{concept_id}", response_class=HTMLResponse)
def generate_and_render_quiz(
    concept_id: str,
    request: Request,
    count: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generates multi-question AI assessment based on user choice: 3, 5, 8, or 10 questions.
    Renders questions with randomized option choices to eliminate option bias.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    c_meta = knowledge_graph.concepts.get(concept_id)
    if not c_meta:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Validate count parameter against allowed options [3, 5, 8, 10]
    valid_counts = [3, 5, 8, 10]
    if count not in valid_counts:
        count = min(valid_counts, key=lambda x: abs(x - count))

    career_name = c_meta.get("career", "General")
    skill_name = c_meta.get("skill", "General")

    # Generate multi-question quiz with exact user-selected count
    res = gemma_service.generate_multi_quiz_for_concept(
        concept_title=c_meta["title"],
        skill_name=skill_name,
        career_name=career_name,
        count=count,
        difficulty="intermediate",
        concept_id=concept_id
    )

    if not res["available"]:
        return templates.TemplateResponse(
            "assessment/service_unavailable.html",
            {
                "request": request,
                "user": user,
                "concept_id": concept_id,
                "concept_title": c_meta["title"],
                "error_message": res["error_message"]
            }
        )

    quiz_data = res["quiz"]
    session_token = quiz_data["session_token"]
    questions = quiz_data["questions"]

    # Store server-side validation data in cache
    ACTIVE_QUIZ_CACHE[session_token] = {
        "session_token": session_token,
        "concept_id": concept_id,
        "concept_title": c_meta["title"],
        "count": len(questions),
        "difficulty": quiz_data["difficulty"],
        "questions": questions
    }

    return templates.TemplateResponse(
        "assessment/quiz.html",
        {
            "request": request,
            "user": user,
            "concept_id": concept_id,
            "concept_title": c_meta["title"],
            "session_token": session_token,
            "quiz_token": session_token,
            "count": len(questions),
            "selected_count": count,
            "allowed_counts": valid_counts,
            "questions": questions,
            "difficulty": quiz_data["difficulty"]
        }
    )

@router.post("/assessment/quiz/submit", response_class=HTMLResponse)
async def submit_quiz_answer(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Evaluates multi-question assessment submissions (3, 5, 8, 10 questions),
    applies sequential Bayesian Knowledge Tracing (BKT) updates, and stores audit logs.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    form_data = await request.form()
    session_token = str(form_data.get("session_token") or form_data.get("quiz_token") or "").strip()

    quiz_cache = ACTIVE_QUIZ_CACHE.get(session_token)

    # If not in memory (e.g. server restart), check if already submitted in DB
    if not quiz_cache:
        existing = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.quiz_token.like(f"{session_token}%")
        ).first()
        if existing:
            return RedirectResponse(url=f"/assessment/result/session/{session_token}", status_code=status.HTTP_302_FOUND)
        raise HTTPException(status_code=400, detail="Quiz session expired or invalid. Please generate a new quiz.")

    concept_id = quiz_cache["concept_id"]
    questions_list = quiz_cache["questions"]

    # Collect answers for all questions
    submitted_answers: Dict[int, str] = {}
    for q in questions_list:
        q_idx = q["q_idx"]
        ans = form_data.get(f"selected_option_{q_idx}") or form_data.get(f"selected_option") or ""
        submitted_answers[q_idx] = str(ans).strip().upper()

    # Execute sequential BKT update & store persistent attempts
    summary = competency_service.record_multi_quiz_assessment_and_update_bkt(
        db=db,
        user_id=user.id,
        session_token=session_token,
        concept_id=concept_id,
        submitted_answers=submitted_answers,
        questions_list=questions_list,
        difficulty=quiz_cache.get("difficulty", "intermediate")
    )

    # Store result summary in cache
    ACTIVE_RESULT_CACHE[session_token] = summary
    ACTIVE_QUIZ_CACHE.pop(session_token, None)

    return RedirectResponse(url=f"/assessment/result/session/{session_token}", status_code=status.HTTP_302_FOUND)

@router.get("/assessment/result/session/{session_token}", response_class=HTMLResponse)
def view_multi_quiz_result(session_token: str, request: Request, db: Session = Depends(get_db)):
    """
    Displays comprehensive multi-question evaluation, score breakdown, BKT trajectory, and question explanations.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    summary = ACTIVE_RESULT_CACHE.get(session_token)

    if not summary:
        # Reconstruct from persistent database attempts
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.quiz_token.like(f"{session_token}%")
        ).order_by(QuizAttempt.id.asc()).all()

        if not attempts:
            raise HTTPException(status_code=404, detail="Quiz result not found")

        concept_id = attempts[0].concept_id
        comp = db.query(LearnerCompetency).filter(
            LearnerCompetency.user_id == user.id,
            LearnerCompetency.concept_id == concept_id
        ).first()

        reviews = []
        correct_count = 0
        for idx, a in enumerate(attempts, 1):
            if a.is_correct:
                correct_count += 1
            reviews.append({
                "q_idx": idx,
                "question": a.question,
                "options": a.options_json,
                "user_choice": a.selected_option,
                "correct_option": a.correct_option,
                "is_correct": a.is_correct,
                "explanation": a.explanation,
                "bkt_prior": a.bkt_prior,
                "bkt_posterior": a.bkt_posterior
            })

        total_q = len(attempts) or 1
        summary = {
            "session_token": session_token,
            "concept_id": concept_id,
            "concept_name": comp.concept_name if comp else attempts[0].concept_name,
            "total_questions": total_q,
            "correct_count": correct_count,
            "score_pct": round((correct_count / total_q) * 100, 1),
            "initial_bkt": attempts[0].bkt_prior,
            "final_bkt": attempts[-1].bkt_posterior,
            "competency_status": comp.status if comp else "developing",
            "question_reviews": reviews,
            "first_attempt_id": attempts[0].id
        }

    comp = db.query(LearnerCompetency).filter(
        LearnerCompetency.user_id == user.id,
        LearnerCompetency.concept_id == summary["concept_id"]
    ).first()

    return templates.TemplateResponse(
        "assessment/result.html",
        {
            "request": request,
            "user": user,
            "summary": summary,
            "competency": comp,
            "concept_id": summary["concept_id"]
        }
    )

@router.get("/assessment/result/{attempt_id}", response_class=HTMLResponse)
def view_quiz_result(attempt_id: int, request: Request, db: Session = Depends(get_db)):
    """Backward compatibility route for single-attempt links."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == user.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz result not found")

    # If this attempt was part of a session, redirect to the session view
    if "_" in attempt.quiz_token:
        session_token = attempt.quiz_token.rsplit("_", 1)[0]
        return RedirectResponse(url=f"/assessment/result/session/{session_token}", status_code=status.HTTP_302_FOUND)

    comp = db.query(LearnerCompetency).filter(
        LearnerCompetency.user_id == user.id,
        LearnerCompetency.concept_id == attempt.concept_id
    ).first()

    summary = {
        "session_token": attempt.quiz_token,
        "concept_id": attempt.concept_id,
        "concept_name": attempt.concept_name,
        "total_questions": 1,
        "correct_count": 1 if attempt.is_correct else 0,
        "score_pct": 100.0 if attempt.is_correct else 0.0,
        "initial_bkt": attempt.bkt_prior,
        "final_bkt": attempt.bkt_posterior,
        "competency_status": comp.status if comp else "developing",
        "question_reviews": [
            {
                "q_idx": 1,
                "question": attempt.question,
                "options": attempt.options_json,
                "user_choice": attempt.selected_option,
                "correct_option": attempt.correct_option,
                "is_correct": attempt.is_correct,
                "explanation": attempt.explanation,
                "bkt_prior": attempt.bkt_prior,
                "bkt_posterior": attempt.bkt_posterior
            }
        ],
        "first_attempt_id": attempt.id
    }

    return templates.TemplateResponse(
        "assessment/result.html",
        {
            "request": request,
            "user": user,
            "summary": summary,
            "attempt": attempt,
            "competency": comp,
            "concept_id": attempt.concept_id
        }
    )


@router.get("/assessment/history", response_class=HTMLResponse)
def view_assessment_history(request: Request, db: Session = Depends(get_db)):
    """Stage 21: Assessment History Log."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user.id
    ).order_by(QuizAttempt.attempted_at.desc()).all()

    total_attempts = len(attempts)
    correct_count = sum(1 for a in attempts if a.is_correct)
    accuracy = round((correct_count / total_attempts * 100), 1) if total_attempts > 0 else 0.0

    return templates.TemplateResponse(
        "assessment/history.html",
        {
            "request": request,
            "user": user,
            "attempts": attempts,
            "total_attempts": total_attempts,
            "correct_count": correct_count,
            "accuracy": accuracy
        }
    )

# ---------------- REST API Routes ----------------

@router.get("/api/assessment/history")
def api_assessment_history(user: User = Depends(require_auth_user), db: Session = Depends(get_db)):
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).all()
    return [
        {
            "id": a.id,
            "concept_id": a.concept_id,
            "concept_name": a.concept_name,
            "is_correct": a.is_correct,
            "bkt_prior": a.bkt_prior,
            "bkt_posterior": a.bkt_posterior,
            "attempted_at": a.attempted_at
        }
        for a in attempts
    ]
