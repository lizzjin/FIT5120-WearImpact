"""Epic 1 geospatial calculation service.

Provides pure, deterministic distance functions used by the nearby search
to sort eco-shop results without making any paid Distance Matrix API calls.
Referenced in: maps_service.py (sort_places_by_distance).
"""

import math

# Mean radius of the Earth used in Haversine calculations
EARTH_RADIUS_KM = 6371.0


def haversine_km(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> float:
    """Compute straight-line distance between two coordinates in kilometres.

    Uses the Haversine formula, which accounts for Earth's curvature and
    provides accuracy within ~0.5% for the distances relevant to this app
    (up to 50 km).

    Used by Epic 1 nearby search results for distance-based sorting.
    No API call is made — this replaces the paid Distance Matrix call in Step 2.

    Args:
        origin_lat: Latitude of the starting point in decimal degrees.
        origin_lng: Longitude of the starting point in decimal degrees.
        dest_lat:   Latitude of the destination in decimal degrees.
        dest_lng:   Longitude of the destination in decimal degrees.

    Returns:
        Straight-line distance in kilometres, rounded to 2 decimal places.
    """
    # Convert all four coordinates from degrees to radians
    lat1 = math.radians(origin_lat)
    lng1 = math.radians(origin_lng)
    lat2 = math.radians(dest_lat)
    lng2 = math.radians(dest_lng)

    delta_lat = lat2 - lat1
    delta_lng = lng2 - lng1

    # Haversine formula: a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlng/2)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
    )
    central_angle = 2 * math.asin(math.sqrt(a))

    return round(EARTH_RADIUS_KM * central_angle, 2)


def sort_places_by_distance(places: list[dict]) -> list[dict]:
    """Sort a list of place dicts by their distance_km field ascending.

    Used after Haversine distances are attached to each place record so
    the nearest eco-shop appears first in the API response.

    Args:
        places: List of place dicts, each containing a 'distance_km' float.

    Returns:
        New list sorted by distance_km ascending (original list unchanged).
    """
    return sorted(places, key=lambda place: place["distance_km"])
