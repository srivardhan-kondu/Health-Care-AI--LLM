"""
Internal test for hospital filtering by location.
"""

from modules.hospital_filter import fetch_all_hospitals, filter_and_rank
from modules.distance import add_distances

# Test locations: (lat, lng, label)
locations = [
    (17.4033, 78.5591, "Uppal"),
    (17.4065, 78.5784, "Medipally"),
    (17.3985, 78.5360, "Habsiguda"),
    (17.4296, 78.6206, "Narapally"),
    (17.4802, 78.5681, "Anurag University"),
]

injury_type = "fracture"
severity = "Moderate"

def test_locations():
    hospitals = fetch_all_hospitals()
    for lat, lng, label in locations:
        hospitals_with_dist = add_distances(hospitals, lat, lng)
        ranked = filter_and_rank(hospitals_with_dist, injury_type, severity, top_n=6)
        print(f"\n--- {label} ({lat}, {lng}) ---")
        if not ranked:
            print("No hospitals found in 8-15 km radius.")
        for h in ranked:
            print(f"{h['name']} | {h['specialization']} | {h['distance_km']} km | Emergency: {h.get('emergency', False)}")

if __name__ == "__main__":
    test_locations()
