"""
Haversine Distance Calculator
FR10.1 – FR10.4
"""

import math


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (km).
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


def add_distances(hospitals: list, user_lat: float, user_lon: float) -> list:
    """
    Attach distance_km to each hospital dict.
    """
    for h in hospitals:
        h["distance_km"] = haversine(user_lat, user_lon, h["latitude"], h["longitude"])
    return hospitals
