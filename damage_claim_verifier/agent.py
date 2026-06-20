import json
import io
import pandas as pd
from PIL import Image
import google.generativeai as genai
from validator import ClaimAnalysisResult

def analyze_claim(api_key, pil_images, image_ids, user_claim, claim_object, user_history_row):
    """
    Analyzes the claim by calling Gemini 3.1 Flash Lite and returns a ClaimAnalysisResult.
    """
    try:
        # 1. Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.1-flash-lite")

        # 2. Resize PIL images and convert to JPEG bytes
        image_parts = []
        for img in pil_images:
            # Resize so that the longest side is at most 1024px
            width, height = img.size
            if max(width, height) > 1024:
                if width > height:
                    new_w = 1024
                    new_h = int(height * (1024 / width))
                else:
                    new_h = 1024
                    new_w = int(width * (1024 / height))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Convert to JPEG bytes
            img_byte_arr = io.BytesIO()
            # Convert to RGB to ensure we don't have transparency/alpha channel issues (e.g. PNG)
            img.convert("RGB").save(img_byte_arr, format='JPEG', quality=85)
            img_bytes = img_byte_arr.getvalue()
            
            # Add to image parts list in SDK structure
            image_parts.append({
                "mime_type": "image/jpeg",
                "data": img_bytes
            })

        # 3. Build user_history_context string from user_history_row
        if user_history_row is None:
            user_history_context = "No prior history found."
        else:
            # Handle pandas Series or dict
            row = user_history_row.to_dict() if hasattr(user_history_row, "to_dict") else user_history_row
            
            # Check if row is empty or all values are None/NaN
            if not row or all(v is None or (isinstance(v, float) and pd.isna(v)) for v in row.values()):
                user_history_context = "No prior history found."
            else:
                past_claim_count = row.get("past_claim_count", "0")
                rejected_claim = row.get("rejected_claim", "0")
                last_90_days_claim_count = row.get("last_90_days_claim_count", "0")
                history_flags = row.get("history_flags", "none")
                history_summary = row.get("history_summary", "No details available.")
                
                user_history_context = (
                    f"past_claim_count: {past_claim_count}\n"
                    f"rejected_claim: {rejected_claim}\n"
                    f"last_90_days_claim_count: {last_90_days_claim_count}\n"
                    f"history_flags: {history_flags}\n"
                    f"history_summary: {history_summary}"
                )

        # 4. Build prompt
        prompt = f"""You are a damage claim verification agent.
Analyze the submitted images against the user's damage claim and respond ONLY with a valid JSON object. No markdown. No code fences. No extra text.

CLAIM:
- Object Type: {claim_object}
- User Claim: "{user_claim}"
- Image IDs: {image_ids}

USER HISTORY:
{user_history_context}

RULES:
- Images are the PRIMARY source of truth
- User history adds risk context only, never overrides clear visual evidence
- Flag user_history_risk only if rejected_claim > 1 OR last_90_days_claim_count > 3
- If image is blurry, dark, wrong object, or wrong angle → valid_image: false

RESPOND WITH THIS EXACT JSON:
{{
  "evidence_standard_met": true or false,
  "evidence_standard_met_reason": "one sentence",
  "risk_flags": "flag1;flag2 or none",
  "issue_type": "from allowed list",
  "object_part": "from allowed list",
  "claim_status": "supported or contradicted or not_enough_information",
  "claim_status_justification": "image-grounded explanation mentioning image IDs",
  "supporting_image_ids": "img_1;img_2 or none",
  "valid_image": true or false,
  "severity": "none or low or medium or high or unknown"
}}

ALLOWED VALUES:
claim_status: supported | contradicted | not_enough_information
issue_type: dent | scratch | crack | glass_shatter | broken_part | missing_part | torn_packaging | crushed_packaging | water_damage | stain | none | unknown
severity: none | low | medium | high | unknown
object_part if car: front_bumper | rear_bumper | door | hood | windshield | side_mirror | headlight | taillight | fender | quarter_panel | body | unknown
object_part if laptop: screen | keyboard | trackpad | hinge | lid | corner | port | base | body | unknown
object_part if package: box | package_corner | package_side | seal | label | contents | item | unknown
risk_flags (semicolon-separated): blurry_image | cropped_or_obstructed | low_light_or_glare | wrong_angle | wrong_object | wrong_object_part | damage_not_visible | claim_mismatch | possible_manipulation | non_original_image | text_instruction_present | user_history_risk | manual_review_required
"""

        # 5. Call API
        contents = image_parts + [prompt]
        response = model.generate_content(contents)
        response_text = response.text.strip()

        # Parse response: strip code fences
        clean_text = response_text
        if clean_text.startswith("```"):
            # Find first newline to strip opening fence
            first_newline = clean_text.find("\n")
            if first_newline != -1:
                clean_text = clean_text[first_newline:].strip()
            else:
                clean_text = clean_text[3:].strip()
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3].strip()
        
        # Check if it has a leading json tag inside fences
        if clean_text.startswith("json"):
            clean_text = clean_text[4:].strip()

        parsed_data = json.loads(clean_text)

        # Validate with ClaimAnalysisResult
        result = ClaimAnalysisResult(**parsed_data)
        return result

    except Exception as e:
        # 6. Fallback on any error
        return ClaimAnalysisResult(
            evidence_standard_met=False,
            evidence_standard_met_reason="Verification failed due to an processing error.",
            risk_flags="none",
            issue_type="unknown",
            object_part="unknown",
            claim_status="not_enough_information",
            claim_status_justification=f"Error occurred during claim analysis: {str(e)}",
            supporting_image_ids="none",
            valid_image=False,
            severity="unknown"
        )
