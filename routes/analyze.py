"""
Route: POST /analyze
Accepts an uploaded accident image, runs LLM analysis, classifies severity.
FR4.1 – FR6.3
"""

import os
import uuid
from flask import Blueprint, request, jsonify

analyze_bp = Blueprint("analyze", __name__)


def _allowed_file(filename: str) -> bool:
    allowed = {"jpg", "jpeg", "png"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    from config import UPLOAD_FOLDER
    from modules.llm_analysis import analyze_image
    from modules.severity import classify_severity

    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format. Use JPG, JPEG, or PNG."}), 400

    # Save uploaded file with unique name
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    # LLM analysis
    analysis = analyze_image(save_path)

    if "error" in analysis and not analysis.get("injuries"):
        return jsonify({"error": analysis["error"]}), 500

    # Determine primary injury type (first injury or overall description)
    injuries = analysis.get("injuries", [])
    primary_injury_type = injuries[0]["type"] if injuries else "Unknown"
    combined_text = " ".join(
        [inj.get("type", "") + " " + inj.get("description", "") for inj in injuries]
    )

    # Classify severity
    severity = classify_severity(combined_text or primary_injury_type)

    return jsonify({
        "image_filename": unique_name,
        "injuries": injuries,
        "overall_description": analysis.get("overall_description", ""),
        "primary_injury_type": primary_injury_type,
        "severity": severity,
        "confidence": analysis.get("confidence", 0),
        "requires_emergency": analysis.get("requires_emergency", False),
        "demo_mode": analysis.get("_demo", False),
    }), 200
