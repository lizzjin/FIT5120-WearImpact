# Epic 4 — Database Schema & Seed Instructions

> **Source data**: `backend/data/brands_cleaned.csv` (372 rows) + `backend/data/companies_cleaned.csv` (123 rows)
> Cleaned by `backend/scripts/clean_brand_data.py` — run that script first if source CSVs are updated.

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Column Mapping](#column-mapping)
3. [Full SQL (CREATE TABLE)](#full-sql)
4. [Indexes](#indexes)
5. [Score Label Logic](#score-label-logic)
6. [Seed Script](#seed-script)
7. [Verification Queries](#verification-queries)

---

## Schema Overview

Two tables only. Scores are stored at the **company** level; brands are a separate lookup table that maps brand names to their parent company.

```
companies (123 rows)
    id  ←──────────────────────┐
    name                       │  FK
    overall_score              │
    governance_score           │
    tracing_score              │
    env_score                  │
    has_supplier_code          │
    code_covers_raw_materials  │
    has_senior_accountability  │
    assessed_fibre_impact      │
    sustainable_fibre_pct      │
    has_emissions_target       │
    product_category           │
                               │
brands (372 rows)              │
    id                         │
    brand_name                 │
    company_id ────────────────┘
    score
```

---

## Column Mapping

### companies ← companies_cleaned.csv

| DB Column | CSV Column | Type | Notes |
|---|---|---|---|
| `name` | `Company` | VARCHAR(255) | Unique, primary join key |
| `overall_score` | `ethical_fashion_brand_score` | SMALLINT | 0–100 |
| `governance_score` | `Policies&Governance_Score(out of 6)` | SMALLINT | 0–6 |
| `has_supplier_code` | `Does the company have a Code of Conduct for suppliers?` | VARCHAR(10) | "Yes" / "No" / "Partial" |
| `code_covers_raw_materials` | `Does the Code apply to multiple levels of the supply chain including the raw materials level?` | VARCHAR(10) | "Yes" / "No" / "Partial" |
| `has_senior_accountability` | `Does the company publicly disclose that it has a designated senior officer...` | VARCHAR(10) | "Yes" / "No" / "Partial" |
| `tracing_score` | `Tracing&Risk_score(all stage Production )` | SMALLINT | 0–15; `<1` already replaced with `0` |
| `env_score` | `environmental_sustainability_score(score_out_of_21)` | SMALLINT | 0–21; `<1` already replaced with `0` |
| `assessed_fibre_impact` | `Has the company assessed the environmental impact of its top three fibres...` | VARCHAR(10) | "Yes" / "No" / "Partial" |
| `sustainable_fibre_pct` | `What percentage of the company's final product is made from sustainable fibers?` | VARCHAR(20) | "0%" / "1-25%" / "26-50%" / "51-75%" / "76-99%" / "100%" |
| `has_emissions_target` | `Has the company published an emissions reduction target...` | VARCHAR(10) | "Yes" / "No" / "Partial" |
| `product_category` | `product_category` | VARCHAR(10) | "general" / "footwear" (added by cleaning script) |

### brands ← brands_cleaned.csv

| DB Column | CSV Column | Type | Notes |
|---|---|---|---|
| `brand_name` | `brand_name` | VARCHAR(255) | Display name; may differ from company name |
| `company_id` | `company_name` | INTEGER (FK) | Resolved via `companies.name` lookup at import |
| `score` | `score` | SMALLINT | Brand-level ethical score 0–100 |

---

## Full SQL

```sql
-- Required extension for trigram search (ILIKE fuzzy search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- -----------------------------------------------------------------------
-- companies: one row per parent company, all score dimensions stored here
-- -----------------------------------------------------------------------
CREATE TABLE companies (
    id                          SERIAL PRIMARY KEY,
    name                        VARCHAR(255) NOT NULL UNIQUE,

    -- Overall score (0–100): source of score_label computed at query time
    overall_score               SMALLINT CHECK (overall_score BETWEEN 0 AND 100),

    -- Dimension scores
    governance_score            SMALLINT CHECK (governance_score BETWEEN 0 AND 6),
    tracing_score               SMALLINT CHECK (tracing_score >= 0),
    env_score                   SMALLINT CHECK (env_score BETWEEN 0 AND 21),

    -- Policy questions: "Yes" | "No" | "Partial"
    has_supplier_code           VARCHAR(10),
    code_covers_raw_materials   VARCHAR(10),
    has_senior_accountability   VARCHAR(10),
    assessed_fibre_impact       VARCHAR(10),

    -- Sustainable fibre range: "0%" | "1-25%" | "26-50%" | "51-75%" | "76-99%" | "100%"
    sustainable_fibre_pct       VARCHAR(20),

    -- Emissions reduction target: "Yes" | "No" | "Partial"
    has_emissions_target        VARCHAR(10),

    -- "general" for apparel companies; "footwear" for footwear-only records
    product_category            VARCHAR(10) NOT NULL DEFAULT 'general'
);

-- -----------------------------------------------------------------------
-- brands: one row per brand name, foreign key to parent company
-- -----------------------------------------------------------------------
CREATE TABLE brands (
    id           SERIAL PRIMARY KEY,
    brand_name   VARCHAR(255) NOT NULL,
    company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    score        SMALLINT CHECK (score BETWEEN 0 AND 100)
);
```

---

## Indexes

```sql
-- Trigram indexes enable ILIKE '%query%' with index support
-- Required for the /api/brands/search endpoint to meet < 500ms target
CREATE INDEX idx_companies_name_trgm ON companies USING GIN (name gin_trgm_ops);
CREATE INDEX idx_brands_name_trgm    ON brands    USING GIN (brand_name gin_trgm_ops);

-- FK lookup: used when joining brands → companies
CREATE INDEX idx_brands_company_id ON brands (company_id);
```

> **Why `pg_trgm` instead of full-text search?**
> Brand names like "H&M", "2XU", "yd." contain punctuation and abbreviations that
> `to_tsvector` tokenises poorly. Trigram similarity handles these correctly and
> supports `ILIKE` queries directly.

---

## Score Label Logic

Score labels are **computed at query time** in the API layer — not stored in the DB.

```python
def get_score_label(score: int) -> str:
    """Map 0-100 ethical score to a human-readable label."""
    if score >= 75:
        return "Great"
    elif score >= 50:
        return "Good"
    elif score >= 30:
        return "It's a Start"
    elif score >= 10:
        return "Below Average"
    else:
        return "Avoid"
```

---

## Seed Script

`backend/scripts/seed_epic4.py` — imports the two cleaned CSVs into PostgreSQL.

```python
"""
Epic 4 database seed script.

Reads backend/data/companies_cleaned.csv and backend/data/brands_cleaned.csv
and inserts all rows into the companies and brands tables.

Run ONCE after CREATE TABLE. Safe to re-run: truncates tables first.

Usage:
    DATABASE_URL=postgresql://user:pass@host/db python backend/scripts/seed_epic4.py
"""

import csv
import os
import psycopg2

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COMPANIES_CSV = os.path.join(DATA_DIR, "companies_cleaned.csv")
BRANDS_CSV    = os.path.join(DATA_DIR, "brands_cleaned.csv")

DATABASE_URL = os.environ["DATABASE_URL"]


def seed(conn):
    cur = conn.cursor()

    # -- Wipe existing data (safe for re-runs in dev/staging) ----------------
    cur.execute("TRUNCATE brands, companies RESTART IDENTITY CASCADE;")

    # -- Insert companies -----------------------------------------------------
    company_id_map = {}   # name → id (used for brand FK resolution)

    with open(COMPANIES_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO companies (
                    name, overall_score, governance_score,
                    tracing_score, env_score,
                    has_supplier_code, code_covers_raw_materials,
                    has_senior_accountability, assessed_fibre_impact,
                    sustainable_fibre_pct, has_emissions_target, product_category
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    row["Company"],
                    int(row["ethical_fashion_brand_score"]),
                    int(row["Policies&Governance_Score(out of 6)"]),
                    int(row["Tracing&Risk_score(all stage Production )"]),
                    int(row["environmental_sustainability_score(score_out_of_21)"]),
                    row["Does the company have a Code of Conduct for suppliers?"],
                    row["Does the Code apply to multiple levels of the supply chain including the raw materials level?"],
                    row["Does the company publicly disclose that it has a designated senior officer accountable for implementation, and a board committee/process tasked with oversight of its supply chain policies that address human rights and environmental sustainability?"],
                    row["Has the company assessed the environmental impact of its top three fibres and materials used in its apparel products and implemented learnings from assessment into product design and production?"],
                    row["What percentage of the company's final product is made from sustainable fibers?"],
                    row["Has the company published an emissions reduction target and decarbonisation strategy in line with the current UN Fashion Industry Charter for Climate Action?"],
                    row["product_category"],
                ),
            )
            (company_id,) = cur.fetchone()
            company_id_map[row["Company"]] = company_id

    print(f"[seed] {len(company_id_map)} companies inserted.")

    # -- Insert brands --------------------------------------------------------
    brands_inserted = 0
    unresolved = []

    with open(BRANDS_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_id = company_id_map.get(row["company_name"])
            if company_id is None:
                unresolved.append(row["company_name"])
                continue
            cur.execute(
                "INSERT INTO brands (brand_name, company_id, score) VALUES (%s, %s, %s)",
                (row["brand_name"], company_id, int(row["score"])),
            )
            brands_inserted += 1

    print(f"[seed] {brands_inserted} brands inserted.")
    if unresolved:
        print(f"[seed] WARNING: {len(unresolved)} brands had unresolved company: {set(unresolved)}")

    conn.commit()
    cur.close()


if __name__ == "__main__":
    conn = psycopg2.connect(DATABASE_URL)
    try:
        seed(conn)
        print("[seed] Done.")
    finally:
        conn.close()
```

**Run order:**

```bash
# 1. Clean source data (if CSVs were updated)
python backend/scripts/clean_brand_data.py

# 2. Apply schema to database
psql $DATABASE_URL -f docs/epic4-db-schema.sql   # or run CREATE TABLE statements manually

# 3. Seed data
DATABASE_URL=postgresql://... python backend/scripts/seed_epic4.py
```

---

## Verification Queries

Run these after seeding to confirm data loaded correctly.

```sql
-- Row counts
SELECT 'companies' AS tbl, COUNT(*) FROM companies
UNION ALL
SELECT 'brands',           COUNT(*) FROM brands;
-- Expected: companies=123, brands=372

-- Footwear companies
SELECT name, overall_score, product_category
FROM companies
WHERE product_category = 'footwear'
ORDER BY name;
-- Expected: Adidas (Footwear), Brand Collective (Footwear), New Balance (Footwear)

-- All brands with no parent company (should be 0)
SELECT b.brand_name FROM brands b
LEFT JOIN companies c ON b.company_id = c.id
WHERE c.id IS NULL;

-- Top 10 companies by overall score
SELECT name, overall_score, product_category
FROM companies
ORDER BY overall_score DESC
LIMIT 10;

-- Score distribution
SELECT
    CASE
        WHEN overall_score >= 75 THEN 'Great (75-100)'
        WHEN overall_score >= 50 THEN 'Good (50-74)'
        WHEN overall_score >= 30 THEN 'It''s a Start (30-49)'
        WHEN overall_score >= 10 THEN 'Below Average (10-29)'
        ELSE                          'Avoid (0-9)'
    END AS label,
    COUNT(*) AS companies
FROM companies
GROUP BY 1
ORDER BY MIN(overall_score) DESC;

-- Fuzzy brand search example (requires pg_trgm index)
SELECT b.brand_name, c.name AS company, c.overall_score
FROM brands b
JOIN companies c ON b.company_id = c.id
WHERE b.brand_name ILIKE '%patagoni%'
   OR c.name ILIKE '%patagoni%';
```
