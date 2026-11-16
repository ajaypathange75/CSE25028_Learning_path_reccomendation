import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\.\-]+\.[a-zA-Z]{2,}$")

# ----------------- Auth Schemas -----------------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not EMAIL_REGEX.match(cleaned):
            raise ValueError("Invalid email address format")
        return cleaned

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Profile Schemas -----------------
class UserProfileBase(BaseModel):
    stream: str = "CSE"
    cgpa_range: str = "6–8"
    practical_preference: str = "Yes"
    logical_reasoning: str = "Good"
    problem_solving: str = "Good"
    programming_knowledge: str = "Intermediate"
    communication_skills: str = "Good"
    creativity_level: str = "Good"
    primary_interest: str = "Software and Technology"
    experience_level: str = "No experience"
    projects_completed: str = "None"
    certifications: str = "None"
    preferred_career_type: str = "Technical role"
    preferred_industry: str = "IT"
    preferred_work_environment: str = "Hybrid"
    career_goal: str = "Entry-level job"
    bio: Optional[str] = None

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileOut(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Career Assessment Schemas -----------------
class CareerAssessmentInput(BaseModel):
    # 5 Personality questions
    q1_party: str = Field(..., description="I am the life of the party.")
    q2_stressed: str = Field(..., description="I get stressed out easily.")
    q3_details: str = Field(..., description="I pay attention to details.")
    q4_sympathize: str = Field(..., description="I sympathize with others’ feelings.")
    q5_vocab: str = Field(..., description="I have a rich vocabulary.")
    
    # 3 Academic questions
    q6_cgpa: str = Field(..., description="What is your CGPA range?")
    q7_stream: str = Field(..., description="Which stream are you studying?")
    q8_practical: str = Field(..., description="Do you prefer practical assignments over theory?")
    
    # 5 Skill self-ratings
    q9_reasoning: str = Field(..., description="Rate your logical reasoning ability.")
    q10_problem_solving: str = Field(..., description="How do you rate your problem-solving skills.")
    q11_programming: str = Field(..., description="Rate your programming knowledge.")
    q12_communication: str = Field(..., description="How are your communication skills?")
    q13_creativity: str = Field(..., description="Rate your creativity level.")
    
    # 8 Profile & preference questions
    q14_interest: str = Field(..., description="Primary interest")
    q15_experience: str = Field(..., description="Experience level")
    q16_projects: str = Field(..., description="Projects completed")
    q17_certifications: str = Field(..., description="Certifications")
    q18_career_type: str = Field(..., description="Preferred career type")
    q19_industry: str = Field(..., description="Preferred industry")
    q20_work_env: str = Field(..., description="Preferred work environment")
    q21_career_goal: str = Field(..., description="Career goal")

class CareerPredictionOut(BaseModel):
    id: int
    predicted_career: str
    confidence_score: float
    probabilities: Dict[str, float]
    career_overview: str
    required_skills: List[str]
    relevant_concepts: List[str]
    learning_objectives: List[str]
    career_requirements: List[str]
    created_at: datetime

class CareerAcceptanceRequest(BaseModel):
    prediction_id: int
    decision: str = Field(..., pattern="^(accept|reject)$")

class AlternativeCareerSelectRequest(BaseModel):
    prediction_id: int
    selected_career: str

# ----------------- Competency & BKT Schemas -----------------
class CompetencyOut(BaseModel):
    concept_id: str
    concept_name: str
    skill_name: str
    p_knowledge: float
    status: str
    total_attempts: int

class BKTUpdateResult(BaseModel):
    concept_id: str
    is_correct: bool
    prior_p: float
    posterior_p: float
    new_status: str

# ----------------- Quiz Schemas -----------------
class QuizQuestionOut(BaseModel):
    quiz_token: str
    concept_id: str
    concept_name: str
    question: str
    options: Dict[str, str]  # 'A', 'B', 'C', 'D'
    difficulty: str
    learning_objective: str

class QuizSubmitRequest(BaseModel):
    quiz_token: str
    concept_id: str
    selected_option: str = Field(..., pattern="^[A-D]$")

class QuizEvaluationOut(BaseModel):
    quiz_token: str
    concept_id: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: str
    bkt_prior: float
    bkt_posterior: float
    new_status: str

# ----------------- Dashboard & Readiness Schemas -----------------
class CareerReadinessOut(BaseModel):
    readiness_percentage: float
    skills_completion_rate: float
    concepts_mastery_rate: float
    projects_completion_rate: float
    assessments_completion_rate: float
    formula_explanation: str
    disclaimer: str

class LearningActivityUpdate(BaseModel):
    activity_id: int
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")
    notes: Optional[str] = None

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    career_target: str
    submission_link: Optional[str] = None
