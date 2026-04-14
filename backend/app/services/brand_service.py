"""Brand data service for Epic 4 sustainability transparency.

Handles all database queries for:
- Fuzzy brand/company search (Step 1)
- Full company detail retrieval (Step 2)

Uses raw SQL via SQLAlchemy text() to leverage pg_trgm ILIKE indexes.
Score labels are computed here — not stored in the database.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def get_score_label(score: int) -> str:
    """Map a 0-100 ethical score to a human-readable label.

    Bands are defined in the iteration plan and applied at query time.

    Args:
        score: Integer ethical score between 0 and 100.

    Returns:
        One of: "Great", "Good", "It's a Start", "Below Average", "Avoid".
    """
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


async def search_brands(db: AsyncSession, query: str) -> list[dict]:
    """Search brands and companies by name using case-insensitive fuzzy match.

    Searches both brands.brand_name and companies.name with ILIKE.
    Results are deduplicated at the company level — one row per company.
    When a brand name matched, matched_brand is set; otherwise null.

    Args:
        db: Async database session.
        query: Search string from the user (min 1 char).

    Returns:
        List of dicts matching BrandSearchResult schema, ordered by
        overall_score descending (best brands first).
    """
    pattern = f"%{query}%"

    # Search companies directly OR via any of their child brands.
    # The subquery resolves matched_brand: the first brand name that matched,
    # or null if the company name itself matched.
    sql = text("""
        SELECT
            c.id               AS company_id,
            c.name             AS company_name,
            c.overall_score,
            c.product_category,
            (
                SELECT b2.brand_name
                FROM brands b2
                WHERE b2.company_id = c.id
                  AND b2.brand_name ILIKE :pattern
                LIMIT 1
            ) AS matched_brand
        FROM companies c
        WHERE c.name ILIKE :pattern
           OR EXISTS (
               SELECT 1 FROM brands b
               WHERE b.company_id = c.id
                 AND b.brand_name ILIKE :pattern
           )
        ORDER BY c.overall_score DESC
        LIMIT 20
    """)

    result = await db.execute(sql, {"pattern": pattern})
    rows = result.mappings().all()

    return [
        {
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "matched_brand": row["matched_brand"],
            "overall_score": row["overall_score"],
            "score_label": get_score_label(row["overall_score"]),
            "product_category": row["product_category"],
            "logo_url": None,  # Clearbit lookup is handled by the frontend
        }
        for row in rows
    ]


async def get_company_detail(db: AsyncSession, company_id: int) -> dict | None:
    """Retrieve full company sustainability data including all dimension scores.

    Fetches the company row and all associated brand names in two queries,
    then combines them into a single response dict.

    Args:
        db: Async database session.
        company_id: Primary key of the company to fetch.

    Returns:
        Dict matching CompanyDetailResponse schema, or None if not found.
    """
    company_sql = text("""
        SELECT
            id, name, overall_score, governance_score, tracing_score,
            env_score, has_supplier_code, code_covers_raw_materials,
            has_senior_accountability, assessed_fibre_impact,
            sustainable_fibre_pct, has_emissions_target, product_category
        FROM companies
        WHERE id = :company_id
    """)

    company_result = await db.execute(company_sql, {"company_id": company_id})
    company = company_result.mappings().first()

    if company is None:
        return None

    brands_sql = text("""
        SELECT brand_name, score
        FROM brands
        WHERE company_id = :company_id
        ORDER BY brand_name
    """)

    brands_result = await db.execute(brands_sql, {"company_id": company_id})
    brands = brands_result.mappings().all()

    return {
        "company_id": company["id"],
        "company_name": company["name"],
        "product_category": company["product_category"],
        "logo_url": None,  # Clearbit lookup is handled by the frontend
        "overall_score": company["overall_score"],
        "score_label": get_score_label(company["overall_score"]),
        "governance_score": company["governance_score"],
        "tracing_score": company["tracing_score"],
        "env_score": company["env_score"],
        "has_supplier_code": company["has_supplier_code"],
        "code_covers_raw_materials": company["code_covers_raw_materials"],
        "has_senior_accountability": company["has_senior_accountability"],
        "assessed_fibre_impact": company["assessed_fibre_impact"],
        "sustainable_fibre_pct": company["sustainable_fibre_pct"],
        "has_emissions_target": company["has_emissions_target"],
        "brands": [{"brand_name": b["brand_name"], "score": b["score"]} for b in brands],
    }
