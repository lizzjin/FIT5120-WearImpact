"""Epic 4 brand transparency API endpoints.

Provides endpoints for:
- searching brands/companies by name (fuzzy ILIKE search)
- retrieving full company sustainability scores and brand list

This module handles request validation, response shaping, and HTTP status codes.
All database logic is delegated to brand_service.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.brand import BrandSearchResponse, BrandSearchResult, CompanyDetailResponse, CompanyListResponse
from app.services.brand_service import get_company_detail, list_companies, search_brands

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/brands", tags=["brands"])


# List all companies with server-side pagination.
@router.get("", response_model=CompanyListResponse)
async def list_companies_endpoint(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(9, ge=1, le=50, description="Results per page"),
    db: AsyncSession = Depends(get_db),
) -> CompanyListResponse:
    """Return a paginated list of all companies ordered by ethical score.

    Args:
        page: 1-based page number.
        page_size: Number of results per page (max 50).
        db: Injected async database session.

    Returns:
        CompanyListResponse with results, total count, page, and page_size.

    Raises:
        HTTPException 503: If the database is unreachable.
    """
    try:
        results, total = await list_companies(db, page, page_size)
    except Exception as exc:
        logger.error("List companies failed for page=%d: %s", page, exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return CompanyListResponse(results=[BrandSearchResult(**r) for r in results], total=total, page=page, page_size=page_size)


# Epic 4 Step 1:
# Fuzzy-search brands and companies by name; returns deduplicated company list.
@router.get("/search", response_model=BrandSearchResponse)
async def search_brands_endpoint(
    q: str = Query(..., min_length=1, description="Brand or company name to search"),
    db: AsyncSession = Depends(get_db),
) -> BrandSearchResponse:
    """Search for brands and companies by name.

    Performs a case-insensitive ILIKE search against both brands.brand_name
    and companies.name, returning up to 20 results grouped by company.

    Args:
        q: Search query string (minimum 1 character).
        db: Injected async database session.

    Returns:
        BrandSearchResponse with results list and optional guidance message.

    Raises:
        HTTPException 503: If the database is unreachable.
    """
    try:
        results = await search_brands(db, q.strip())
    except Exception as exc:
        logger.error("Brand search failed for query=%r: %s", q, exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    if not results:
        return BrandSearchResponse(
            results=[],
            message="No brands found. Try a different spelling.",
        )

    return BrandSearchResponse(
        results=[BrandSearchResult(**item) for item in results],
    )


# Epic 4 Step 2:
# Fetch full company sustainability detail including all dimension scores.
@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company_detail_endpoint(
    company_id: int,
    db: AsyncSession = Depends(get_db),
) -> CompanyDetailResponse:
    """Return full sustainability data for a company.

    Fetches all dimension scores, policy answers, and the list of all
    brands under this company.

    Args:
        company_id: Integer primary key of the company.
        db: Injected async database session.

    Returns:
        CompanyDetailResponse with scores, policies, and brands list.

    Raises:
        HTTPException 404: If no company with the given ID exists.
        HTTPException 503: If the database is unreachable.
    """
    try:
        detail = await get_company_detail(db, company_id)
    except Exception as exc:
        logger.error("Company detail failed for company_id=%d: %s", company_id, exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    if detail is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyDetailResponse(**detail)
