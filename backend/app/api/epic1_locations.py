"""Epic 1 nearby location API.

Provides endpoints for:
- searching nearby eco-shops by user coordinates
- retrieving place details by place_id

This module coordinates request validation and response formatting.
All raw Google API logic lives in services/maps_service.py.
"""

import logging

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas.location import NearbyResponse, PlaceDetails, PlaceResult
from app.services import maps_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/locations", tags=["Epic 1 — Locations"])


# ---------------------------------------------------------------------------
# Epic 1 Step 2:
# Search nearby second-hand/donation/recycling places and return sorted results.
# ---------------------------------------------------------------------------

@router.get("/nearby", response_model=NearbyResponse)
async def get_nearby_places(
    lat: float = Query(..., ge=-90, le=90, description="User latitude"),
    lng: float = Query(..., ge=-180, le=180, description="User longitude"),
    radius_km: float = Query(5.0, gt=0, le=50, description="Search radius in km"),
) -> NearbyResponse:
    """Return eco-shops within radius_km of the user, sorted by distance.

    Calls the Google Places Nearby Search API with multiple eco-shop keywords,
    deduplicates results, attaches Haversine distances, and sorts ascending.

    Args:
        lat:       User latitude in decimal degrees.
        lng:       User longitude in decimal degrees.
        radius_km: Search radius in kilometres (default 5, max 50).

    Returns:
        NearbyResponse with a list of PlaceResult objects and an optional
        guidance message when no results are found.

    Raises:
        HTTPException 503: When the Google Places API is unavailable or times out.
    """
    try:
        places = await maps_service.fetch_nearby_places(
            user_lat=lat,
            user_lng=lng,
            radius_km=radius_km,
        )
    except httpx.TimeoutException:
        logger.error(
            "Google Places API timed out for lat=%s lng=%s radius_km=%s",
            lat, lng, radius_km,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_timeout",
                "detail": "Google Places API did not respond in time. Please try again.",
            },
        )
    except (httpx.HTTPStatusError, RuntimeError) as exc:
        logger.error(
            "Google Places API error for lat=%s lng=%s: %s", lat, lng, exc
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_error",
                "detail": "Could not retrieve nearby places. Please try again later.",
            },
        )

    # Empty result is not an error — return 200 with guidance message per plan
    if not places:
        return NearbyResponse(
            results=[],
            message="No eco-shops found in this area. Try increasing the search radius.",
        )

    return NearbyResponse(
        results=[PlaceResult(**place) for place in places],
        message=None,
    )


# ---------------------------------------------------------------------------
# Epic 1 Step 4:
# Fetch full place details for a selected marker; return cached when available.
# ---------------------------------------------------------------------------

@router.get("/details/{place_id}", response_model=PlaceDetails)
async def get_place_details(place_id: str) -> PlaceDetails:
    """Return full details for a single eco-shop identified by place_id.

    Results are cached in Redis for 24 hours (place_details:{place_id}).
    Cache hit returns immediately without calling Google; cache miss fetches
    from Google, caches the normalised payload, then returns.

    Args:
        place_id: Google place_id string from a previous nearby search result.

    Returns:
        PlaceDetails with address, opening hours, phone, website, and type.

    Raises:
        HTTPException 404: When Google reports no result for the given place_id.
        HTTPException 503: When the Google Place Details API is unavailable.
    """
    try:
        details = await maps_service.get_place_details(place_id=place_id)
    except httpx.TimeoutException:
        logger.error("Google Place Details API timed out for place_id=%s", place_id)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_timeout",
                "detail": "Google Place Details API did not respond in time.",
            },
        )
    except RuntimeError as exc:
        error_str = str(exc)
        if "NOT_FOUND" in error_str or "INVALID_REQUEST" in error_str:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "place_not_found",
                    "detail": f"No place found for place_id: {place_id}",
                },
            )
        logger.error("Google Place Details error for place_id=%s: %s", place_id, exc)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_error",
                "detail": "Could not retrieve place details. Please try again later.",
            },
        )
    except httpx.HTTPStatusError as exc:
        logger.error(
            "HTTP error fetching details for place_id=%s: %s", place_id, exc
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_error",
                "detail": "Could not retrieve place details. Please try again later.",
            },
        )

    return PlaceDetails(**details)
