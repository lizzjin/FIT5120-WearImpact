# Claude Coding Standard (Epic 1 Only)

> Project: WearImpact
> Scope: Epic 1 - Local Eco-Shop Navigator only
> Language/Framework: Python 3.11 + FastAPI

## 1. Scope and Non-Goals

This document applies only to Epic 1 backend and related frontend integration points:

- Nearby eco-shop search
- Place detail retrieval
- Distance calculation (Haversine)
- Redis cache for details endpoint

Out of scope:

- Epic 4 brand search/rating features
- Non-Epic 1 data models and APIs

---

## 2. Core Principles

1. Readability over cleverness.
2. One module, one clear responsibility.
3. Public functions must have complete docstrings.
4. Complex logic must include intent-focused comments.
5. Naming should reveal business meaning without extra explanation.
6. Keep endpoint response fields consistent with iteration plan.

---

## 3. Epic 1 Module Layout and Responsibilities

Recommended backend structure for Epic 1:

- backend/app/api/epic1_locations.py
  - Defines Epic 1 HTTP endpoints only.
  - Handles request validation, response shaping, and status codes.
  - Must not contain raw Google API request logic.

- backend/app/services/maps_service.py
  - Wraps Google Places/Details requests.
  - Converts upstream payloads to internal normalized structures.
  - Handles upstream timeout/retry/error mapping.

- backend/app/services/geo_service.py
  - Pure geospatial calculations.
  - Contains Haversine distance implementation.
  - Must be deterministic and side-effect free.

- backend/app/schemas/location.py
  - Pydantic request/response schemas for Epic 1.
  - Single source of truth for field names and types.

- backend/app/core/config.py
  - Reads environment variables (API key, timeout, cache TTL).

- backend/tests/test_epic1.py
  - Endpoint and service-level tests for Epic 1 behavior.

Rule:
Each file starts with a short module docstring explaining why this module exists and where it is used in the Epic 1 flow.

---

## 4. Commenting Standard (Mandatory)

### 4.1 Module-Level Docstring

Every Epic 1 module must begin with a docstring like this:

```python
"""Epic 1 nearby location API.

Provides endpoints for:
- searching nearby eco-shops by user coordinates
- retrieving place details by place_id

This module coordinates request validation and response formatting.
"""
```

### 4.2 Function/Method Docstring

All public functions must include:

- Purpose (what business action this function performs)
- Parameters (with units where relevant, e.g. km)
- Returns (shape/meaning)
- Raises (HTTPException, timeout, validation errors)

Example:

```python
def haversine_km(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> float:
    """Compute straight-line distance between two coordinates in kilometers.

    Used by Epic 1 nearby search results for distance-based sorting.
    """
```

### 4.3 Inline Comments

Inline comments are required only when logic is not obvious.

Good comment:

```python
# Use straight-line distance here to avoid paid matrix API calls in Step 2.
```

Bad comment:

```python
# Increment i by 1.
```

### 4.4 Endpoint-Level Comment Block

Each endpoint should have a short comment block above declaration:

```python
# Epic 1 Step 2:
# Search nearby second-hand/donation/recycling places and return sorted results.
```

---

## 5. Naming Conventions (Mandatory)

## 5.1 General Rules

- Use snake_case for variables, functions, and file names.
- Use PascalCase for Pydantic models and classes.
- Use UPPER_SNAKE_CASE for constants.
- Avoid abbreviations unless domain-standard (lat, lng, ttl, api).
- Boolean names must read as true/false facts (is_open_now, has_website).

## 5.2 Business-Aligned Variable Naming

Use business terms from Epic 1 plan:

- user_lat, user_lng
- radius_km
- place_id
- distance_km
- opening_hours
- eco_place_type

Do not use ambiguous names:

- data, item, tmp, val, obj

## 5.3 Function Naming

Function names must include intent:

- fetch_nearby_places
- normalize_place_result
- classify_place_type
- get_place_details
- sort_places_by_distance

---

## 6. API Contract Rules (Epic 1)

Must match iteration plan fields exactly.

### 6.1 GET /api/locations/nearby

Query params:

- lat: float
- lng: float
- radius_km: float (default 5)

Response:

- results: list
- message: string or null (set when empty)

Each result must contain:

- place_id
- name
- type
- lat
- lng
- distance_km

### 6.2 GET /api/locations/details/{place_id}

Response must contain:

- place_id
- name
- address
- opening_hours
- phone
- website
- type

Rule:
Never rename response keys without updating schema and tests in the same PR.

---

## 7. Error Handling Standard

1. Validate input early and fail fast (400/422).
2. Map Google upstream errors to 503 with clear detail.
3. Use consistent error payload shape:

```json
{ "error": "...", "detail": "..." }
```

4. Log upstream failures with request context but never log secrets.
5. Empty search result is not an error; return 200 with results=[] and guidance message.

---

## 8. Caching Standard (Epic 1 Step 4)

1. Cache key format:

- place_details:{place_id}

2. Default TTL:

- 86400 seconds (24h)

3. Cache behavior:

- Cache hit: return cached payload directly
- Cache miss: fetch from Google API, normalize, cache, return

4. Comment requirement:

- Add one short comment where cache key is created explaining why key naming is fixed and versionable.

---

## 9. Performance and Reliability Rules

1. Add timeout to all outbound Google API calls.
2. Never perform Distance Matrix call in Epic 1 Step 2.
3. Sort nearby results by distance_km ascending before response.
4. Keep service methods pure where possible for easier unit testing.
5. Avoid repeated data transformation loops when one pass is sufficient.

---

## 10. Test Standard (Epic 1)

Minimum tests required per feature:

1. Nearby endpoint returns sorted results by distance.
2. Nearby endpoint handles zero results with message.
3. Details endpoint returns normalized fields.
4. Details endpoint uses cache hit path.
5. Details endpoint cache miss path writes cache.
6. Upstream API failure maps to 503.
7. Invalid lat/lng/radius returns validation error.

Test naming examples:

- test_nearby_returns_distance_sorted_results
- test_nearby_returns_empty_message_when_no_results
- test_details_uses_cache_before_upstream_call

---

## 11. PR Checklist (Epic 1)

Before merging Epic 1 code, verify:

1. Module docstring added/updated.
2. Public functions have meaningful docstrings.
3. Endpoint blocks have Step comments aligned to plan.
4. Variable/function names follow this document.
5. Response fields match API contract exactly.
6. Error format is consistent.
7. Tests cover happy path + edge path.

---

## 12. Example Comment and Naming Pattern

```python
"""Google Maps service for Epic 1 location discovery.

Encapsulates Google Places API calls so API layer stays framework-focused.
"""

GOOGLE_PLACES_TIMEOUT_SECONDS = 6


def fetch_nearby_places(user_lat: float, user_lng: float, radius_km: float) -> list[dict]:
    """Fetch nearby eco-related places and return normalized place records."""
    # Step 2 uses Nearby Search + Haversine to minimize API cost and latency.
    ...
```

---

## 13. Enforcement Policy

If new Epic 1 code violates this standard:

1. Request changes before merge.
2. Mark PR as not ready until naming/comments/contracts are fixed.
3. Do not postpone schema or naming corrections to later iterations.

This standard is mandatory for all Epic 1 implementation work.
