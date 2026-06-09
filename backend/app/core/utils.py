import json
import re
from typing import Any, Dict
from app.core.logging import get_logger
from app.services.ai.exceptions import AIGenerationError

logger = get_logger(__name__)

def parse_ai_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract and parse JSON from AI response text.
    
    Handles markdown code blocks and leading/trailing conversational text.
    """
    # Remove markdown code blocks if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    
    # Find the first '{' and the last '}'
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    
    if start_idx == -1 or end_idx == -1:
        logger.error(f"No JSON object found in AI response: {text[:200]}...")
        raise AIGenerationError("AI response did not contain a valid JSON object")
        
    json_str = text[start_idx : end_idx + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode AI JSON: {json_str}")
        raise AIGenerationError(f"AI response was not valid JSON: {str(e)}")
