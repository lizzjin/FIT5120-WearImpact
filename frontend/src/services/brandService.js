/**
 * Epic 4 brand service — Brand Transparency & Sustainability Inquiry.
 *
 * Handles all backend API calls:
 *   - searchBrands()      → GET /api/brands/search?q=...  (Step 1)
 *   - fetchCompanyDetail() → GET /api/brands/{company_id}  (Step 2)
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Search brands and companies by name with fuzzy matching.
 *
 * @param {string} query - Search string (min 1 char)
 * @returns {Promise<{results: Array, message: string|null}>}
 * @throws {Error} On network failure or non-2xx response
 */
export async function searchBrands(query) {
  const params = new URLSearchParams({ q: query })
  const response = await fetch(`${API_BASE}/api/brands/search?${params}`)

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody?.detail || `Search failed (HTTP ${response.status})`)
  }

  return response.json()
}

/**
 * Fetch full sustainability detail for a company.
 *
 * @param {number} companyId - Company primary key
 * @returns {Promise<object>} Full CompanyDetailResponse
 * @throws {Error} On network failure, 404, or 503
 */
export async function fetchCompanyDetail(companyId) {
  const response = await fetch(`${API_BASE}/api/brands/${companyId}`)

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody?.detail || `Detail fetch failed (HTTP ${response.status})`)
  }

  return response.json()
}
