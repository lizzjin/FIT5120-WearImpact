"""Epic 1 Pydantic schemas for the Local Eco-Shop Navigator.

Single source of truth for all request and response field names and types.
Used by epic1_locations.py (request validation + response serialization).
"""

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Nearby search — response
# ---------------------------------------------------------------------------

class PlaceResult(BaseModel):
    """A single eco-shop entry returned in the nearby search response."""

    place_id: str
    name: str
    # Possible values: "second_hand_shop" | "donation_point" | "recycling"
    type: str
    lat: float
    lng: float
    distance_km: float


class NearbyResponse(BaseModel):
    """Full response body for GET /api/locations/nearby."""

    results: list[PlaceResult]
    # Populated only when results is empty — guides the user to widen their search
    message: str | None = None


# ---------------------------------------------------------------------------
# Place details — response
# ---------------------------------------------------------------------------

class PlaceDetails(BaseModel):
    """Full place details returned by GET /api/locations/details/{place_id}."""

    place_id: str
    name: str
    address: str
    # e.g. ["Monday: 9:00 AM – 5:00 PM", ...]  — empty list when unavailable
    opening_hours: list[str]
    phone: str | None = None
    website: str | None = None
    type: str
