from typing import Dict, List, Set, Any, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import QuizAttempt, UserProject, LearningActivity
from app.services.knowledge_graph import knowledge_graph
from app.services.competency_service import competency_service

class LearningPathService:
    """
    Adaptive Learning Path, Prerequisite Reasoning, Skill Gap Analysis,
    and Career Readiness Service.
    """

    def analyze_skill_gaps(
        self,
        db: Session,
        user_id: int,
        target_career: str
    ) -> Dict[str, Any]:
        """
        Stage 13 & 24: Skill Gap Analysis.
        Compares target career requirements against the learner's recorded competencies.
        """
        competencies = competency_service.get_user_competencies(db, user_id, target_career)
        career_skills = knowledge_graph.get_career_skills(target_career)
        career_concepts = knowledge_graph.get_career_concepts(target_career)

        mastered_concepts = []
        developing_concepts = []
        weak_concepts = []
        unassessed_concepts = []

        for cid in career_concepts:
            c_info = competencies.get(cid, {})
            status = c_info.get("status", "unassessed")
            concept_title = c_info.get("concept_name", cid)
            p_val = c_info.get("p_knowledge", 0.20)

            item = {
                "concept_id": cid,
                "title": concept_title,
                "skill": c_info.get("skill_name", ""),
                "p_knowledge": p_val,
                "status": status
            }

            if status == "mastered":
                mastered_concepts.append(item)
            elif status == "developing":
                developing_concepts.append(item)
            elif status == "weak":
                weak_concepts.append(item)
            else:
                unassessed_concepts.append(item)

        # Missing skills analysis: A skill is partially missing if not all its concepts are mastered,
        # or completely missing if none are mastered.
        skill_breakdown = []
        for s_name in career_skills:
            s_cids = knowledge_graph.get_skill_concepts(s_name)
            s_mastered = [cid for cid in s_cids if competencies.get(cid, {}).get("status") == "mastered"]
            skill_breakdown.append({
                "skill_name": s_name,
                "total_concepts": len(s_cids),
                "mastered_concepts": len(s_mastered),
                "is_fully_mastered": len(s_mastered) == len(s_cids) and len(s_cids) > 0
            })

        return {
            "target_career": target_career,
            "total_required_concepts": len(career_concepts),
            "mastered_concepts": mastered_concepts,
            "developing_concepts": developing_concepts,
            "weak_concepts": weak_concepts,
            "unassessed_concepts": unassessed_concepts,
            "skills_breakdown": skill_breakdown,
            "missing_concepts_count": len(weak_concepts) + len(unassessed_concepts) + len(developing_concepts)
        }

    def generate_personalized_learning_path(
        self,
        db: Session,
        user_id: int,
        target_career: str
    ) -> List[Dict[str, Any]]:
        """
        Stage 14, 15, & 25: Prerequisite-aware Adaptive Learning Path Generation.
        Ranks concepts needing study, ensures prerequisites are scheduled first,
        and provides rationales for priorities.
        """
        competencies = competency_service.get_user_competencies(db, user_id, target_career)
        career_concepts = knowledge_graph.get_career_concepts(target_career)

        # Set of mastered concept IDs
        mastered_set = {
            cid for cid, info in competencies.items() if info.get("status") == "mastered"
        }

        # Candidate concepts that still need mastery
        candidates = [
            cid for cid in career_concepts
            if competencies.get(cid, {}).get("status") != "mastered"
        ]

        # Topologically sort the candidates to preserve strict prerequisite order
        ordered_candidates = knowledge_graph.topological_sort_concepts(candidates)

        learning_path = []
        for rank, cid in enumerate(ordered_candidates, start=1):
            c_meta = knowledge_graph.concepts.get(cid, {})
            user_comp = competencies.get(cid, {})
            prereqs = knowledge_graph.get_prerequisites(cid)
            prereqs_satisfied = knowledge_graph.are_prerequisites_satisfied(cid, mastered_set)

            # Assign priority:
            # 1 (Highest): Prerequisites are satisfied and concept is weak or unassessed
            # 2 (Medium): Prerequisites satisfied and concept is developing
            # 3 (Blocked): Prerequisites are not yet satisfied
            if prereqs_satisfied:
                if user_comp.get("status") in ("weak", "unassessed"):
                    priority_level = "High"
                    reason = "Immediate prerequisite for advanced topics; ready to study now."
                else:
                    priority_level = "Medium"
                    reason = "In-progress concept requiring reinforcement to reach full mastery."
            else:
                priority_level = "Prerequisite Blocked"
                unsatisfied = [p for p in prereqs if p not in mastered_set]
                unsatisfied_names = [knowledge_graph.concepts.get(p, {}).get("title", p) for p in unsatisfied]
                reason = f"Pending prerequisite completion: {', '.join(unsatisfied_names)}"

            learning_path.append({
                "sequence_order": rank,
                "concept_id": cid,
                "title": c_meta.get("title", cid),
                "skill_name": c_meta.get("skill", ""),
                "current_status": user_comp.get("status", "unassessed"),
                "p_knowledge": user_comp.get("p_knowledge", 0.20),
                "priority": priority_level,
                "prerequisites_satisfied": prereqs_satisfied,
                "prerequisites": [knowledge_graph.concepts.get(p, {}).get("title", p) for p in prereqs],
                "expected_outcome": f"Achieve mastery in {c_meta.get('title', cid)} through structured theory and quiz validation.",
                "reason": reason
            })

        return learning_path

    def generate_career_roadmap(
        self,
        db: Session,
        user_id: int,
        target_career: str
    ) -> Dict[str, Any]:
        """
        Stage 16: Structured 6-Tier Career Roadmap.
        - Foundation
        - Intermediate
        - Advanced
        - Projects
        - Practice Activities
        - Career Preparation
        """
        learning_path = self.generate_personalized_learning_path(db, user_id, target_career)
        career_meta = knowledge_graph.careers.get(target_career, {})

        # Partition ordered learning path into tiers
        total_items = len(learning_path)
        third = max(1, total_items // 3)

        foundation = learning_path[:third]
        intermediate = learning_path[third: 2 * third]
        advanced = learning_path[2 * third:]

        # Projects for this career
        career_projects = [
            p for p in knowledge_graph.projects.values() if p.get("career") == target_career
        ]

        # Career Preparation items
        career_prep = [
            {
                "title": "Technical Resume & Portfolio Audit",
                "description": f"Tailor your project highlights and skill endorsements specifically for {target_career} job specifications."
            },
            {
                "title": "Mock Technical & Domain Interview",
                "description": "Engage in scenario-based question drills focusing on system design and quantitative problem-solving."
            },
            {
                "title": "Industry Capstone Showcase",
                "description": "Publish a comprehensive project repository demonstrating clean code, CI/CD, and documentation."
            }
        ]

        return {
            "career_name": target_career,
            "overview": career_meta.get("overview", ""),
            "stages": [
                {"stage_name": "Foundation Level", "modules": foundation, "items": foundation},
                {"stage_name": "Intermediate Level", "modules": intermediate, "items": intermediate},
                {"stage_name": "Advanced Specialization", "modules": advanced, "items": advanced},
                {"stage_name": "Practical Capstone Projects", "modules": career_projects, "items": career_projects},
                {"stage_name": "Skill Validations & Quizzes", "modules": [
                    {"title": "Daily Concept Quiz Verification", "description": "Validate retention via adaptive AI-generated MCQs with BKT tracking."},
                    {"title": "Hands-on Code & Case Studies", "description": "Implement practical mini-assignments for active learning."}
                ], "items": [
                    {"title": "Daily Concept Quiz Verification", "description": "Validate retention via adaptive AI-generated MCQs with BKT tracking."},
                    {"title": "Hands-on Code & Case Studies", "description": "Implement practical mini-assignments for active learning."}
                ]},
                {"stage_name": "Career Preparation", "modules": career_prep, "items": career_prep}
            ]
        }

    def get_recommended_next_activity(
        self,
        db: Session,
        user_id: int,
        target_career: str
    ) -> Optional[Dict[str, Any]]:
        """
        Stage 25: Returns the single top-priority, prerequisite-cleared next activity.
        """
        path = self.generate_personalized_learning_path(db, user_id, target_career)
        for item in path:
            if item["prerequisites_satisfied"] and item["current_status"] != "mastered":
                return item
        return None

    def calculate_career_readiness(
        self,
        db: Session,
        user_id: int,
        target_career: str
    ) -> Dict[str, Any]:
        """
        Stage 27: Career Readiness Tracking.
        
        Transparent Formula:
        - W_skills (35%): Fraction of required skills where at least one concept is mastered.
        - W_concepts (35%): Average knowledge probability across all career concepts.
        - W_projects (15%): Completed user projects against a recommended baseline of 2.
        - W_assessments (15%): Percentage of quiz attempts answered correctly (min 5 attempts to reach 100%).
        
        Total Readiness % = (0.35 * S) + (0.35 * C) + (0.15 * P) + (0.15 * A)
        """
        competencies = competency_service.get_user_competencies(db, user_id, target_career)
        career_skills = knowledge_graph.get_career_skills(target_career)
        career_concepts = knowledge_graph.get_career_concepts(target_career)

        # 1. Skills completion rate
        mastered_skill_count = 0
        for skill in career_skills:
            cids = knowledge_graph.get_skill_concepts(skill)
            if any(competencies.get(cid, {}).get("status") == "mastered" for cid in cids):
                mastered_skill_count += 1
        skills_rate = (mastered_skill_count / len(career_skills)) if career_skills else 0.0

        # 2. Concept mastery rate (average p_knowledge)
        concept_p_sum = sum(competencies.get(cid, {}).get("p_knowledge", 0.0) for cid in career_concepts)
        concepts_rate = (concept_p_sum / len(career_concepts)) if career_concepts else 0.0

        # 3. Projects rate
        completed_projects = db.query(UserProject).filter(
            UserProject.user_id == user_id,
            UserProject.status == "completed"
        ).count()
        projects_rate = min(1.0, completed_projects / 2.0)

        # 4. Assessment accuracy & activity
        attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
        if attempts:
            correct_count = sum(1 for a in attempts if a.is_correct)
            assessment_acc = correct_count / len(attempts)
            volume_multiplier = min(1.0, len(attempts) / 5.0)
            assessments_rate = assessment_acc * volume_multiplier
        else:
            assessments_rate = 0.0

        # Weighted calculation
        total_readiness = (
            (0.35 * skills_rate) +
            (0.35 * concepts_rate) +
            (0.15 * projects_rate) +
            (0.15 * assessments_rate)
        ) * 100.0

        total_readiness = round(max(0.0, min(100.0, total_readiness)), 1)

        explanation = (
            "Readiness Score Formula: "
            "35% Skills Breadth (fraction of skills with mastered concepts) + "
            "35% Concept Mastery (BKT knowledge probabilities) + "
            "15% Capstone Projects Completed + "
            "15% Quiz Assessment Track Record."
        )

        disclaimer = (
            "Notice: The Career Readiness Score is an academic progress metric reflecting curriculum "
            "mastery and practice milestones. It does not represent a commercial employment prediction or guarantee."
        )

        return {
            "readiness_percentage": total_readiness,
            "skills_completion_rate": round(skills_rate * 100, 1),
            "concepts_mastery_rate": round(concepts_rate * 100, 1),
            "projects_completion_rate": round(projects_rate * 100, 1),
            "assessments_completion_rate": round(assessments_rate * 100, 1),
            "completed_projects_count": completed_projects,
            "total_assessments_count": len(attempts),
            "formula_explanation": explanation,
            "disclaimer": disclaimer
        }

learning_path_service = LearningPathService()
