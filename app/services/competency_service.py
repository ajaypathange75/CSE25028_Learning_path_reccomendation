from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.models import LearnerCompetency, QuizAttempt
from app.services.knowledge_graph import knowledge_graph

class CompetencyService:
    """
    Bayesian Knowledge Tracing (BKT) and Learner State Management Service.
    Implements standard Corbett & Anderson BKT formulas with state transitions.
    """
    def __init__(
        self,
        p_l0: float = settings.BKT_DEFAULT_P_L0,
        p_t: float = settings.BKT_DEFAULT_P_TRANSIT,
        p_g: float = settings.BKT_DEFAULT_P_GUESS,
        p_s: float = settings.BKT_DEFAULT_P_SLIP
    ):
        self.p_l0 = p_l0
        self.p_t = p_t
        self.p_g = p_g
        self.p_s = p_s

    def calculate_bkt_posterior(self, prior_p: float, is_correct: bool) -> float:
        """
        Calculates posterior probability P(L_t | obs) using Bayes' Rule:
        
        If correct:
            P(L_t | 1) = [P(L_{t-1}) * (1 - P(S))] / [P(L_{t-1}) * (1 - P(S)) + (1 - P(L_{t-1})) * P(G)]
            
        If incorrect:
            P(L_t | 0) = [P(L_{t-1}) * P(S)] / [P(L_{t-1}) * P(S) + (1 - P(L_{t-1})) * (1 - P(G))]
        
        Learning transition step for the next opportunity:
            P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
        """
        p_l = max(0.01, min(0.99, prior_p))
        
        if is_correct:
            numerator = p_l * (1.0 - self.p_s)
            denominator = numerator + ((1.0 - p_l) * self.p_g)
        else:
            numerator = p_l * self.p_s
            denominator = numerator + ((1.0 - p_l) * (1.0 - self.p_g))

        posterior_obs = numerator / denominator if denominator > 0 else p_l
        
        # Apply learning transition
        next_p = posterior_obs + ((1.0 - posterior_obs) * self.p_t)
        return round(float(next_p), 4)

    def determine_competency_status(self, p_knowledge: float, total_attempts: int) -> str:
        """
        Maps probability P(L) to competency state:
        - 'unassessed' if 0 attempts
        - 'weak' if p < 0.40
        - 'developing' if 0.40 <= p < 0.70
        - 'mastered' if p >= 0.70
        """
        if total_attempts == 0:
            return "unassessed"
        if p_knowledge >= settings.COMPETENCY_MASTERED_THRESHOLD:
            return "mastered"
        elif p_knowledge >= settings.COMPETENCY_DEVELOPING_THRESHOLD:
            return "developing"
        else:
            return "weak"

    def get_or_create_competency(
        self,
        db: Session,
        user_id: int,
        concept_id: str
    ) -> LearnerCompetency:
        """Retrieves existing learner competency record or initializes it."""
        rec = db.query(LearnerCompetency).filter(
            LearnerCompetency.user_id == user_id,
            LearnerCompetency.concept_id == concept_id
        ).first()

        if not rec:
            concept_data = knowledge_graph.concepts.get(concept_id, {})
            concept_name = concept_data.get("title", concept_id)
            skill_name = concept_data.get("skill", "General")

            rec = LearnerCompetency(
                user_id=user_id,
                concept_id=concept_id,
                concept_name=concept_name,
                skill_name=skill_name,
                p_knowledge=self.p_l0,
                status="unassessed",
                total_attempts=0
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)

        return rec

    def get_user_competencies(
        self,
        db: Session,
        user_id: int,
        career_name: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Returns full dictionary of concept competencies for user.
        Ensures all concepts in the target career exist in the output.
        """
        target_concept_ids = []
        if career_name:
            target_concept_ids = knowledge_graph.get_career_concepts(career_name)
        else:
            target_concept_ids = list(knowledge_graph.concepts.keys())

        records = db.query(LearnerCompetency).filter(
            LearnerCompetency.user_id == user_id
        ).all()
        rec_map = {r.concept_id: r for r in records}

        competencies = {}
        for cid in target_concept_ids:
            cdata = knowledge_graph.concepts.get(cid, {})
            if cid in rec_map:
                r = rec_map[cid]
                competencies[cid] = {
                    "concept_id": cid,
                    "concept_name": r.concept_name,
                    "skill_name": r.skill_name,
                    "p_knowledge": round(r.p_knowledge, 4),
                    "status": r.status,
                    "total_attempts": r.total_attempts,
                    "last_assessment_score": r.last_assessment_score
                }
            else:
                competencies[cid] = {
                    "concept_id": cid,
                    "concept_name": cdata.get("title", cid),
                    "skill_name": cdata.get("skill", "General"),
                    "p_knowledge": self.p_l0,
                    "status": "unassessed",
                    "total_attempts": 0,
                    "last_assessment_score": None
                }

        return competencies

    def record_quiz_assessment_and_update_bkt(
        self,
        db: Session,
        user_id: int,
        quiz_token: str,
        concept_id: str,
        question: str,
        options: Dict[str, str],
        correct_option: str,
        selected_option: str,
        explanation: str,
        difficulty: str = "intermediate"
    ) -> Tuple[QuizAttempt, LearnerCompetency]:
        """
        Evaluates quiz attempt server-side, guards against duplicate submissions,
        updates BKT estimate, and stores audit trail in database.
        """
        # Guard: check if quiz_token already evaluated to prevent duplicate BKT updates
        existing_attempt = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_token == quiz_token
        ).first()

        if existing_attempt:
            # Return existing attempt without double updating BKT
            comp = self.get_or_create_competency(db, user_id, concept_id)
            return existing_attempt, comp

        is_correct = (selected_option.strip().upper() == correct_option.strip().upper())

        # Retrieve current competency state
        comp = self.get_or_create_competency(db, user_id, concept_id)
        prior_p = comp.p_knowledge

        # Compute BKT update
        posterior_p = self.calculate_bkt_posterior(prior_p, is_correct)

        # Update competency record
        comp.p_knowledge = posterior_p
        comp.total_attempts += 1
        comp.last_assessment_score = 1.0 if is_correct else 0.0
        comp.status = self.determine_competency_status(posterior_p, comp.total_attempts)
        comp.updated_at = datetime.utcnow()

        # Create persistent quiz attempt record
        attempt = QuizAttempt(
            user_id=user_id,
            concept_id=concept_id,
            concept_name=comp.concept_name,
            quiz_token=quiz_token,
            question=question,
            options_json=options,
            correct_option=correct_option.strip().upper(),
            selected_option=selected_option.strip().upper(),
            is_correct=is_correct,
            explanation=explanation,
            difficulty=difficulty,
            bkt_prior=prior_p,
            bkt_posterior=posterior_p,
            attempted_at=datetime.utcnow()
        )

        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        db.refresh(comp)

        return attempt, comp

    def record_multi_quiz_assessment_and_update_bkt(
        self,
        db: Session,
        user_id: int,
        session_token: str,
        concept_id: str,
        submitted_answers: Dict[int, str],
        questions_list: List[Dict[str, Any]],
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Processes a multi-question quiz submission (3, 5, 8, 10 questions).
        Sequentially updates BKT for each question answered, creates persistent QuizAttempt rows,
        and returns a complete evaluation summary for the result view.
        """
        # Guard: check if any attempt for this session already exists
        first_token = f"{session_token}_1"
        existing_first = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_token == first_token
        ).first()

        comp = self.get_or_create_competency(db, user_id, concept_id)

        if existing_first:
            existing_attempts = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_token.like(f"{session_token}%")
            ).order_by(QuizAttempt.id.asc()).all()

            reviews = []
            correct_count = 0
            for a in existing_attempts:
                if a.is_correct:
                    correct_count += 1
                reviews.append({
                    "q_idx": len(reviews) + 1,
                    "question": a.question,
                    "options": a.options_json,
                    "user_choice": a.selected_option,
                    "correct_option": a.correct_option,
                    "is_correct": a.is_correct,
                    "explanation": a.explanation,
                    "bkt_prior": a.bkt_prior,
                    "bkt_posterior": a.bkt_posterior
                })

            total_q = len(reviews) or 1
            return {
                "session_token": session_token,
                "concept_id": concept_id,
                "concept_name": comp.concept_name,
                "total_questions": total_q,
                "correct_count": correct_count,
                "score_pct": round((correct_count / total_q) * 100, 1),
                "initial_bkt": existing_attempts[0].bkt_prior if existing_attempts else comp.p_knowledge,
                "final_bkt": existing_attempts[-1].bkt_posterior if existing_attempts else comp.p_knowledge,
                "competency_status": comp.status,
                "question_reviews": reviews,
                "first_attempt_id": existing_attempts[0].id if existing_attempts else 1
            }

        # Sequential BKT update across all submitted questions
        initial_bkt = comp.p_knowledge
        current_p = initial_bkt
        correct_count = 0
        reviews = []
        created_attempts = []

        for q in questions_list:
            q_idx = q["q_idx"]
            token = f"{session_token}_{q_idx}"
            user_choice = str(submitted_answers.get(q_idx, "")).strip().upper()
            correct_choice = str(q["correct_option"]).strip().upper()
            is_correct = (user_choice == correct_choice)
            if is_correct:
                correct_count += 1

            prior_p = current_p
            posterior_p = self.calculate_bkt_posterior(prior_p, is_correct)
            current_p = posterior_p

            attempt = QuizAttempt(
                user_id=user_id,
                concept_id=concept_id,
                concept_name=comp.concept_name,
                quiz_token=token,
                question=q["question"],
                options_json=q["options"],
                correct_option=correct_choice,
                selected_option=user_choice,
                is_correct=is_correct,
                explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", difficulty),
                bkt_prior=prior_p,
                bkt_posterior=posterior_p,
                attempted_at=datetime.utcnow()
            )
            db.add(attempt)
            created_attempts.append(attempt)

            reviews.append({
                "q_idx": q_idx,
                "question": q["question"],
                "options": q["options"],
                "user_choice": user_choice,
                "correct_option": correct_choice,
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
                "bkt_prior": prior_p,
                "bkt_posterior": posterior_p
            })

        total_q = len(questions_list) or 1
        comp.p_knowledge = current_p
        comp.total_attempts += total_q
        comp.last_assessment_score = round(correct_count / total_q, 4)
        comp.status = self.determine_competency_status(current_p, comp.total_attempts)
        comp.updated_at = datetime.utcnow()

        db.commit()
        for att in created_attempts:
            db.refresh(att)
        db.refresh(comp)

        return {
            "session_token": session_token,
            "concept_id": concept_id,
            "concept_name": comp.concept_name,
            "total_questions": total_q,
            "correct_count": correct_count,
            "score_pct": round((correct_count / total_q) * 100, 1),
            "initial_bkt": initial_bkt,
            "final_bkt": current_p,
            "competency_status": comp.status,
            "question_reviews": reviews,
            "first_attempt_id": created_attempts[0].id if created_attempts else 1
        }

competency_service = CompetencyService()

