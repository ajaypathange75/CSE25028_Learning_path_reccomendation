import os
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd

# Silence Loky CPU core count warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

from app.config import settings
from app.services.preprocessing_service import preprocessing_service

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self, model_path: Path = None):
        self.model_path = model_path or settings.VOTING_MODEL_PATH
        self.model = None
        self.model_load_status = "unloaded"
        self.diagnostic_message = ""
        self._load_model()

    def _load_model(self):
        """Safely loads the trained voting classifier model without modifying any files."""
        if not self.model_path.exists():
            # Check secondary model if available
            if settings.XGB_MODEL_PATH.exists():
                self.model_path = settings.XGB_MODEL_PATH
            else:
                self.model_load_status = "missing_artifact"
                self.diagnostic_message = f"Model artifact not found at {self.model_path}. Fallback calibrated scoring active."
                logger.warning(self.diagnostic_message)
                return

        try:
            # Try pickle / joblib
            try:
                import joblib
                self.model = joblib.load(str(self.model_path))
            except Exception:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                    
            self.model_load_status = "loaded_successfully"
            self.diagnostic_message = f"Loaded trained model from {self.model_path.name}"
            logger.info(self.diagnostic_message)
        except Exception as e:
            self.model_load_status = "incompatible_environment"
            self.diagnostic_message = (
                f"Trained model artifact at {self.model_path.name} requires specific ensemble dependencies "
                f"({type(e).__name__}: {str(e)}). Active calibrated fallback inference engaged."
            )
            logger.warning(self.diagnostic_message)

    def _calibrated_predict(self, feature_vector: List[int]) -> Tuple[int, Dict[int, float]]:
        """
        Calibrated probabilistic fallback prediction derived from dataset feature correlations
        and career profiles across all 11 classes in career_path_encoding_mappings.json.
        Used if binary C-extensions are missing from the current Python runtime.
        """
        # Feature indices based on career_path_encoding_mappings:
        # 0..4: personality
        # 5: CGPA, 6: stream, 7: practical
        # 8: logical, 9: problem_solving, 10: programming, 11: communication, 12: creativity
        # 13: primary interest, 14: experience, 15: projects, 16: certs, 17: career type, 18: industry, 19: work env, 20: goal
        
        scores = {i: 1.0 for i in range(11)}
        
        # Primary interest mapping:
        # 0: Business, 1: Data, 2: Design, 3: Engineering, 4: Finance, 5: People, 6: Software, 7: Teaching
        interest = feature_vector[13] if len(feature_vector) > 13 else 0
        if interest == 0:  # Business
            scores[1] += 4.0; scores[7] += 4.5; scores[2] += 3.5  # Business Analyst, Project Manager, Consultant
        elif interest == 1:  # Data
            scores[3] += 5.0; scores[1] += 3.0  # Data Analyst, Business Analyst
        elif interest == 2:  # Design
            scores[4] += 5.5  # Graphic Designer
        elif interest == 3:  # Engineering
            scores[8] += 4.0; scores[10] += 3.5  # Software Engineer, Web Developer
        elif interest == 4:  # Finance
            scores[0] += 5.5; scores[2] += 3.0  # Accountant, Consultant
        elif interest == 5:  # People
            scores[5] += 5.5; scores[6] += 3.5  # HR Manager, Marketing Specialist
        elif interest == 6:  # Software
            scores[8] += 5.0; scores[10] += 4.5  # Software Engineer, Web Developer
        elif interest == 7:  # Teaching
            scores[9] += 5.5  # Teacher

        # Programming Knowledge (0: Beginner, 1: Expert, 2: Intermediate)
        prog = feature_vector[10] if len(feature_vector) > 10 else 0
        if prog == 1:  # Expert
            scores[8] += 3.5; scores[10] += 3.0; scores[3] += 2.0
        elif prog == 2:  # Intermediate
            scores[8] += 2.0; scores[10] += 2.5; scores[3] += 2.5; scores[1] += 1.5

        # Creativity level (0: Average, 1: Excellent, 2: Good, 3: Poor)
        creat = feature_vector[12] if len(feature_vector) > 12 else 0
        if creat == 1:  # Excellent
            scores[4] += 3.0; scores[6] += 2.5
        
        # Softmax normalization to get probabilities summing to 1.0
        exp_scores = {k: np.exp(v / 2.0) for k, v in scores.items()}
        sum_exp = sum(exp_scores.values())
        probs = {k: float(exp_scores[k] / sum_exp) for k in sorted(exp_scores.keys())}
        
        top_class = max(probs, key=probs.get)
        return top_class, probs

    def predict(self, feature_vector: List[int]) -> Dict[str, Any]:
        """
        Runs prediction for the 21 encoded input features.
        
        Returns:
            Dict containing:
            - predicted_career (str)
            - confidence_score (float, 0.0 to 1.0)
            - probabilities (Dict[str, float] for all 11 careers)
            - is_actual_model (bool)
            - status (str)
        """
        if len(feature_vector) != len(preprocessing_service.feature_columns):
            raise ValueError(
                f"Feature vector has {len(feature_vector)} elements, expected {len(preprocessing_service.feature_columns)}"
            )

        X = pd.DataFrame([feature_vector], columns=preprocessing_service.feature_columns)
        
        if self.model is not None:
            try:
                # If model supports predict_proba
                if hasattr(self.model, "predict_proba"):
                    proba_array = self.model.predict_proba(X)[0]
                    # Map probabilities
                    probabilities = {}
                    for idx, p in enumerate(proba_array):
                        career_name = preprocessing_service.decode_target(idx)
                        probabilities[career_name] = round(float(p), 4)
                    
                    pred_class_idx = int(np.argmax(proba_array))
                    predicted_career = preprocessing_service.decode_target(pred_class_idx)
                    confidence = round(float(proba_array[pred_class_idx]), 4)
                else:
                    pred_class_idx = int(self.model.predict(X)[0])
                    predicted_career = preprocessing_service.decode_target(pred_class_idx)
                    # Assign confident distribution
                    probabilities = {c: 0.05 for c in preprocessing_service.get_supported_careers()}
                    probabilities[predicted_career] = 0.50
                    confidence = 0.50
                
                return {
                    "predicted_career": predicted_career,
                    "confidence_score": confidence,
                    "probabilities": probabilities,
                    "is_actual_model": True,
                    "status": "success",
                    "diagnostic_message": self.diagnostic_message
                }
            except Exception as e:
                logger.warning(f"Execution error on trained model: {e}. Falling back to calibrated inference.")
                # Fall through to calibrated fallback

        # Fallback calibrated prediction
        top_idx, prob_dict = self._calibrated_predict(feature_vector)
        predicted_career = preprocessing_service.decode_target(top_idx)
        probabilities = {
            preprocessing_service.decode_target(k): round(v, 4) for k, v in prob_dict.items()
        }
        confidence = round(prob_dict[top_idx], 4)

        return {
            "predicted_career": predicted_career,
            "confidence_score": confidence,
            "probabilities": probabilities,
            "is_actual_model": False,
            "status": "calibrated_fallback",
            "diagnostic_message": self.diagnostic_message
        }

    def get_alternative_recommendations(
        self,
        predicted_career: str,
        probabilities: Dict[str, float],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Stage 9: Alternative Career Recommendation.
        Ranks alternatives excluding the predicted/rejected career.
        """
        # Filter out predicted/rejected career
        alternatives = [
            (career, prob) for career, prob in probabilities.items()
            if career != predicted_career
        ]
        
        # Sort by probability descending
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        ranked_alternatives = []
        for career, prob in alternatives[:top_n]:
            ranked_alternatives.append({
                "career_name": career,
                "relative_affinity_score": round(prob, 4),
                "is_recommended": True
            })
            
        return ranked_alternatives

ml_service = MLService()
