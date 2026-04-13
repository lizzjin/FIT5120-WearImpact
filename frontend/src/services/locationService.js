import { mockLocations } from '../data/mockLocations'

/**
 * Fetch eco-shop locations.
 * For iteration 1, this returns mock data.
 * Later, this function can be replaced with a real API request.
 *
 * @param {Object} params
 * @param {string} params.query - user search input
 * @param {string} params.filter - selected location type
 * @returns {Promise<Array>}
 */
export async function fetchLocations({ query = '', filter = 'All' } = {}) {
  // Simulate async API behavior
  await new Promise((resolve) => setTimeout(resolve, 300))

  let results = [...mockLocations]

  const normalizedQuery = query.trim().toLowerCase()

  if (normalizedQuery) {
    results = results.filter(
      (location) =>
        location.name.toLowerCase().includes(normalizedQuery) ||
        location.address.toLowerCase().includes(normalizedQuery) ||
        location.type.toLowerCase().includes(normalizedQuery)
    )
  }

  if (filter !== 'All') {
    results = results.filter((location) => location.type === filter)
  }

  return results
}