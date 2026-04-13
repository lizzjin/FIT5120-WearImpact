"""Google Maps service for Epic 1 location discovery.

Encapsulates all Google Places API calls so the API layer (epic1_locations.py)
stays framework-focused and free of raw HTTP logic.

Flow:
  Step 2 — fetch_nearby_places()  → Nearby Search API + Haversine sort
  Step 4 — get_place_details()    → Place Details API + Redis cache
"""

import json
import logging
from typing import Any

import httpx
import redis.asyncio as aioredis

from app.core.config import settings
from app.services.geo_service import haversine_km, sort_places_by_distance

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Google Places API constants
# ---------------------------------------------------------------------------

PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Detail fields requested from Google — only ask for what we expose to avoid
# extra billing on fields we discard.
PLACE_DETAILS_FIELDS = (
    "place_id,name,formatted_address,opening_hours,formatted_phone_number,website,types"
)

# Keywords sent to Nearby Search to maximise op-shop coverage in Australia.
ECO_SHOP_KEYWORDS = [
    "op shop",
    "charity shop",
    "clothing donation",
    "clothing recycling",
    "Salvos",
    "Vinnies",
    "Red Cross",
]

# Place type labels used as the 'type' field in API responses
ECO_PLACE_TYPE_SECOND_HAND = "second_hand_shop"
ECO_PLACE_TYPE_DONATION = "donation_point"
ECO_PLACE_TYPE_RECYCLING = "recycling"

# Google place types that are incompatible with eco-shops.
# If a result carries any of these types it is excluded from results,
# even if a keyword happened to match it through a review or description.
INCOMPATIBLE_GOOGLE_TYPES = {
    "grocery_or_supermarket",
    "supermarket",
    "convenience_store",
    "shopping_mall",
    "department_store",
    "restaurant",
    "food",
    "cafe",
    "bar",
    "bakery",
    "meal_delivery",
    "meal_takeaway",
    "lodging",
    "hospital",
    "health",
    "doctor",
    "dentist",
    "physiotherapist",
    "school",
    "gym",
    "pharmacy",
    "gas_station",
    "bank",
    "atm",
    "hair_care",
    "beauty_salon",
    "spa",
    "electronics_store",
    "hardware_store",
    "furniture_store",
    "car_dealer",
    "car_repair",
    "real_estate_agency",
    "insurance_agency",
    "accounting",
    "lawyer",
}

# Well-known Australian retail/grocery chains that can appear via keyword noise.
# Matched as a substring of the lowercased place name.
NON_ECO_NAME_BLOCKLIST = (
    "woolworths",
    "coles",
    "aldi",
    "iga ",
    "7-eleven",
    "7 eleven",
    "kmart",
    "target",
    "big w",
    "bunnings",
    "officeworks",
    "jb hi-fi",
    "chemist warehouse",
    "super centre",
    "supercenter",
    "shopping centre",
    "shopping center",
    "shopping mall",
    " plaza",
    "central plaza",
    "town centre",
    "town center",
    "westfield",
    "chadstone",
    "myer",
    "david jones",
    "harvey norman",
    "the good guys",
    "blood",
    "plasma",
    "lifeblood",
    "red cross blood",
    "pathology",
    "medical centre",
    "medical center",
    "health centre",
    "health center",
    "clinic",
    "hospital",
    "dental",
    "physio",
    "optometrist",
    "veterinary",
    "vet clinic",
)


# ---------------------------------------------------------------------------
# Redis client — injected at startup from main.py
# ---------------------------------------------------------------------------

_redis_client: aioredis.Redis | None = None


def set_redis_client(client: aioredis.Redis) -> None:
    """Inject the shared Redis client at application startup.

    Args:
        client: An initialised async Redis client from main.py lifespan.
    """
    global _redis_client
    _redis_client = client


def get_redis_client() -> aioredis.Redis | None:
    """Return the current Redis client, or None if not initialised."""
    return _redis_client


# ---------------------------------------------------------------------------
# Place type classification
# ---------------------------------------------------------------------------

