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

**Iteration 1 data source:** Two pre-cleaned CSV files derived from the Fashion Transparency Index (Australian market focus), processed by `backend/scripts/clean_brand_data.py`:

| File | Rows | Key fields |
|---|---|---|
| `backend/data/brands_cleaned.csv` | 372 | `brand_name`, `company_name`, `score` |
| `backend/data/companies_cleaned.csv` | 123 | 10 dimension columns + `product_category` |

**Data cleaning already completed:**
- `<1` sentinel values replaced with `0` (18 instances across tracing + env scores)
- 15 company name inconsistencies normalised (e.g. `APG& CO` → `APG & Co`)
- `product_category` column added: `footwear` (3 companies) / `general` (120 companies)
- All 372 brands verified to resolve to a company record (0 unresolved joins)

**Two-hop data model:** Scores are stored at the **company** level. When a user searches by brand name, the backend first resolves the brand to its parent company, then returns the company-level detail along with the full list of sibling brands.

**Score label bands** (applied at query time, not stored):

| Score (0–100) | Label |
|---|---|
| 75 – 100 | Great |
| 50 – 74 | Good |
| 30 – 49 | It's a Start |
| 10 – 29 | Below Average |
| 0 – 9 | Avoid |

**Company logo:** Retrieved at runtime via Clearbit Logo API (`https://logo.clearbit.com/{domain}`) — not stored in DB. Falls back to a letter-avatar if unavailable.

---

### Step 1 — Brand Search (Frontend + Backend)

| Item | Detail |
|---|---|
| **Trigger** | User types in the search bar |
| **Frontend** | 300ms debounce to avoid per-keystroke requests |
| **Endpoint** | `GET /api/brands/search?q={query}` |
| **Backend logic** | PostgreSQL `ILIKE` search on both `brands.brand_name` and `companies.name`; deduplicates by company |
| **Response** | `[{ company_id, company_name, matched_brand, overall_score, score_label, product_category, logo_url }]` |
| **No-results fallback** | Return empty array with `message: "No brands found. Try a different spelling."` |

---

### Step 2 — Brand Detail (Frontend + Backend)

| Item | Detail |
|---|---|
| **Trigger** | User clicks a brand from search results |
| **Endpoint** | `GET /api/brands/{company_id}` |
| **Backend logic** | Single DB query on `companies` joined with `brands`; returns full dimension scores + all sibling brands |
| **Cache** | Redis — cache by `company_id`, TTL 1 hour |
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
  Query params: q (string, min 1 char)
  Searches brands.brand_name and companies.name using ILIKE, groups by company.
  Response: [
    {
      company_id:        integer,
      company_name:      string,
      matched_brand:     string | null,   // brand name that matched; null if company name matched
      overall_score:     integer,         // 0–100
      score_label:       string,          // "Great" | "Good" | "It's a Start" | "Below Average" | "Avoid"
      product_category:  string,          // "general" | "footwear"
      logo_url:          string | null    // Clearbit runtime lookup
    }
  ]
  Empty result: { results: [], message: "No brands found. Try a different spelling." }

GET /api/brands/{company_id}
  Response: {
    company_id:                integer,
    company_name:              string,
    product_category:          string,
    logo_url:                  string | null,
    overall_score:             integer,         // 0–100
    score_label:               string,
    governance_score:          integer,         // 0–6
    tracing_score:             integer,         // 0–15
    env_score:                 integer,         // 0–21
    has_supplier_code:         string,          // "Yes" | "No" | "Partial"
    code_covers_raw_materials: string,
    has_senior_accountability: string,
    assessed_fibre_impact:     string,
    sustainable_fibre_pct:     string,          // "0%" | "1-25%" | "26-50%" | "51-75%" | "76-99%" | "100%"
    has_emissions_target:      string,
    brands: [
      { brand_name: string, score: integer }   // all brands under this company
    ]
  }
```

---

### Epic 4 — Data Flow Summary

| Phase | Initiator | Data Sent | Data Received |
|---|---|---|---|
| Search | Frontend → Backend | `q` (string) | Company list with `overall_score`, `score_label`, matched brand |
| Detail | Frontend → Backend | `company_id` | Full company data (all scores + brands list) |
| Logo | Frontend → Clearbit | company domain | Logo image (runtime, no backend involved) |

---

## Database Schema

### Epic 1 Tables

```sql
-- No persistent storage needed for Epic 1
-- All location data is fetched live from Google APIs
-- Only cache layer (Redis) is used for place details
```

### Epic 4 Tables

Two tables directly derived from `brands_cleaned.csv` and `companies_cleaned.csv`.
See `docs/epic4-db-schema.md` for full column mapping, index rationale, and seed instructions.

```sql
-- One row per company (123 rows from companies_cleaned.csv)
CREATE TABLE companies (
    id                          SERIAL PRIMARY KEY,
    name                        VARCHAR(255) NOT NULL UNIQUE,
    overall_score               SMALLINT,                     -- 0-100 (ethical_fashion_brand_score)
    governance_score            SMALLINT,                     -- 0-6
    tracing_score               SMALLINT,                     -- 0-15
    env_score                   SMALLINT,                     -- 0-21
    has_supplier_code           VARCHAR(10),                  -- "Yes" | "No" | "Partial"
    code_covers_raw_materials   VARCHAR(10),
    has_senior_accountability   VARCHAR(10),
    assessed_fibre_impact       VARCHAR(10),
    sustainable_fibre_pct       VARCHAR(20),                  -- "0%" | "1-25%" | ... | "100%"
    has_emissions_target        VARCHAR(10),
    product_category            VARCHAR(10) DEFAULT 'general' -- "general" | "footwear"
);

-- One row per brand (372 rows from brands_cleaned.csv)
CREATE TABLE brands (
    id           SERIAL PRIMARY KEY,
    brand_name   VARCHAR(255) NOT NULL,
    company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    score        SMALLINT                                      -- brand-level ethical score
);

-- Indexes for search performance
CREATE INDEX idx_companies_name_trgm ON companies USING GIN (name gin_trgm_ops);
CREATE INDEX idx_brands_name_trgm    ON brands    USING GIN (brand_name gin_trgm_ops);
CREATE INDEX idx_brands_company_id   ON brands (company_id);
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
| R3 | Epic 4 | Cleaned CSV data has edge-case encoding issues not caught by script | Low | Low | `cleaning_report.txt` shows 0 unresolved joins; rerun script if source CSVs are updated |
| R4 | Epic 4 | Clearbit logo unavailable for some companies | Medium | Low | Frontend falls back to letter-avatar; no backend dependency on Clearbit |
| R5 | Epic 4 | User searches brand not in database | High | Low | Return empty array with guidance message; `pg_trgm` similarity handles typos |
| R6 | Both | 3-second response SLA not met | Low | Medium | Redis caching + DB indexing; profile slow queries early |
