import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from app.config import settings

class PreprocessingService:
    def __init__(self, mapping_path: Path = None):
        self.mapping_path = mapping_path or settings.ENCODING_MAPPING_PATH
        self._load_mappings()

    def _load_mappings(self):
        """Loads the saved encoding mappings from the read-only JSON artifact."""
        if not self.mapping_path.exists():
            raise FileNotFoundError(
                f"Required encoding mapping artifact missing at {self.mapping_path}. "
                "Ensure dataset/career_path_encoding_mappings.json exists."
            )
        
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.feature_columns: List[str] = data["feature_columns"]
        self.target_column: str = data["target_column"]
        self.feature_mappings: Dict[str, Dict[str, int]] = data["feature_mappings"]
        self.target_mapping: Dict[str, int] = data["target_mapping"]
        
        # Build inverse target mapping: int -> career_name
        self.inverse_target_mapping: Dict[int, str] = {
            v: k for k, v in self.target_mapping.items()
        }

    def normalize_input_value(self, val: Any) -> str:
        """
        Normalizes unicode variations (like en-dash to hyphen or curly quotes)
        to maintain robustness while strictly matching mapping keys.
        """
        if not isinstance(val, str):
            return str(val)
        s = val.strip()
        # Normalize various dashes to standard or en-dash if needed
        # In the dataset mappings: "6–8", "8–10", "1–2 projects", "3–5 projects", "2–3 certifications" use U+2013 en-dash
        return s

    def validate_and_encode_response(self, raw_responses: Dict[str, Any]) -> Tuple[List[int], Dict[str, int]]:
        """
        Validates all 21 required features and encodes them using the saved mapping.
        
        Returns:
            Tuple of:
            - List of 21 integer feature values in exact training order
            - Dict of feature_name -> encoded_integer
        
        Raises:
            ValueError: if any required feature is missing or has an unseen categorical value.
        """
        encoded_dict = {}
        encoded_list = []

        # Check all required feature columns in exact order
        for col_name in self.feature_columns:
            if col_name not in raw_responses:
                raise ValueError(f"Missing required assessment feature: '{col_name}'")
            
            raw_val = self.normalize_input_value(raw_responses[col_name])
            mapping = self.feature_mappings.get(col_name)
            if not mapping:
                raise ValueError(f"No encoding mapping found for feature: '{col_name}'")
            
            # Exact match attempt
            if raw_val in mapping:
                encoded_val = mapping[raw_val]
            else:
                # Try normalization: replace hyphen with en-dash or vice-versa
                normalized_alt = raw_val.replace("-", "–").replace("'", "’")
                if normalized_alt in mapping:
                    encoded_val = mapping[normalized_alt]
                else:
                    alt2 = raw_val.replace("–", "-").replace("’", "'")
                    if alt2 in mapping:
                        encoded_val = mapping[alt2]
                    else:
                        valid_options = list(mapping.keys())
                        raise ValueError(
                            f"Unseen categorical value '{raw_val}' for feature '{col_name}'. "
                            f"Expected one of: {valid_options}"
                        )
            
            encoded_dict[col_name] = encoded_val
            encoded_list.append(encoded_val)

        if len(encoded_list) != len(self.feature_columns):
            raise ValueError(
                f"Feature vector length mismatch. Expected {len(self.feature_columns)}, got {len(encoded_list)}"
            )

        return encoded_list, encoded_dict

    def decode_target(self, target_id: int) -> str:
        """Decodes integer target prediction into career title."""
        if target_id not in self.inverse_target_mapping:
            raise ValueError(f"Unknown target class id {target_id}. Supported: {list(self.inverse_target_mapping.keys())}")
        return self.inverse_target_mapping[target_id]

    def get_supported_careers(self) -> List[str]:
        """Returns sorted list of all 11 supported careers."""
        return [self.inverse_target_mapping[i] for i in sorted(self.inverse_target_mapping.keys())]

preprocessing_service = PreprocessingService()
