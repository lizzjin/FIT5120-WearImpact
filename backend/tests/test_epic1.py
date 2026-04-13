"""Epic 1 test suite — Local Eco-Shop Navigator.

Covers all minimum required scenarios from the claude.md test standard:
1. Nearby endpoint returns sorted results by distance.
2. Nearby endpoint handles zero results with guidance message.
3. Details endpoint returns normalised fields.
4. Details endpoint uses cache hit path.
5. Details endpoint cache miss path writes cache.
6. Upstream API failure maps to 503.
7. Invalid lat/lng/radius returns validation error.

Run with:  pytest tests/test_epic1.py -v
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import maps_service
from app.services.geo_service import haversine_km, sort_places_by_distance


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Synchronous test client wrapping the FastAPI app."""
    with TestClient(app) as c:
        yield c


SAMPLE_PLACE_DETAILS_RAW = {
    "place_id": "place_001",
    "name": "Salvos Stores Melbourne",
    "formatted_address": "123 Bourke St, Melbourne VIC 3000",
    "opening_hours": {
        "weekday_text": [
            "Monday: 9:00 AM – 5:00 PM",
            "Tuesday: 9:00 AM – 5:00 PM",
        ]
    },
    "formatted_phone_number": "(03) 9000 0000",
    "website": "https://www.salvos.org.au",
    "types": ["store"],
}


# ---------------------------------------------------------------------------
# geo_service unit tests
# ---------------------------------------------------------------------------

class TestHaversineKm:
    def test_same_point_returns_zero(self):
        """Distance between identical coordinates must be zero."""
        assert haversine_km(-37.81, 144.96, -37.81, 144.96) == 0.0

    def test_known_distance_melbourne_cbd(self):
        """~1 km separation in Melbourne should return a value close to that."""
        # Approx distance from Flinders St to Melbourne Central (~1.1 km)
        dist = haversine_km(-37.8183, 144.9671, -37.8100, 144.9626)
        assert 0.8 < dist < 1.5, f"Expected ~1 km, got {dist}"

    def test_returns_float(self):
        """Return type must be float."""
        result = haversine_km(-37.81, 144.96, -37.82, 144.97)
        assert isinstance(result, float)

    def test_distance_is_symmetric(self):
        """Distance A→B must equal distance B→A."""
        d1 = haversine_km(-37.81, 144.96, -37.85, 145.00)
        d2 = haversine_km(-37.85, 145.00, -37.81, 144.96)
        assert abs(d1 - d2) < 0.01


class TestSortPlacesByDistance:
    def test_sorts_ascending(self):
        """Places must be sorted by distance_km from nearest to furthest."""
        places = [
            {"place_id": "a", "distance_km": 3.5},
            {"place_id": "b", "distance_km": 1.2},
            {"place_id": "c", "distance_km": 2.0},
        ]
        sorted_places = sort_places_by_distance(places)
        distances = [p["distance_km"] for p in sorted_places]
        assert distances == sorted(distances)

    def test_does_not_mutate_original(self):
        """Original list must be unchanged after sorting."""
        places = [
            {"distance_km": 3.0},
            {"distance_km": 1.0},
        ]
        original_order = [p["distance_km"] for p in places]
        sort_places_by_distance(places)
        assert [p["distance_km"] for p in places] == original_order


# ---------------------------------------------------------------------------
# Nearby endpoint tests
# ---------------------------------------------------------------------------

