from pydantic import BaseModel, Field, field_validator
from typing import Any

class ClaimAnalysisResult(BaseModel):
    evidence_standard_met: bool
    evidence_standard_met_reason: str
    risk_flags: str = "none"
    issue_type: str = "unknown"
    object_part: str = "unknown"
    claim_status: str = "not_enough_information"
    claim_status_justification: str
    supporting_image_ids: str = "none"
    valid_image: bool
    severity: str = "unknown"

    @field_validator('evidence_standard_met', 'valid_image', mode='before')
    @classmethod
    def validate_bool(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            val = v.strip().lower()
            if val in ("true", "1", "yes"):
                return True
            if val in ("false", "0", "no"):
                return False
        return False

    @field_validator('risk_flags', mode='before')
    @classmethod
    def validate_risk_flags(cls, v: Any) -> str:
        allowed = {
            "blurry_image", "cropped_or_obstructed", "low_light_or_glare", "wrong_angle",
            "wrong_object", "wrong_object_part", "damage_not_visible", "claim_mismatch",
            "possible_manipulation", "non_original_image", "text_instruction_present",
            "user_history_risk", "manual_review_required"
        }
        if not isinstance(v, str) or not v.strip():
            return "none"
        
        parts = [p.strip().lower() for p in v.split(";") if p.strip()]
        valid_parts = [p for p in parts if p in allowed]
        
        if not valid_parts:
            return "none"
        return ";".join(valid_parts)

    @field_validator('issue_type', mode='before')
    @classmethod
    def validate_issue_type(cls, v: Any) -> str:
        allowed = {
            "dent", "scratch", "crack", "glass_shatter", "broken_part", "missing_part",
            "torn_packaging", "crushed_packaging", "water_damage", "stain", "none", "unknown"
        }
        if isinstance(v, str):
            val = v.strip().lower()
            if val in allowed:
                return val
        return "unknown"

    @field_validator('severity', mode='before')
    @classmethod
    def validate_severity(cls, v: Any) -> str:
        allowed = {"none", "low", "medium", "high", "unknown"}
        if isinstance(v, str):
            val = v.strip().lower()
            if val in allowed:
                return val
        return "unknown"

    @field_validator('claim_status', mode='before')
    @classmethod
    def validate_claim_status(cls, v: Any) -> str:
        allowed = {"supported", "contradicted", "not_enough_information"}
        if isinstance(v, str):
            val = v.strip().lower()
            if val in allowed:
                return val
        return "not_enough_information"

    @field_validator('object_part', mode='before')
    @classmethod
    def validate_object_part(cls, v: Any) -> str:
        allowed = {
            # car
            "front_bumper", "rear_bumper", "door", "hood", "windshield", "side_mirror", 
            "headlight", "taillight", "fender", "quarter_panel", "body",
            # laptop
            "screen", "keyboard", "trackpad", "hinge", "lid", "corner", "port", "base",
            # package
            "box", "package_corner", "package_side", "seal", "label", "contents", "item",
            # default
            "unknown"
        }
        if isinstance(v, str):
            val = v.strip().lower()
            # Clean up potential prefixing or spacing
            val = val.replace(" ", "_")
            if val in allowed:
                return val
        return "unknown"

    @field_validator('supporting_image_ids', mode='before')
    @classmethod
    def validate_supporting_image_ids(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            return "none"
        return v.strip()