def is_eco_place(name: str, google_types: list[str]) -> bool:
    """Return True only if the place is plausibly an eco-shop.

    Filters out places that Google's keyword search surfaced via review noise
    (e.g. a supermarket whose review mentions 'op shop nearby').

    Args:
        name:         Place name as returned by Google Places.
        google_types: List of Google place type strings for this place.

    Returns:
        False if the place carries an incompatible Google type or matches a
        known non-eco retail chain name; True otherwise.
    """
    # Reject if any Google-assigned type is on the incompatible list
    if any(t in INCOMPATIBLE_GOOGLE_TYPES for t in google_types):
        return False

    # Reject well-known non-eco retail chains matched by keyword noise
    name_lower = name.lower()
    if any(chain in name_lower for chain in NON_ECO_NAME_BLOCKLIST):
        return False

    return True


def classify_place_type(name: str, google_types: list[str]) -> str:
    """Classify a Google place into one of three Epic 1 eco-place categories.

    Classification order: recycling → donation → second_hand_shop (fallback).

    Args:
        name:         Place name as returned by Google Places.
        google_types: List of Google place type strings (e.g. ['store', 'point_of_interest']).

    Returns:
        One of: "recycling" | "donation_point" | "second_hand_shop".
    """
    name_lower = name.lower()

    # Detect recycling centres first — most specific category
    if any(term in name_lower for term in ("recycl", "textile", "fabric")):
        return ECO_PLACE_TYPE_RECYCLING

    # Detect donation points — charity organisations that accept donations
    if any(
        term in name_lower
        for term in ("donation", "salvos", "vinnies", "red cross", "goodwill", "charity")
    ):
        return ECO_PLACE_TYPE_DONATION

    # Everything else is treated as a second-hand / thrift shop
    return ECO_PLACE_TYPE_SECOND_HAND


# ---------------------------------------------------------------------------
# Response normalisation
# ---------------------------------------------------------------------------

def normalize_place_result(
    raw_place: dict[str, Any],
    user_lat: float,
    user_lng: float,
) -> dict[str, Any]:
    """Convert a raw Google Places Nearby Search result into an Epic 1 record.

    Extracts only the fields the API contract requires and attaches the
    Haversine distance from the user's location.

    Args:
        raw_place: A single place dict from the Google Nearby Search response.
        user_lat:  User latitude used for distance calculation.
        user_lng:  User longitude used for distance calculation.

    Returns:
        Dict matching the PlaceResult schema:
        {place_id, name, type, lat, lng, distance_km}.
    """
    location = raw_place.get("geometry", {}).get("location", {})
    place_lat: float = location.get("lat", 0.0)
    place_lng: float = location.get("lng", 0.0)

    # Use straight-line distance here to avoid paid matrix API calls in Step 2.
    distance_km = haversine_km(user_lat, user_lng, place_lat, place_lng)

    return {
        "place_id": raw_place.get("place_id", ""),
        "name": raw_place.get("name", ""),
        "type": classify_place_type(
            raw_place.get("name", ""),
            raw_place.get("types", []),
        ),
        "lat": place_lat,
        "lng": place_lng,
        "distance_km": distance_km,
    }