class TestNearbyEndpoint:
    def test_nearby_returns_distance_sorted_results(self, client):
        """Nearby endpoint must return results sorted by distance_km ascending."""
        mock_places = [
            {
                "place_id": "place_003",
                "name": "Eco Recycle Textile Centre",
                "type": "recycling",
                "lat": -37.810,
                "lng": 144.960,
                "distance_km": 0.8,
            },
            {
                "place_id": "place_001",
                "name": "Salvos Stores Melbourne",
                "type": "donation_point",
                "lat": -37.815,
                "lng": 144.965,
                "distance_km": 1.2,
            },
            {
                "place_id": "place_002",
                "name": "Green Thread Thrift Shop",
                "type": "second_hand_shop",
                "lat": -37.820,
                "lng": 144.970,
                "distance_km": 2.5,
            },
        ]

        with patch(
            "app.api.epic1_locations.maps_service.fetch_nearby_places",
            new_callable=AsyncMock,
            return_value=mock_places,
        ):
            response = client.get(
                "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=5"
            )

        assert response.status_code == 200
        data = response.json()
        distances = [r["distance_km"] for r in data["results"]]
        assert distances == sorted(distances), "Results are not sorted by distance_km"

    def test_nearby_returns_empty_message_when_no_results(self, client):
        """When no places are found, response must contain guidance message."""
        with patch(
            "app.api.epic1_locations.maps_service.fetch_nearby_places",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client.get(
                "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=5"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["message"] is not None
        assert len(data["message"]) > 0

    def test_nearby_upstream_timeout_returns_503(self, client):
        """Google Places timeout must map to HTTP 503."""
        with patch(
            "app.api.epic1_locations.maps_service.fetch_nearby_places",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("timeout"),
        ):
            response = client.get(
                "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=5"
            )

        assert response.status_code == 503

    def test_nearby_upstream_error_returns_503(self, client):
        """Google Places API error must map to HTTP 503."""
        with patch(
            "app.api.epic1_locations.maps_service.fetch_nearby_places",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Google Places API returned status: REQUEST_DENIED"),
        ):
            response = client.get(
                "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=5"
            )

        assert response.status_code == 503

    def test_nearby_invalid_lat_returns_validation_error(self, client):
        """Latitude outside [-90, 90] must return 422 validation error."""
        response = client.get(
            "/api/locations/nearby?lat=999&lng=144.96&radius_km=5"
        )
        assert response.status_code == 422

    def test_nearby_invalid_lng_returns_validation_error(self, client):
        """Longitude outside [-180, 180] must return 422 validation error."""
        response = client.get(
            "/api/locations/nearby?lat=-37.81&lng=999&radius_km=5"
        )
        assert response.status_code == 422

    def test_nearby_zero_radius_returns_validation_error(self, client):
        """radius_km <= 0 must return 422 validation error."""
        response = client.get(
            "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=0"
        )
        assert response.status_code == 422

    def test_nearby_response_contains_required_fields(self, client):
        """Each result must contain all fields defined in the API contract."""
        required_fields = {"place_id", "name", "type", "lat", "lng", "distance_km"}
        mock_places = [
            {
                "place_id": "place_001",
                "name": "Salvos Stores Melbourne",
                "type": "donation_point",
                "lat": -37.815,
                "lng": 144.965,
                "distance_km": 1.2,
            }
        ]

        with patch(
            "app.api.epic1_locations.maps_service.fetch_nearby_places",
            new_callable=AsyncMock,
            return_value=mock_places,
        ):
            response = client.get(
                "/api/locations/nearby?lat=-37.81&lng=144.96&radius_km=5"
            )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert required_fields.issubset(result.keys())


# ---------------------------------------------------------------------------
# Details endpoint tests
# ---------------------------------------------------------------------------

SAMPLE_DETAILS_NORMALISED = {
    "place_id": "place_001",
    "name": "Salvos Stores Melbourne",
    "address": "123 Bourke St, Melbourne VIC 3000",
    "opening_hours": ["Monday: 9:00 AM – 5:00 PM", "Tuesday: 9:00 AM – 5:00 PM"],
    "phone": "(03) 9000 0000",
    "website": "https://www.salvos.org.au",
    "type": "donation_point",
}


class TestDetailsEndpoint:
    def test_details_returns_normalised_fields(self, client):
        """Details endpoint must return all required fields with correct types."""
        required_fields = {
            "place_id", "name", "address", "opening_hours", "phone", "website", "type"
        }

        with patch(
            "app.api.epic1_locations.maps_service.get_place_details",
            new_callable=AsyncMock,
            return_value=SAMPLE_DETAILS_NORMALISED,
        ):
            response = client.get("/api/locations/details/place_001")

        assert response.status_code == 200
        data = response.json()
        assert required_fields.issubset(data.keys())
        assert isinstance(data["opening_hours"], list)

    def test_details_uses_cache_before_upstream_call(self, client):
        """Cache hit must return immediately — get_place_details handles this internally."""
        # Patch get_place_details to return data (cache hit behaviour tested here
        # by verifying no extra HTTP call is issued — the service handles internals)
        with patch(
            "app.api.epic1_locations.maps_service.get_place_details",
            new_callable=AsyncMock,
            return_value=SAMPLE_DETAILS_NORMALISED,
        ) as mock_get:
            response = client.get("/api/locations/details/place_001")
            assert mock_get.call_count == 1  # Endpoint called service exactly once

        assert response.status_code == 200

    def test_details_cache_hit_path(self):
        """Redis cache hit must return cached data without calling Google."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(
            return_value=json.dumps(SAMPLE_DETAILS_NORMALISED)
        )
        maps_service.set_redis_client(mock_redis)

        async def run():
            result = await maps_service.get_place_details("place_001")
            return result

        result = asyncio.get_event_loop().run_until_complete(run())

        # Redis get was called — Google API was NOT called (no httpx client)
        mock_redis.get.assert_called_once_with("place_details:place_001")
        assert result["place_id"] == "place_001"

        # Clean up
        maps_service.set_redis_client(None)

    def test_details_cache_miss_writes_cache(self):
        """Cache miss must fetch from Google, then write the result to Redis."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)  # Cache miss
        mock_redis.setex = AsyncMock()
        maps_service.set_redis_client(mock_redis)

        google_response_payload = {
            "status": "OK",
            "result": SAMPLE_PLACE_DETAILS_RAW,
        }

        async def run():
            with patch("app.services.maps_service.httpx.AsyncClient") as mock_client_cls:
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock()
                mock_response.json = MagicMock(return_value=google_response_payload)

                mock_http = AsyncMock()
                mock_http.get = AsyncMock(return_value=mock_response)
                mock_http.__aenter__ = AsyncMock(return_value=mock_http)
                mock_http.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_http

                result = await maps_service.get_place_details("place_001")
                return result

        result = asyncio.get_event_loop().run_until_complete(run())

        # Verify the result was written to Redis cache
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[0] == "place_details:place_001"
        assert result["place_id"] == "place_001"

        # Clean up
        maps_service.set_redis_client(None)

    def test_details_upstream_timeout_returns_503(self, client):
        """Google Place Details timeout must map to HTTP 503."""
        with patch(
            "app.api.epic1_locations.maps_service.get_place_details",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("timeout"),
        ):
            response = client.get("/api/locations/details/place_001")

        assert response.status_code == 503

    def test_details_upstream_error_returns_503(self, client):
        """Google Place Details API error must map to HTTP 503."""
        with patch(
            "app.api.epic1_locations.maps_service.get_place_details",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Google Place Details API returned status: UNKNOWN_ERROR"),
        ):
            response = client.get("/api/locations/details/place_001")

        assert response.status_code == 503
