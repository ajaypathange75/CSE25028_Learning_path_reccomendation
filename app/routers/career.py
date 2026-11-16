from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User, AssessmentResponse, CareerPrediction,
    UserCareerSelection, UserProfile
)
from app.schemas import (
    CareerAssessmentInput, CareerPredictionOut,
    CareerAcceptanceRequest, AlternativeCareerSelectRequest
)
from app.routers.auth import get_current_user, require_auth_user
from app.services.preprocessing_service import preprocessing_service
from app.services.ml_service import ml_service
from app.services.knowledge_graph import knowledge_graph

router = APIRouter(tags=["Career Assessment & Prediction"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# ---------------- HTML Template Routes ----------------

@router.get("/career/assessment", response_class=HTMLResponse)
def career_assessment_page(request: Request, db: Session = Depends(get_db)):
    """Stage 4: Career Assessment Questionnaire Form."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Check if user has saved profile to pre-fill default values
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    return templates.TemplateResponse(
        "career/assessment.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "feature_mappings": preprocessing_service.feature_mappings,
            "error": None
        }
    )

@router.post("/career/assessment", response_class=HTMLResponse)
def career_assessment_submit(
    request: Request,
    # 5 Personality
    q1_party: str = Form(...),
    q2_stressed: str = Form(...),
    q3_details: str = Form(...),
    q4_sympathize: str = Form(...),
    q5_vocab: str = Form(...),
    # 3 Academic
    q6_cgpa: str = Form(...),
    q7_stream: str = Form(...),
    q8_practical: str = Form(...),
    # 5 Skill self-ratings
    q9_reasoning: str = Form(...),
    q10_problem_solving: str = Form(...),
    q11_programming: str = Form(...),
    q12_communication: str = Form(...),
    q13_creativity: str = Form(...),
    # 8 Profile preferences
    q14_interest: str = Form(...),
    q15_experience: str = Form(...),
    q16_projects: str = Form(...),
    q17_certifications: str = Form(...),
    q18_career_type: str = Form(...),
    q19_industry: str = Form(...),
    q20_work_env: str = Form(...),
    q21_career_goal: str = Form(...),
    db: Session = Depends(get_db)
):
    """Stages 4, 5, 6: Process Assessment -> Encode -> ML Predict -> Persist."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Map form fields directly to the exact 21 feature column strings expected by the model
    raw_responses = {
        "I am the life of the party.": q1_party,
        "I get stressed out easily.": q2_stressed,
        "I pay attention to details.": q3_details,
        "I sympathize with others’ feelings.": q4_sympathize,
        "I have a rich vocabulary.": q5_vocab,
        "What is your CGPA range?": q6_cgpa,
        "Which stream are you studying?": q7_stream,
        "Do you prefer practical assignments over theory?": q8_practical,
        "Rate your logical reasoning ability.": q9_reasoning,
        "How do you rate your problem-solving skills.": q10_problem_solving,
        "Rate your programming knowledge.": q11_programming,
        "How are your communication skills?": q12_communication,
        "Rate your creativity level.": q13_creativity,
        "Primary interest": q14_interest,
        "Experience level": q15_experience,
        "Projects completed": q16_projects,
        "Certifications": q17_certifications,
        "Preferred career type": q18_career_type,
        "Preferred industry": q19_industry,
        "Preferred work environment": q20_work_env,
        "Career goal": q21_career_goal
    }

    try:
        # Stage 5: Input Preprocessing using existing encoding mappings
        feature_vector, encoded_dict = preprocessing_service.validate_and_encode_response(raw_responses)
        
        # Persist Assessment
        assessment = AssessmentResponse(
            user_id=user.id,
            responses_json=raw_responses
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Stage 6: ML Career Prediction
        prediction_result = ml_service.predict(feature_vector)
        predicted_career = prediction_result["predicted_career"]
        confidence = prediction_result["confidence_score"]
        probs = prediction_result["probabilities"]

        # Persist CareerPrediction
        pred_record = CareerPrediction(
            user_id=user.id,
            assessment_id=assessment.id,
            predicted_career=predicted_career,
            confidence_score=confidence,
            probabilities_json=probs,
            is_accepted=None
        )
        db.add(pred_record)
        db.commit()
        db.refresh(pred_record)

        return RedirectResponse(url=f"/career/prediction/{pred_record.id}", status_code=status.HTTP_302_FOUND)

    except ValueError as e:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        return templates.TemplateResponse(
            "career/assessment.html",
            {
                "request": request,
                "user": user,
                "profile": profile,
                "feature_mappings": preprocessing_service.feature_mappings,
                "error": str(e)
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.get("/career/prediction/{prediction_id}", response_class=HTMLResponse)
def view_prediction_page(prediction_id: int, request: Request, db: Session = Depends(get_db)):
    """Stage 7: Display Predicted Career Path with metadata."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pred = db.query(CareerPrediction).filter(
        CareerPrediction.id == prediction_id,
        CareerPrediction.user_id == user.id
    ).first()

    if not pred:
        raise HTTPException(status_code=404, detail="Prediction record not found")

    career_meta = knowledge_graph.careers.get(pred.predicted_career, {
        "overview": "Exciting professional domain focused on high impact and growth.",
        "learning_objectives": ["Master core skills", "Build portfolio projects", "Continuous learning"],
        "career_requirements": ["Discipline", "Analytical mindset", "Domain expertise"]
    })
    
    required_skills = knowledge_graph.get_career_skills(pred.predicted_career)
    relevant_concepts = [
        knowledge_graph.concepts.get(cid, {}).get("title", cid)
        for cid in knowledge_graph.get_career_concepts(pred.predicted_career)
    ]

    return templates.TemplateResponse(
        "career/prediction.html",
        {
            "request": request,
            "user": user,
            "prediction": pred,
            "career_meta": career_meta,
            "required_skills": required_skills,
            "relevant_concepts": relevant_concepts,
            "probabilities": pred.probabilities_json or {}
        }
    )

@router.post("/career/decision", response_class=HTMLResponse)
def career_decision_submit(
    request: Request,
    prediction_id: int = Form(...),
    decision: str = Form(...),  # 'accept' or 'reject'
    db: Session = Depends(get_db)
):
    """Stage 8: Accept or Reject predicted career."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pred = db.query(CareerPrediction).filter(
        CareerPrediction.id == prediction_id,
        CareerPrediction.user_id == user.id
    ).first()

    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if decision == "accept":
        pred.is_accepted = True
        
        # Deactivate previous active career selections
        db.query(UserCareerSelection).filter(
            UserCareerSelection.user_id == user.id
        ).update({"is_active": False})

        # Stage 10: Selected Career Path set as active target career
        selection = UserCareerSelection(
            user_id=user.id,
            prediction_id=pred.id,
            selected_career=pred.predicted_career,
            selection_type="predicted_accepted",
            is_active=True
        )
        db.add(selection)
        db.commit()

        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    else:
        # Rejection -> proceed to Stage 9: Alternative Career Recommendation
        pred.is_accepted = False
        db.commit()
        return RedirectResponse(url=f"/career/alternatives/{pred.id}", status_code=status.HTTP_302_FOUND)

@router.get("/career/alternatives/{prediction_id}", response_class=HTMLResponse)
def view_alternatives_page(prediction_id: int, request: Request, db: Session = Depends(get_db)):
    """Stage 9: Alternative Career Recommendation when user rejects prediction."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pred = db.query(CareerPrediction).filter(
        CareerPrediction.id == prediction_id,
        CareerPrediction.user_id == user.id
    ).first()

    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    probs = pred.probabilities_json or {}
    alternatives = ml_service.get_alternative_recommendations(
        predicted_career=pred.predicted_career,
        probabilities=probs,
        top_n=5
    )

    # Attach career metadata to alternatives
    for alt in alternatives:
        c_name = alt["career_name"]
        meta = knowledge_graph.careers.get(c_name, {})
        alt["overview"] = meta.get("overview", "")
        alt["skills"] = knowledge_graph.get_career_skills(c_name)

    return templates.TemplateResponse(
        "career/alternatives.html",
        {
            "request": request,
            "user": user,
            "prediction": pred,
            "alternatives": alternatives
        }
    )

@router.post("/career/select-alternative", response_class=HTMLResponse)
def select_alternative_submit(
    request: Request,
    prediction_id: int = Form(...),
    selected_career: str = Form(...),
    db: Session = Depends(get_db)
):
    """Stage 10: Persist chosen alternative as user's active target career."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pred = db.query(CareerPrediction).filter(
        CareerPrediction.id == prediction_id,
        CareerPrediction.user_id == user.id
    ).first()

    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Deactivate previous active career selections
    db.query(UserCareerSelection).filter(
        UserCareerSelection.user_id == user.id
    ).update({"is_active": False})

    selection = UserCareerSelection(
        user_id=user.id,
        prediction_id=pred.id,
        selected_career=selected_career,
        selection_type="alternative_selected",
        is_active=True
    )
    db.add(selection)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# ---------------- REST API Routes ----------------

@router.post("/api/career/assess", response_model=CareerPredictionOut)
def api_assess_career(
    payload: CareerAssessmentInput,
    user: User = Depends(require_auth_user),
    db: Session = Depends(get_db)
):
    raw_responses = {
        "I am the life of the party.": payload.q1_party,
        "I get stressed out easily.": payload.q2_stressed,
        "I pay attention to details.": payload.q3_details,
        "I sympathize with others’ feelings.": payload.q4_sympathize,
        "I have a rich vocabulary.": payload.q5_vocab,
        "What is your CGPA range?": payload.q6_cgpa,
        "Which stream are you studying?": payload.q7_stream,
        "Do you prefer practical assignments over theory?": payload.q8_practical,
        "Rate your logical reasoning ability.": payload.q9_reasoning,
        "How do you rate your problem-solving skills.": payload.q10_problem_solving,
        "Rate your programming knowledge.": payload.q11_programming,
        "How are your communication skills?": payload.q12_communication,
        "Rate your creativity level.": payload.q13_creativity,
        "Primary interest": payload.q14_interest,
        "Experience level": payload.q15_experience,
        "Projects completed": payload.q16_projects,
        "Certifications": payload.q17_certifications,
        "Preferred career type": payload.q18_career_type,
        "Preferred industry": payload.q19_industry,
        "Preferred work environment": payload.q20_work_env,
        "Career goal": payload.q21_career_goal
    }

    try:
        feature_vector, _ = preprocessing_service.validate_and_encode_response(raw_responses)
        
        assessment = AssessmentResponse(user_id=user.id, responses_json=raw_responses)
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        pred_res = ml_service.predict(feature_vector)
        pred_record = CareerPrediction(
            user_id=user.id,
            assessment_id=assessment.id,
            predicted_career=pred_res["predicted_career"],
            confidence_score=pred_res["confidence_score"],
            probabilities_json=pred_res["probabilities"],
            is_accepted=None
        )
        db.add(pred_record)
        db.commit()
        db.refresh(pred_record)

        meta = knowledge_graph.careers.get(pred_record.predicted_career, {})
        return CareerPredictionOut(
            id=pred_record.id,
            predicted_career=pred_record.predicted_career,
            confidence_score=pred_record.confidence_score,
            probabilities=pred_record.probabilities_json or {},
            career_overview=meta.get("overview", ""),
            required_skills=knowledge_graph.get_career_skills(pred_record.predicted_career),
            relevant_concepts=[
                knowledge_graph.concepts.get(cid, {}).get("title", cid)
                for cid in knowledge_graph.get_career_concepts(pred_record.predicted_career)
            ],
            learning_objectives=meta.get("learning_objectives", []),
            career_requirements=meta.get("career_requirements", []),
            created_at=pred_record.created_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