def normalize_place_details(raw_result: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw Google Place Details result into an Epic 1 PlaceDetails record.

    Args:
        raw_result: The 'result' dict from a Google Place Details API response.

    Returns:
        Dict matching the PlaceDetails schema:
        {place_id, name, address, opening_hours, phone, website, type}.
    """
    raw_hours: list[str] = (
        raw_result.get("opening_hours", {}).get("weekday_text", [])
    )

    return {
        "place_id": raw_result.get("place_id", ""),
        "name": raw_result.get("name", ""),
        "address": raw_result.get("formatted_address", ""),
        "opening_hours": raw_hours,
        "phone": raw_result.get("formatted_phone_number") or None,
        "website": raw_result.get("website") or None,
        "type": classify_place_type(
            raw_result.get("name", ""),
            raw_result.get("types", []),
        ),
    }


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

async def fetch_nearby_places(
    user_lat: float,
    user_lng: float,
    radius_km: float,
) -> list[dict[str, Any]]:
    """Fetch nearby eco-related places and return normalised, distance-sorted records.

    Performs one Nearby Search per keyword against the Google Places API,
    deduplicates results by place_id, attaches Haversine distances, then
    returns the combined list sorted by distance ascending.

    Step 2 uses Nearby Search + Haversine to minimise API cost and latency.
    No Distance Matrix call is made here.

    Args:
        user_lat:  User latitude in decimal degrees.
        user_lng:  User longitude in decimal degrees.
        radius_km: Search radius in kilometres (converted to metres for Google).

    Returns:
        List of place dicts (PlaceResult shape), sorted by distance_km ascending.

    Raises:
        httpx.TimeoutException: Propagated so the endpoint can return 503.
        RuntimeError:           On unexpected Google API error status.
    """
    radius_metres = int(radius_km * 1000)
    seen_place_ids: set[str] = set()
    all_places: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=settings.google_places_timeout_seconds) as client:
        for keyword in ECO_SHOP_KEYWORDS:
            params = {
                "location": f"{user_lat},{user_lng}",
                "radius": radius_metres,
                "keyword": keyword,
                "key": settings.google_maps_api_key,
            }
            response = await client.get(PLACES_NEARBY_URL, params=params)
            response.raise_for_status()
            payload = response.json()

            api_status = payload.get("status", "")
            if api_status not in ("OK", "ZERO_RESULTS"):
                logger.error(
                    "Google Places Nearby Search error: status=%s keyword=%s",
                    api_status,
                    keyword,
                )
                raise RuntimeError(f"Google Places API returned status: {api_status}")

            for raw_place in payload.get("results", []):
                place_id = raw_place.get("place_id", "")
                # Deduplicate — multiple keywords can return the same place
                if place_id and place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    # Filter out non-eco places that appeared via keyword noise
                    # (e.g. supermarkets whose reviews mention 'op shop')
                    google_types = raw_place.get("types", [])
                    place_name = raw_place.get("name", "")
                    if not is_eco_place(place_name, google_types):
                        logger.debug(
                            "Excluded non-eco place: name=%s types=%s",
                            place_name,
                            google_types,
                        )
                        continue
                    all_places.append(
                        normalize_place_result(raw_place, user_lat, user_lng)
                    )

    return sort_places_by_distance(all_places)


async def get_place_details(place_id: str) -> dict[str, Any]:
    """Fetch full place details, using Redis cache to avoid redundant API calls.

    Cache strategy (Epic 1 Step 4):
      Cache hit  → return cached payload directly (no Google API call)
      Cache miss → call Google Place Details API, normalise, cache, return

    Args:
        place_id: Google place_id string identifying the location.

    Returns:
        Dict matching the PlaceDetails schema.

    Raises:
        httpx.TimeoutException: Propagated so the endpoint can return 503.
        RuntimeError:           On unexpected Google API error status.
    """
    # Cache key format is fixed and versioned so future schema changes can be
    # handled by incrementing the prefix (e.g. place_details_v2:{place_id}).
    cache_key = f"place_details:{place_id}"

    redis = get_redis_client()
    if redis is not None:
        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.debug("Cache hit for place_id=%s", place_id)
                return json.loads(cached)
        except Exception as exc:
            # Cache read failure should not block the request — degrade gracefully
            logger.warning("Redis read failed for key=%s: %s", cache_key, exc)

    # Cache miss — fetch from Google Place Details API
    logger.debug("Cache miss for place_id=%s — calling Google API", place_id)
    async with httpx.AsyncClient(timeout=settings.google_places_timeout_seconds) as client:
        params = {
            "place_id": place_id,
            "fields": PLACE_DETAILS_FIELDS,
            "key": settings.google_maps_api_key,
        }
        response = await client.get(PLACE_DETAILS_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    api_status = payload.get("status", "")
    if api_status != "OK":
        logger.error(
            "Google Place Details error: status=%s place_id=%s", api_status, place_id
        )
        raise RuntimeError(f"Google Place Details API returned status: {api_status}")

    details = normalize_place_details(payload.get("result", {}))

    if redis is not None:
        try:
            await redis.setex(
                cache_key,
                settings.place_details_cache_ttl,
                json.dumps(details),
            )
            logger.debug(
                "Cached place_id=%s for %d seconds",
                place_id,
                settings.place_details_cache_ttl,
            )
        except Exception as exc:
            # Cache write failure should not fail the response
            logger.warning("Redis write failed for key=%s: %s", cache_key, exc)

    return details
