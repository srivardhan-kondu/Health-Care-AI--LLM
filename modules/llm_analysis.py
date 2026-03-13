"""
LLM Analysis Module — GPT-4o Vision
FR4.1 – FR4.5
"""

import base64
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OPENAI_API_KEY

try:
    from openai import OpenAI
    _client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    _client = None


SYSTEM_PROMPT = """You are a medical AI assistant specializing in accident and trauma analysis.
Analyze the provided accident/injury image and respond ONLY with a valid JSON object.

Required JSON format:
{
  "injuries": [
    {
      "type": "<injury type, e.g. Head Trauma, Arm Fracture, External Bleeding>",
      "description": "<brief clinical description>",
      "body_part": "<affected body part>"
    }
  ],
  "overall_description": "<one sentence summary of visible injuries>",
  "confidence": <0.0 to 1.0>,
  "requires_emergency": <true or false>
}

Rules:
- Be medically accurate but conservative.
- If no injuries are visible, return an empty injuries array.
- Do NOT include markdown, code fences, or extra text — only valid JSON.
"""


def _encode_image(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_mime_type(image_path: str) -> str:
    ext = image_path.rsplit(".", 1)[-1].lower()
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext, "image/jpeg")


def analyze_image(image_path: str) -> dict:
    """
    Send image to GPT-4o Vision and return structured injury analysis.
    Returns a dict with keys: injuries, overall_description, confidence, requires_emergency
    """
    if not _client:
        # ── Demo / fallback mode (no API key) ──────────────────────────────
        return _demo_response()

    base64_image = _encode_image(image_path)
    mime_type = _get_mime_type(image_path)

    try:
        response = _client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": "Analyze this accident scene image and return the JSON response.",
                        },
                    ],
                },
            ],
            max_tokens=600,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip("` \n")

        result = json.loads(raw)
        return _validate_result(result)

    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON", **_demo_response()}
    except Exception as e:
        return {"error": str(e), **_demo_response()}


def _validate_result(data: dict) -> dict:
    """Ensure all required keys exist."""
    return {
        "injuries": data.get("injuries", []),
        "overall_description": data.get("overall_description", "Injury analysis complete."),
        "confidence": float(data.get("confidence", 0.75)),
        "requires_emergency": bool(data.get("requires_emergency", False)),
    }


def _demo_response() -> dict:
    """Fallback response when no API key is set."""
    return {
        "injuries": [
            {
                "type": "External Bleeding",
                "description": "Visible surface wound with moderate bleeding on the arm.",
                "body_part": "Arm",
            },
            {
                "type": "Body Trauma",
                "description": "Signs of blunt force trauma to the torso area.",
                "body_part": "Torso",
            },
        ],
        "overall_description": "Demo mode: Moderate injuries detected including external bleeding and body trauma.",
        "confidence": 0.82,
        "requires_emergency": True,
        "_demo": True,
    }
