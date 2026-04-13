# WearImpact — Iteration 1 Implementation Plan

> **Scope**: Epic 1 (Local Eco-Shop Navigator) + Epic 4 (Brand Transparency & Sustainability Inquiry)
> **Sprint**: Iteration 1
> **Last Updated**: 2026-04-13

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Epic 1: Local Eco-Shop Navigator](#epic-1-local-eco-shop-navigator)
4. [Epic 4: Brand Transparency & Sustainability Inquiry](#epic-4-brand-transparency--sustainability-inquiry)
5. [Shared API Conventions](#shared-api-conventions)
6. [Database Schema](#database-schema)
7. [External Dependencies](#external-dependencies)
8. [Risk Register](#risk-register)

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | Python 3.11 + FastAPI | REST API, async support |
| **Database** | PostgreSQL 15 | Main DB for Epic 4 brand data (Epic 1 requires no DB storage) |
| **ORM** | SQLAlchemy 2.0 | Database operations |
| **Cache** | Redis | API response caching (3s requirement) |
| **Maps** | Google Maps Platform | Places, Distance Matrix, Directions |
| **Deployment** | Railway / Render | PaaS, suitable for student project |

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── epic1_locations.py     # Eco-shop search & details endpoints
│   │   └── epic4_brands.py        # Brand search & details endpoints
│   ├── services/
│   │   ├── maps_service.py        # Google Maps API wrapper
│   │   └── geo_service.py         # Haversine distance calculation
│   ├── models/
│   │   ├── location.py            # Epic 1 DB models
│   │   └── brand.py               # Epic 4 DB models
│   ├── schemas/
│   │   ├── location.py            # Epic 1 Pydantic schemas
│   │   └── brand.py               # Epic 4 Pydantic schemas
│   ├── core/
│   │   ├── config.py              # Environment variables
│   │   └── database.py            # DB connection
│   └── main.py
├── data/
│   └── brands_seed.csv            # Epic 4 initial brand dataset
├── tests/
│   ├── test_epic1.py
│   └── test_epic4.py
├── requirements.txt
└── .env.example
```

---

## Epic 1: Local Eco-Shop Navigator

### Overview

Helps users find nearby second-hand shops, donation points, and clothing recycling locations on a map, with route directions.

### Business Flow

```
Step 1  Frontend obtains geolocation
           ↓
Step 2  Backend searches nearby eco-shops (Google Places API)
        + calculates distance (Haversine)          ← single backend call
           ↓
Step 3  Frontend renders map markers (Google Maps JS SDK)
           ↓
Step 4  User clicks marker → Backend fetches place details (Google Place Details API)
           ↓
Step 5  User clicks "Get Directions" → Frontend renders route directly via Maps SDK
```

---

### Step 1 — Initialization & User Authorization (Frontend)

| Item | Detail |
|---|---|
| **Trigger** | User opens the eco-shop navigator page |
| **Action** | Browser calls `navigator.geolocation.getCurrentPosition()` |
| **Fallback** | User manually enters a suburb or postcode |
| **Data sent to backend** | `{ user_lat, user_lng, radius_km }` |

---

### Step 2 — Search Nearby Places (Backend)

| Item | Detail |
|---|---|
| **Endpoint** | `GET /api/locations/nearby` |
| **API called** | Google Places Nearby Search API |
| **Keywords** | `["op shop", "charity shop", "clothing donation", "clothing recycling", "Salvos", "Vinnies", "Red Cross"]` |
| **Distance calc** | Haversine formula on backend (no extra Distance Matrix call) |
| **Fields extracted** | `place_id`, `name`, `lat`, `lng`, `types`, `distance_km` |
| **Response** | JSON array of places, sorted by distance ascending |

> **Why Haversine instead of Distance Matrix API?**
> Places Nearby Search already returns `lat/lng` for each result.
> Haversine gives straight-line distance instantly with zero extra API cost.
> Distance Matrix (driving time) is only called on demand in Step 5.

**No-results handling**: If Google returns 0 results, backend responds with:
```json
{ "results": [], "message": "No eco-shops found in this area. Try increasing the search radius." }
```

---

### Step 3 — Map Rendering (Frontend)

| Item | Detail |
|---|---|
| **SDK** | Google Maps JavaScript SDK |
| **Action** | Render one marker per place returned by Step 2 |
| **Marker info** | Name, type label, distance (km) |
| **Performance target** | At least 3 results visible within 3 seconds of page load |

---

### Step 4 — View Place Details (Frontend + Backend)

| Item | Detail |
|---|---|
| **Trigger** | User clicks a map marker or list item |
| **Endpoint** | `GET /api/locations/details/{place_id}` |
| **API called** | Google Place Details API |
| **Fields returned** | `address`, `opening_hours`, `phone`, `website`, `place_type` |
| **Cache** | Redis — cache by `place_id`, TTL 24 hours |
| **Performance target** | Response within 3 seconds |

---

### Step 5 — Get Directions (Frontend)

| Item | Detail |
|---|---|
| **Trigger** | User clicks "Get Directions" button |
| **Handler** | Frontend only — Google Maps Directions Service (JS SDK) |
| **Input** | `user_lat/lng` → `destination place_id` |
| **Output** | Route rendered on map with distance (km) + estimated time (mins) |
| **Backend involvement** | None required |

> Route rendering is handled entirely client-side to minimise latency and backend load.

---

### Epic 1 — API Endpoints

```
GET /api/locations/nearby
  Query params: lat (float), lng (float), radius_km (float, default 5)
  Response: {
    results: [
      {
        place_id:     string,
        name:         string,
        type:         string,   // "second_hand_shop" | "donation_point" | "recycling"
        lat:          float,
        lng:          float,
        distance_km:  float
      }
    ],
    message: string | null      // populated only when results is empty
  }

GET /api/locations/details/{place_id}
  Response: {
    place_id:       string,
    name:           string,
    address:        string,
    opening_hours:  string[],   // e.g. ["Mon-Fri: 9am-5pm", ...]
    phone:          string | null,
    website:        string | null,
    type:           string
  }
```

---

### Epic 1 — Data Flow Summary

| Phase | Initiator | Data Sent | Data Received |
|---|---|---|---|
| Search | Frontend → Backend | `user_lat`, `user_lng`, `radius_km` | Place list with `distance_km` |
| Details | Frontend → Backend | `place_id` | `address`, `opening_hours`, `phone` |
| Directions | Frontend (SDK direct) | `user_lat/lng`, `dest_lat/lng` | Map route rendered |

---

## Epic 4: Brand Transparency & Sustainability Inquiry

### Overview

Allows users to search clothing brands and view their environmental claims, supply chain transparency, and third-party sustainability ratings, helping users make informed purchasing decisions.

### Business Flow

```
Step 1  User types brand name → debounced search request (300ms)
           ↓
Step 2  Backend fuzzy-searches brand database → returns brand list with summary rating
           ↓
Step 3  User selects a brand → Backend returns full brand details
           ↓
Step 4  Frontend renders: overall rating + dimension scores + claims + data sources
```

---

### Data Strategy

> **This is the highest-risk area of Epic 4.**
> There is no free, comprehensive, real-time API for brand sustainability data.

**Recommended approach for Iteration 1 MVP:**

1. Manually curate a dataset of **50–100 brands** (Australian + global fast fashion + sustainable brands)
2. Primary data sources to reference:
   - [Good On You](https://goodonyou.eco) — planet / people / animals ratings
   - Fashion Revolution Fashion Transparency Index 2024
   - B Corp public registry
3. Store as `brands_seed.csv` → import to PostgreSQL on first deploy
4. Each record includes `last_updated` and `source_url` for AC 4.1.3 compliance

**Suggested brand coverage:**

| Category | Examples |
|---|---|
| Fast fashion (low rating) | Zara, H&M, Shein, Cotton On, Kmart |
| Mid-range | Uniqlo, Country Road, Witchery |
| Sustainable (high rating) | Patagonia, Eileen Fisher, Mighty Good Undies |
| Australian focus | CAMILLA, R.M.Williams, Spell & the Gypsy |

---

### Step 1 — Brand Search (Frontend + Backend)

| Item | Detail |
|---|---|
| **Trigger** | User types in the search bar |
| **Frontend** | 300ms debounce to avoid per-keystroke requests |
| **Endpoint** | `GET /api/brands/search?q={query}` |
| **Backend logic** | PostgreSQL `ILIKE` search on `name` + `aliases` fields |
| **Response** | `[{ id, name, logo_url, overall_rating, overall_label, country }]` |
| **No-results fallback** | Return closest match via Levenshtein distance (`Did you mean...`) |

---

### Step 2 — Brand Detail (Frontend + Backend)

| Item | Detail |
|---|---|
| **Trigger** | User clicks a brand from search results |
| **Endpoint** | `GET /api/brands/{brand_id}` |
| **Backend logic** | Single DB query joining brands + ratings + claims + sources |
| **Cache** | Redis — cache by `brand_id`, TTL 1 hour |
| **Performance target** | Response within 3 seconds |

---

### Step 3 — Data Source Attribution (Frontend)

| Item | Detail |
|---|---|
| **Trigger** | User clicks "Data Source" on the brand detail page |
| **Handler** | Frontend renders the `sources` array already returned in Step 2 |
| **Backend involvement** | None — data already included in brand detail response |

---

### Epic 4 — API Endpoints

```
GET /api/brands/search?q={query}
  Response: [
    {
      id:              integer,
      name:            string,
      logo_url:        string | null,
      overall_rating:  float,         // 1.0 – 5.0
      overall_label:   string,        // "Great" | "Good" | "It's a Start" | "Avoid"
      country:         string
    }
  ]

GET /api/brands/{brand_id}
  Response: {
    id:                  integer,
    name:                string,
    logo_url:            string | null,
    country:             string,
    overall_rating:      float,
    overall_label:       string,
    ratings: [
      { category: "planet" | "people" | "animals", score: float, summary: string }
    ],
    environmental_claims: [
      { claim: string, verified: bool, source_url: string | null }
    ],
    supply_chain: {
      transparency_score:    integer,   // 0–100
      factories_disclosed:   bool,
      certifications:        string[],  // e.g. ["GOTS", "Fair Trade", "B Corp"]
      audit_info:            string | null
    },
    sources: [
      { name: string, url: string, last_updated: string }
    ]
  }

GET /api/brands/featured
  Response: top 6 brands for homepage display (optional)
```

---

### Epic 4 — Data Flow Summary

| Phase | Initiator | Data Sent | Data Received |
|---|---|---|---|
| Search | Frontend → Backend | `query` (string) | Brand list + `overall_rating` |
| Detail | Frontend → Backend | `brand_id` | Full brand data (ratings + claims + sources) |
| Source view | Frontend only | — | From `sources` field in detail response |

---

## Database Schema

### Epic 1 Tables

```sql
-- No persistent storage needed for Epic 1
-- All location data is fetched live from Google APIs
-- Only cache layer (Redis) is used for place details
```

### Epic 4 Tables

```sql
CREATE TABLE brands (
    id                SERIAL PRIMARY KEY,
    name              VARCHAR(255) NOT NULL,
    aliases           TEXT[],                    -- alternative search terms
    country           VARCHAR(100),
    founded_year      INTEGER,
    logo_url          TEXT,
    overall_rating    NUMERIC(2,1),              -- 1.0 – 5.0
    overall_label     VARCHAR(50),
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE brand_ratings (
    id          SERIAL PRIMARY KEY,
    brand_id    INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    category    VARCHAR(20) CHECK (category IN ('planet', 'people', 'animals')),
    score       NUMERIC(2,1),
    summary     TEXT,
    detail_text TEXT
);

CREATE TABLE brand_claims (
    id          SERIAL PRIMARY KEY,
    brand_id    INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    claim_text  TEXT NOT NULL,
    verified    BOOLEAN DEFAULT FALSE,
    source_url  TEXT
);

CREATE TABLE brand_supply_chain (
    id                     SERIAL PRIMARY KEY,
    brand_id               INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    transparency_score     INTEGER CHECK (transparency_score BETWEEN 0 AND 100),
    factories_disclosed    BOOLEAN DEFAULT FALSE,
    certifications         TEXT[],
    audit_info             TEXT
);

CREATE TABLE brand_sources (
    id            SERIAL PRIMARY KEY,
    brand_id      INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    source_name   VARCHAR(255),
    source_url    TEXT,
    last_updated  DATE
);

-- Full-text search index
CREATE INDEX idx_brands_name ON brands USING GIN (to_tsvector('english', name));
```

---

## Shared API Conventions

All endpoints follow these conventions:

```
Base URL:     /api/v1/
Content-Type: application/json
Error format: { "error": string, "detail": string }

HTTP status codes:
  200  Success
  400  Bad request (missing/invalid params)
  404  Resource not found
  422  Validation error
  500  Internal server error
  503  Upstream API unavailable (Google Maps timeout etc.)
```

**Performance requirements** (from Epic 6 NFR):

| Endpoint | Target |
|---|---|
| `GET /api/locations/nearby` | < 3s |
| `GET /api/locations/details/{id}` | < 3s (Redis cache hit: < 200ms) |
| `GET /api/brands/search` | < 3s (DB query: < 500ms) |
| `GET /api/brands/{id}` | < 3s (Redis cache hit: < 200ms) |

---

## External Dependencies

| Service | Used by | Billing model | Free tier |
|---|---|---|---|
| Google Places Nearby Search | Epic 1 Step 2 | Per request | $200/month credit |
| Google Place Details API | Epic 1 Step 4 | Per request | included in credit |
| Google Maps JS SDK | Epic 1 Step 3 & 5 | Per map load | included in credit |
| Redis | Epic 1 + Epic 4 | Self-hosted or Redis Cloud | Free tier available |
| PostgreSQL | Epic 4 | Self-hosted or Supabase | Free tier available |

---

## Risk Register

| # | Epic | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| R1 | Epic 1 | Australian op-shop data sparse in Google Places | Medium | High | Supplement with keyword variations; manually verify coverage before launch |
| R2 | Epic 1 | Google API quota exceeded during demo | Low | High | Cache all Place Details responses in Redis (TTL 24h) |
| R3 | Epic 4 | Brand dataset too small / outdated | Medium | Medium | Prioritise 50 high-traffic brands; display `last_updated` on all records |
| R4 | Epic 4 | No free API for Good On You data | High | Medium | Manually curate from public website; cite source URL per record |
| R5 | Epic 4 | User searches brand not in database | High | Low | Return "Did you mean..." suggestion via Levenshtein; show "not found" message |
| R6 | Both | 3-second response SLA not met | Low | Medium | Redis caching + DB indexing; profile slow queries early |
