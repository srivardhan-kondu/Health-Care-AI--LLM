"""
Route: POST /hospitals
Accepts user GPS coordinates + injury info, returns ranked hospital list.
FR7.3, FR9.1 – FR11.3
"""

from flask import Blueprint, request, jsonify

hospitals_bp = Blueprint("hospitals", __name__)


@hospitals_bp.route("/hospitals", methods=["POST"])
def get_hospitals():
    from modules.hospital_filter import fetch_all_hospitals, filter_and_rank
    from modules.distance import add_distances

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    lat = data.get("lat")
    lng = data.get("lng")
    injury_type = data.get("injury_type", "")
    severity = data.get("severity", "Moderate")

    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinates"}), 400

    hospitals = fetch_all_hospitals()
    hospitals = add_distances(hospitals, lat, lng)
    ranked = filter_and_rank(hospitals, injury_type, severity, top_n=6)

    return jsonify({"hospitals": ranked, "count": len(ranked)}), 200
