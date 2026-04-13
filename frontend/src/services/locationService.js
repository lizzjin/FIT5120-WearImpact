/**
 * Epic 1 location service — Local Eco-Shop Navigator.
 *
 * Handles geolocation acquisition (Step 1) and all backend API calls:
 *   - fetchNearbyPlaces()  → GET /api/locations/nearby  (Step 2)
 *   - fetchPlaceDetails()  → GET /api/locations/details/{place_id}  (Step 4)
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Melbourne CBD used as fallback when geolocation is denied or unavailable
const MELBOURNE_CBD_LAT = -37.8136
const MELBOURNE_CBD_LNG = 144.9631

/**
 * Request the user's current GPS coordinates from the browser.
 *
 * Falls back to Melbourne CBD coordinates if the user denies permission
 * or if geolocation is not supported by their browser.
 *
 * @returns {Promise<{lat: number, lng: number, isFallback: boolean}>}
 */
export function getUserCoordinates() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({ lat: MELBOURNE_CBD_LAT, lng: MELBOURNE_CBD_LNG, isFallback: true })
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          isFallback: false,
        })
      },
      () => {
        // User denied permission or position unavailable — use fallback
        resolve({ lat: MELBOURNE_CBD_LAT, lng: MELBOURNE_CBD_LNG, isFallback: true })
      },
      { timeout: 8000, maximumAge: 60000 }
    )
  })
}

/**
 * Fetch nearby eco-shops from the backend for a given user location.
 *
 * Calls GET /api/locations/nearby and returns the parsed response.
 * Results are already sorted by distance_km ascending by the backend.
 *
 * @param {object} params
 * @param {number} params.lat       - User latitude in decimal degrees
 * @param {number} params.lng       - User longitude in decimal degrees
 * @param {number} [params.radiusKm=5] - Search radius in kilometres
 * @returns {Promise<{results: Array, message: string|null}>}
 * @throws {Error} On network failure or non-2xx response
 */
export async function fetchNearbyPlaces({ lat, lng, radiusKm = 5 }) {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius_km: radiusKm.toString(),
  })

  const response = await fetch(`${API_BASE}/api/locations/nearby?${params}`)

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(
      errorBody?.detail?.detail ||
      errorBody?.detail ||
      `Nearby search failed (HTTP ${response.status})`
    )
  }

  return response.json()
}

/**
 * Fetch full place details for a single eco-shop.
 *
 * Calls GET /api/locations/details/{place_id}. The backend caches this
 * response in Redis for 24 hours, so repeated clicks are fast.
 *
 * @param {string} placeId - Google place_id from a nearby search result
 * @returns {Promise<object>} PlaceDetails: {place_id, name, address, opening_hours, phone, website, type}
 * @throws {Error} On network failure, 404 (unknown place), or 503 (upstream error)
 */
export async function fetchPlaceDetails(placeId) {
  const response = await fetch(
    `${API_BASE}/api/locations/details/${encodeURIComponent(placeId)}`
  )

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(
      errorBody?.detail?.detail ||
      errorBody?.detail ||
      `Place details fetch failed (HTTP ${response.status})`
    )
  }

  return response.json()
}
