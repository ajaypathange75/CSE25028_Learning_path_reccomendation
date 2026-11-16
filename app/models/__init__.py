from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    assessments = relationship("AssessmentResponse", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("CareerPrediction", back_populates="user", cascade="all, delete-orphan")
    career_selections = relationship("UserCareerSelection", back_populates="user", cascade="all, delete-orphan")
    competencies = relationship("LearnerCompetency", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("LearningActivity", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("UserProject", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Academic & Background
    stream = Column(String(64), default="CSE")
    cgpa_range = Column(String(32), default="6–8")
    practical_preference = Column(String(32), default="Yes")
    
    # Skills self-rating
    logical_reasoning = Column(String(32), default="Good")
    problem_solving = Column(String(32), default="Good")
    programming_knowledge = Column(String(32), default="Intermediate")
    communication_skills = Column(String(32), default="Good")
    creativity_level = Column(String(32), default="Good")
    
    # Interests & Experience
    primary_interest = Column(String(64), default="Software and Technology")
    experience_level = Column(String(64), default="No experience")
    projects_completed = Column(String(64), default="None")
    certifications = Column(String(64), default="None")
    
    # Career preferences
    preferred_career_type = Column(String(64), default="Technical role")
    preferred_industry = Column(String(64), default="IT")
    preferred_work_environment = Column(String(64), default="Hybrid")
    career_goal = Column(String(64), default="Entry-level job")
    
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    responses_json = Column(JSON, nullable=False)  # Dictionary of all 21 feature questions and answers
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="assessments")
    prediction = relationship("CareerPrediction", back_populates="assessment", uselist=False, cascade="all, delete-orphan")


class CareerPrediction(Base):
    __tablename__ = "career_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessment_responses.id", ondelete="CASCADE"), nullable=False)
    predicted_career = Column(String(128), nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    probabilities_json = Column(JSON, nullable=True)  # Dict: career_name -> probability
    is_accepted = Column(Boolean, nullable=True)  # True = accepted, False = rejected, None = pending decision
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="predictions")
    assessment = relationship("AssessmentResponse", back_populates="prediction")
    selections = relationship("UserCareerSelection", back_populates="prediction")


class UserCareerSelection(Base):
    __tablename__ = "user_career_selections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("career_predictions.id", ondelete="SET NULL"), nullable=True)
    selected_career = Column(String(128), nullable=False)
    selection_type = Column(String(64), default="predicted_accepted")  # 'predicted_accepted' or 'alternative_selected'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="career_selections")
    prediction = relationship("CareerPrediction", back_populates="selections")


class LearnerCompetency(Base):
    __tablename__ = "learner_competencies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(64), nullable=False, index=True)
    concept_name = Column(String(128), nullable=False)
    skill_name = Column(String(128), nullable=False)
    p_knowledge = Column(Float, default=0.20)  # P(L) in BKT: [0.0, 1.0]
    status = Column(String(32), default="unassessed")  # 'unassessed', 'weak', 'developing', 'mastered'
    last_assessment_score = Column(Float, nullable=True)
    total_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="competencies")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(64), nullable=False, index=True)
    concept_name = Column(String(128), nullable=True)
    quiz_token = Column(String(64), index=True, nullable=False)  # To avoid duplicate submissions
    question = Column(Text, nullable=False)
    options_json = Column(JSON, nullable=False)  # Dict: {'A': ..., 'B': ..., 'C': ..., 'D': ...}
    correct_option = Column(String(8), nullable=False)
    selected_option = Column(String(8), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(32), default="intermediate")
    bkt_prior = Column(Float, nullable=False)
    bkt_posterior = Column(Float, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="quiz_attempts")


class LearningActivity(Base):
    __tablename__ = "learning_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(64), nullable=False, index=True)
    activity_type = Column(String(32), default="study")  # 'study', 'project', 'practice'
    title = Column(String(256), nullable=False)
    resource_url = Column(String(512), nullable=True)
    status = Column(String(32), default="pending")  # 'pending', 'in_progress', 'completed'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="activities")


class UserProject(Base):
    __tablename__ = "user_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    career_target = Column(String(128), nullable=False)
    status = Column(String(32), default="in_progress")  # 'in_progress', 'completed'
    submission_link = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="projects")
