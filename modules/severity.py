"""
Injury Severity Classifier (Rule-based)
FR5.1 – FR5.3
"""

import re

# ── Keyword → Severity rules ──────────────────────────────────────────────────
SEVERE_KEYWORDS = [
    "unconscious", "unresponsive", "head trauma", "traumatic brain", "tbi",
    "skull fracture", "internal bleeding", "haemorrhage", "hemorrhage",
    "cardiac arrest", "spinal injury", "spinal cord", "severe blood loss",
    "critical", "life-threatening", "fatal", "penetrating", "deep laceration",
    "multiple fractures", "severe burns", "burns", "crushed", "amputation",
]

MODERATE_KEYWORDS = [
    "fracture", "broken bone", "dislocation", "concussion", "moderate bleeding",
    "contusion", "whiplash", "head injury", "rib fracture", "blunt trauma",
    "soft tissue", "swelling", "bruising", "lacerations", "cut",
    "abdominal injury", "chest injury", "shoulder injury", "knee injury",
]

MINOR_KEYWORDS = [
    "minor cut", "minor scratch", "abrasion", "scrape", "bruise", "surface wound",
    "minor bruise", "minor swelling", "minor injury", "scratch", "redness",
    "grazing", "minor laceration",
]


def classify_severity(injury_text: str) -> str:
    """
    Classify severity from LLM injury description text.
    Returns: 'Severe' | 'Moderate' | 'Minor'
    """
    text_lower = injury_text.lower()

    for kw in SEVERE_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return "Severe"

    for kw in MODERATE_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return "Moderate"

    for kw in MINOR_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return "Minor"

    # Default to Moderate if detected injuries exist but no clear match
    return "Moderate"


def severity_to_color(severity: str) -> str:
    return {
        "Severe": "#ff4444",
        "Moderate": "#ffaa00",
        "Minor": "#00c851",
    }.get(severity, "#aaaaaa")


def severity_to_priority(severity: str) -> int:
    """Higher number = higher priority."""
    return {"Severe": 3, "Moderate": 2, "Minor": 1}.get(severity, 0)
