"""Pydantic schemas for Epic 4 brand transparency API.

Defines request/response shapes for:
- GET /api/brands/search  — brand search results list
- GET /api/brands/{company_id}  — full company detail with dimension scores
"""

from pydantic import BaseModel


class BrandItem(BaseModel):
    """A single brand under a parent company."""

    brand_name: str
    score: int


class BrandSearchResult(BaseModel):
    """One company entry returned by the brand search endpoint."""

    company_id: int
    company_name: str
    # The brand name that matched the query; null when the company name matched directly
    matched_brand: str | None
    overall_score: int
    score_label: str
    product_category: str
    logo_url: str | None


class BrandSearchResponse(BaseModel):
    """Wrapper for search results; message is set only when results is empty."""

    results: list[BrandSearchResult]
    message: str | None = None


class CompanyDetailResponse(BaseModel):
    """Full company detail including all sustainability dimension scores."""

    company_id: int
    company_name: str
    product_category: str
    logo_url: str | None

    # Overall ethical fashion score (0-100)
    overall_score: int
    score_label: str

    # Dimension scores
    governance_score: int      # 0-6
    tracing_score: int         # 0-15
    env_score: int             # 0-21

    # Policy questions: "Yes" | "No" | "Partial"
    has_supplier_code: str
    code_covers_raw_materials: str
    has_senior_accountability: str
    assessed_fibre_impact: str

    # Sustainable fibre percentage range: "0%" | "1-25%" | ... | "100%"
    sustainable_fibre_pct: str

    # Emissions reduction target: "Yes" | "No" | "Partial"
    has_emissions_target: str

    # All brand names under this company
    brands: list[BrandItem]
