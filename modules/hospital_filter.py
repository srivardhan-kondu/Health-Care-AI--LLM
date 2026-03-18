"""
Hospital Filter & Ranking Module
FR9.1 – FR9.2, FR11.1 – FR11.3
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DB_PATH

# ── Injury type → required specialization mapping ─────────────────────────────
INJURY_SPECIALIZATION_MAP = {
    # Head / Brain
    "head injury": ["Neurology", "Trauma Care", "Emergency"],
    "head trauma": ["Neurology", "Trauma Care", "Emergency"],
    "skull fracture": ["Neurology", "Trauma Care"],
    "brain": ["Neurology", "Trauma Care"],
    "concussion": ["Neurology", "Trauma Care", "Emergency"],

    # Fracture / Bone
    "fracture": ["Orthopedic", "Trauma Care"],
    "bone fracture": ["Orthopedic", "Trauma Care"],
    "broken bone": ["Orthopedic", "Trauma Care"],
    "arm fracture": ["Orthopedic"],
    "leg fracture": ["Orthopedic"],
    "rib fracture": ["Orthopedic", "Trauma Care"],
    "dislocation": ["Orthopedic"],

    # Bleeding / Trauma
    "external bleeding": ["Emergency", "Trauma Care"],
    "internal bleeding": ["Trauma Care", "Emergency"],
    "hemorrhage": ["Trauma Care", "Emergency"],
    "body trauma": ["Trauma Care", "Emergency"],
    "blunt trauma": ["Trauma Care", "Emergency"],

    # Minor
    "minor cut": ["Emergency"],
    "abrasion": ["Emergency"],
    "scratch": ["Emergency"],
    "bruise": ["Emergency"],
    "wound": ["Emergency", "Trauma Care"],

    # Default
    "": ["Emergency", "Trauma Care", "Orthopedic", "Neurology"],
}


def _get_preferred_specs(injury_type: str) -> list:
    """Return ordered list of preferred specializations for the detected injury."""
    injury_lower = injury_type.lower().strip()
    for key, specs in INJURY_SPECIALIZATION_MAP.items():
        if key and key in injury_lower:
            return specs
    return INJURY_SPECIALIZATION_MAP[""]


def fetch_all_hospitals() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospitals")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def filter_and_rank(
    hospitals: list,
    injury_type: str,
    severity: str,
    top_n: int = 6,
) -> list:
    """
    Filter hospitals by injury type specialization and rank by:
      1. Preferred specialization match
      2. Emergency availability (for Severe/Moderate)
      3. Distance (ascending)
    """
    preferred_specs = _get_preferred_specs(injury_type)

    def score(h):
        spec_score = 0
        for i, spec in enumerate(preferred_specs):
            if h["specialization"].lower() == spec.lower():
                spec_score = len(preferred_specs) - i  # Higher match = higher score
                break

        emergency_score = 1 if h.get("emergency") and severity in ("Severe", "Moderate") else 0
        distance_score = -h.get("distance_km", 9999)  # Closer = higher score

        return (spec_score, emergency_score, distance_score)

    # Show top N hospitals, sorted by score (specialization, emergency, distance)
    ranked = sorted(hospitals, key=score, reverse=True)[:top_n]
    # Always sort final list by distance_km ascending for user clarity
    ranked = sorted(ranked, key=lambda h: h.get("distance_km", 9999))
    return ranked
