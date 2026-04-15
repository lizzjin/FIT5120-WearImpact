<template>
  <div class="eco-page">
    <Navbar />
    <div class="page-container">
      <section class="eco-hero" role="search">
        <p class="hero-eyebrow">NEARBY ECO-LOCATIONS</p>
        <h1>Find Eco-Friendly Fashion Near You</h1>
        <p class="hero-subtitle">
          Discover second-hand shops, donation points, and textile
          recycling — all on one map.
        </p>

        <!-- AC 1.1.1 — manual address input with Google Places Autocomplete -->
        <div class="address-search-row">
          <div class="address-input-wrap">
            <Search class="address-search-icon" :size="16" :stroke-width="2" />
            <input
              ref="addressSearchInput"
              type="text"
              class="address-input"
              placeholder="Type a suburb or address to search…"
              autocomplete="off"
            />
          </div>
          <p class="address-hint">or allow location access for automatic results</p>
        </div>

        <p v-if="isFallbackLocation" class="fallback-notice">
          Showing results near Melbourne CBD — allow location access for personalised results.
        </p>
      </section>

      <!-- Radius selector + type filters -->
      <div class="controls-row">
        <label class="radius-label">
          Search radius:
          <div class="select-wrap">
            <select v-model="radiusKm" @change="loadPlaces" class="radius-select">
              <option :value="2">2 km</option>
              <option :value="5">5 km</option>
              <option :value="10">10 km</option>
              <option :value="20">20 km</option>
            </select>
            <ChevronDown class="select-chevron" :size="14" :stroke-width="2.5" />
          </div>
        </label>

        <div class="controls-divider"></div>

        <div class="filter-row">
          <button
            v-for="typeOption in filterOptions"
            :key="typeOption.value"
            :class="{ active: activeFilter === typeOption.value }"
            :aria-pressed="activeFilter === typeOption.value"
            @click="setFilter(typeOption.value)"
          >
            <span
              v-if="typeOption.color"
              class="filter-dot"
              :style="{ background: typeOption.color }"
            ></span>
            {{ typeOption.label }}
          </button>
        </div>
      </div>

      <!-- Non-loading status messages -->
      <div v-if="errorMessage" class="status-message error">{{ errorMessage }}</div>
      <div v-else-if="!isLoading && apiMessage" class="status-message info">{{ apiMessage }}</div>

      <!-- Main layout: sidebar (details + list) + map -->
      <div class="content-layout">
        <!-- Left sidebar — results list with inline details, scrolls independently -->
        <div class="results-section">
          <!-- Skeleton cards shown while loading -->
          <template v-if="isLoading">
            <div v-for="n in 5" :key="'skel-' + n" class="skeleton-card">
              <div class="skeleton-header">
                <div class="skeleton-bar skeleton-title"></div>
                <div class="skeleton-bar skeleton-badge"></div>
              </div>
              <div class="skeleton-bar skeleton-distance"></div>
              <div class="skeleton-bar skeleton-hint"></div>
            </div>
          </template>

          <template v-else>
            <!-- Empty state — only shown after a real search attempt -->
            <div
              v-if="filteredPlaces.length === 0 && !errorMessage && !apiMessage && hasSearched"
              class="empty-state"
            >
              <div class="empty-state-icon">🌿</div>
              <p class="empty-state-title">No eco-shops found here</p>
              <p class="empty-state-hint">
                Try expanding the search radius or selecting a different filter.
              </p>
            </div>
            <!-- Details panel renders inline, directly below the card that was clicked -->
            <template v-for="place in filteredPlaces" :key="place.place_id">
              <LocationCard
                :place="place"
                :is-selected="selectedPlaceId === place.place_id"
                @select="handleCardSelect(place)"
              />
              <transition name="slide-up">
                <div
                  v-if="selectedDetails && selectedPlaceId === place.place_id"
                  class="details-panel"
                >
                  <button class="details-close" @click="clearSelection" aria-label="Close details">
                    <X :size="18" :stroke-width="2.5" />
                  </button>

                  <h3>{{ selectedDetails.name }}</h3>
                  <span class="details-type-badge" :class="selectedDetails.type">
                    {{ typeLabel(selectedDetails.type) }}
                  </span>

                  <div v-if="detailsLoading" class="details-loading">Loading details…</div>

                  <template v-else>
                    <p v-if="selectedDetails.address">
                      <strong>Address:</strong> {{ selectedDetails.address }}
                    </p>

                    <div v-if="selectedDetails.opening_hours?.length" class="details-section">
                      <strong>Opening Hours:</strong>
                      <ul class="hours-list">
                        <li v-for="line in selectedDetails.opening_hours" :key="line">{{ line }}</li>
                      </ul>
                    </div>

                    <p v-if="selectedDetails.phone">
                      <strong>Phone:</strong>
                      <a :href="`tel:${selectedDetails.phone}`">{{ selectedDetails.phone }}</a>
                    </p>

                    <p v-if="selectedDetails.website">
                      <strong>Website:</strong>
                      <a :href="selectedDetails.website" target="_blank" rel="noopener noreferrer">
                        {{ selectedDetails.website }}
                      </a>
                    </p>

                    <p v-if="detailsError" class="details-error">{{ detailsError }}</p>

                    <div class="travel-mode-row">
                      <button
                        v-for="mode in travelModes"
                        :key="mode.value"
                        :class="{ active: travelMode === mode.value }"
                        class="mode-btn"
                        @click="travelMode = mode.value"
                      >
                        <component :is="mode.icon" :size="15" :stroke-width="2" />
                        {{ mode.label }}
                      </button>
                    </div>

                    <button class="directions-btn" @click="getDirections(selectedDetails)">
                      <Navigation :size="15" :stroke-width="2" />
                      Get Directions
                    </button>

                    <div v-if="routeInfo" class="route-info">
                      <span class="route-stat">
                        <Route :size="14" :stroke-width="2.2" /> {{ routeInfo.distance }}
                      </span>
                      <span class="route-divider">·</span>
                      <span class="route-stat">
                        <Clock :size="14" :stroke-width="2.2" /> {{ routeInfo.duration }}
                      </span>
                    </div>
                  </template>
                </div>
              </transition>
            </template>
          </template>
        </div>

        <!-- Map — fills all remaining width and height -->
        <div class="map-section">
          <div ref="mapContainer" class="map-container">
            <div v-if="mapLoadError" class="map-error">
              <p>🗺️ Map unavailable</p>
              <p class="map-error-detail">{{ mapLoadError }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import Navbar from '../components/Navbar.vue'
import LocationCard from '../components/LocationCard.vue'
import { Car, PersonStanding, Bus, Route, Clock, Search, X, Navigation, ChevronDown } from 'lucide-vue-next'
import {
  getUserCoordinates,
  fetchNearbyPlaces,
  fetchPlaceDetails,
} from '../services/locationService'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const mapContainer = ref(null)
const mapLoadError = ref('')

const isLoading = ref(true)   // true from the start so skeleton shows immediately
const hasSearched = ref(false) // flips to true after the first loadPlaces() completes
const errorMessage = ref('')
const apiMessage = ref('')
const isFallbackLocation = ref(false)

const userLat = ref(null)
const userLng = ref(null)
const radiusKm = ref(5)

const allPlaces = ref([])
const activeFilter = ref('all')

const selectedPlaceId = ref(null)
const selectedDetails = ref(null)
const detailsLoading = ref(false)
const detailsError = ref('')

// Manual address search input element ref (for Places Autocomplete)
const addressSearchInput = ref(null)

// Route info shown in the details panel after Get Directions (AC 1.2.2)
const routeInfo = ref(null)   // { distance: '5.2 km', duration: '12 mins' } or null

// Travel mode selection for directions
const travelMode = ref('DRIVING')

// Map objects — kept outside reactive state to avoid Vue proxying DOM objects
let mapInstance = null
let userLocationMarker = null   // blue dot for the user's own position
let activeInfoWindow = null
let directionsService = null
let directionsRenderer = null
const markerMap = {}   // place_id → google.maps.Marker

// ---------------------------------------------------------------------------
// Filter options — values match the 'type' field returned by the backend
// ---------------------------------------------------------------------------

const filterOptions = [
  { label: 'All',         value: 'all',             color: null },
  { label: 'Second-hand', value: 'second_hand_shop', color: '#16a34a' },
  { label: 'Donation',    value: 'donation_point',   color: '#2563eb' },
  { label: 'Recycling',   value: 'recycling',        color: '#d97706' },
]

const travelModes = [
  { label: 'Drive',   value: 'DRIVING', icon: Car },
  { label: 'Walk',    value: 'WALKING', icon: PersonStanding },
  { label: 'Transit', value: 'TRANSIT', icon: Bus },
]

const filteredPlaces = computed(() => {
  if (activeFilter.value === 'all') return allPlaces.value
  return allPlaces.value.filter((p) => p.type === activeFilter.value)
})

// ---------------------------------------------------------------------------
// Marker icon helpers
// ---------------------------------------------------------------------------

// Colour per eco-place type — also used in the legend / filter chips
const TYPE_COLOURS = {
  second_hand_shop: '#16a34a',
  donation_point:   '#2563eb',
  recycling:        '#d97706',
}

/**
 * Build a pin-shaped SVG marker icon for a given hex colour.
 * Uses a data URI so no extra network request is needed and the shape
 * works across all Google Maps versions without relying on SymbolPath enums.
 */
function createPinIcon(colour) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
    <path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 26 14 26S28 24.5 28 14C28 6.268 21.732 0 14 0z"
          fill="${colour}" stroke="white" stroke-width="1.5"/>
    <circle cx="14" cy="14" r="5.5" fill="white" fill-opacity="0.9"/>
  </svg>`
  return {
    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
    scaledSize: new window.google.maps.Size(28, 40),
    anchor: new window.google.maps.Point(14, 40),
  }
}

function typeLabel(type) {
  return (
    { second_hand_shop: 'Second-hand', donation_point: 'Donation', recycling: 'Recycling' }[type] ||
    type
  )
}

// ---------------------------------------------------------------------------
// Google Maps JS SDK — dynamic loader (Step 3)
// ---------------------------------------------------------------------------

function loadGoogleMapsScript() {
  return new Promise((resolve, reject) => {
    // Already loaded — nothing to do
    if (window.google?.maps) {
      resolve()
      return
    }
    const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
    if (!key) {
      reject(new Error('Add VITE_GOOGLE_MAPS_API_KEY to frontend/.env.local'))
      return
    }
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=places`
    script.async = true
    script.defer = true
    script.onload = resolve
    script.onerror = () => reject(new Error('Failed to load Google Maps JS SDK'))
    document.head.appendChild(script)
  })
}

function initMap(lat, lng) {
  if (!mapContainer.value || !window.google?.maps) return

  mapInstance = new window.google.maps.Map(mapContainer.value, {
    center: { lat, lng },
    zoom: 14,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: true,
  })

  // Directions service + renderer for inline routing (AC 1.2.1 / 1.2.2)
  directionsService = new window.google.maps.DirectionsService()
  directionsRenderer = new window.google.maps.DirectionsRenderer({
    suppressMarkers: true,   // keep our custom pin markers visible
    polylineOptions: { strokeColor: '#16a34a', strokeWeight: 5, strokeOpacity: 0.85 },
  })
  directionsRenderer.setMap(mapInstance)

  // Blue dot — user's current location (stored so it can be re-attached after re-renders)
  userLocationMarker = new window.google.maps.Marker({
    position: { lat, lng },
    map: mapInstance,
    title: 'Your location',
    icon: {
      // CIRCLE is a valid SymbolPath enum value
      path: window.google.maps.SymbolPath.CIRCLE,
      scale: 8,
      fillColor: '#1d4ed8',
      fillOpacity: 1,
      strokeColor: '#ffffff',
      strokeWeight: 2,
    },
    zIndex: 999,
  })
}

// ---------------------------------------------------------------------------
// Map marker management
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Address search — Google Places Autocomplete (AC 1.1.1 manual input)
// ---------------------------------------------------------------------------

function initAutocomplete() {
  if (!addressSearchInput.value || !window.google?.maps?.places) return

  const autocomplete = new window.google.maps.places.Autocomplete(
    addressSearchInput.value,
    {
      // Restrict to Australian addresses to match the eco-shop dataset
      componentRestrictions: { country: 'au' },
      fields: ['geometry', 'formatted_address'],
    },
  )

  autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace()
    if (!place.geometry?.location) return

    const lat = place.geometry.location.lat()
    const lng = place.geometry.location.lng()

    // Update user coordinates and re-centre map + marker
    userLat.value = lat
    userLng.value = lng
    isFallbackLocation.value = false

    if (mapInstance) mapInstance.setCenter({ lat, lng })
    if (userLocationMarker) userLocationMarker.setPosition({ lat, lng })

    clearRoute()
    clearSelection()
    loadPlaces()
  })
}

// ---------------------------------------------------------------------------
// Route helpers (AC 1.2.1 / 1.2.2)
// ---------------------------------------------------------------------------

function clearRoute() {
  if (directionsRenderer) {
    // Passing an empty route removes the polyline from the map
    directionsRenderer.setDirections({ routes: [] })
  }
  routeInfo.value = null
}

function closeActiveInfoWindow() {
  if (activeInfoWindow) {
    activeInfoWindow.close()
    activeInfoWindow = null
  }
}

function addPlaceMarkers(places) {
  if (!mapInstance) return

  // Remove all existing place markers from the map
  Object.values(markerMap).forEach((m) => m.setMap(null))
  Object.keys(markerMap).forEach((k) => delete markerMap[k])
  closeActiveInfoWindow()

  // Ensure the user location dot is always visible after markers are redrawn
  if (userLocationMarker) {
    userLocationMarker.setMap(mapInstance)
  }

  places.forEach((place) => {
    const colour = TYPE_COLOURS[place.type] || '#16a34a'
    const marker = new window.google.maps.Marker({
      position: { lat: place.lat, lng: place.lng },
      map: mapInstance,
      title: place.name,
      icon: createPinIcon(colour),
    })

    // InfoWindow — small popup shown on the map when clicking a marker
    const infoWindow = new window.google.maps.InfoWindow({
      content: `
        <div style="font-family:sans-serif;max-width:180px;padding:2px">
          <strong style="font-size:13px">${place.name}</strong><br>
          <span style="font-size:12px;color:#475569">${place.distance_km} km away</span>
        </div>`,
      ariaLabel: place.name,
    })

    marker.addListener('click', () => {
      // Close any previously open InfoWindow before opening this one
      closeActiveInfoWindow()
      infoWindow.open({ anchor: marker, map: mapInstance })
      activeInfoWindow = infoWindow
      // Trigger the full details flow (same as clicking a card)
      handleCardSelect(place)
    })

    markerMap[place.place_id] = marker
  })
}

// ---------------------------------------------------------------------------
// Data loading — Step 2
// ---------------------------------------------------------------------------

async function loadPlaces() {
  isLoading.value = true
  errorMessage.value = ''
  apiMessage.value = ''
  allPlaces.value = []

  try {
    const data = await fetchNearbyPlaces({
      lat: userLat.value,
      lng: userLng.value,
      radiusKm: radiusKm.value,
    })

    allPlaces.value = data.results || []
    apiMessage.value = data.message || ''

    if (mapInstance) {
      addPlaceMarkers(allPlaces.value)
    }
  } catch (err) {
    errorMessage.value = err.message || 'Failed to load eco-shops. Please try again.'
  } finally {
    isLoading.value = false
    hasSearched.value = true
  }
}

// ---------------------------------------------------------------------------
// Card / marker selection → fetch place details (Step 4)
// ---------------------------------------------------------------------------

async function handleCardSelect(place) {
  // Second click on the same card collapses the panel
  if (selectedPlaceId.value === place.place_id) {
    clearSelection()
    return
  }

  selectedPlaceId.value = place.place_id
  // Immediately show an optimistic stub so the panel appears without delay
  selectedDetails.value = { name: place.name, type: place.type }
  detailsLoading.value = true
  detailsError.value = ''

  // Pan map to the selected marker
  if (mapInstance) {
    mapInstance.panTo({ lat: place.lat, lng: place.lng })
  }

  try {
    const details = await fetchPlaceDetails(place.place_id)
    selectedDetails.value = details
  } catch (err) {
    detailsError.value = 'Could not load details. Please try again.'
  } finally {
    detailsLoading.value = false
    // Scroll the details panel into view — block:'nearest' means minimum scroll only
    await nextTick()
    const panel = document.querySelector('.details-panel')
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

function clearSelection() {
  selectedPlaceId.value = null
  selectedDetails.value = null
  detailsError.value = ''
  closeActiveInfoWindow()
  clearRoute()
}

// ---------------------------------------------------------------------------
// Directions — Step 5 (frontend-only via Google Maps URL)
// ---------------------------------------------------------------------------

function getDirections(place) {
  if (!place?.address || !directionsService || !directionsRenderer) return

  // Clear any previous route before drawing a new one
  clearRoute()

  const request = {
    origin: { lat: userLat.value, lng: userLng.value },
    destination: place.address,
    travelMode: window.google.maps.TravelMode[travelMode.value],
  }

  directionsService.route(request, (result, status) => {
    if (status === window.google.maps.DirectionsStatus.OK) {
      directionsRenderer.setDirections(result)
      const leg = result.routes[0].legs[0]
      // AC 1.2.2 — display distance and estimated travel time
      routeInfo.value = {
        distance: leg.distance.text,
        duration: leg.duration.text,
      }
    } else {
      // Fallback: open Google Maps in a new tab if Directions API call fails
      console.warn('Directions request failed:', status)
      const dest = encodeURIComponent(place.address)
      const origin = `${userLat.value},${userLng.value}`
      window.open(
        `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${dest}`,
        '_blank',
      )
    }
  })
}

// ---------------------------------------------------------------------------
// Filter
// ---------------------------------------------------------------------------

function setFilter(value) {
  activeFilter.value = value
}

// Sync map markers with the active filter so hidden types don't appear
watch(filteredPlaces, (places) => {
  if (mapInstance) addPlaceMarkers(places)
})

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

onMounted(async () => {
  // Step 1 — Obtain user GPS coordinates (or fall back to Melbourne CBD)
  const coords = await getUserCoordinates()
  userLat.value = coords.lat
  userLng.value = coords.lng
  isFallbackLocation.value = coords.isFallback

  // Step 3 — Load Google Maps JS SDK and initialise the map
  try {
    await loadGoogleMapsScript()
    initMap(coords.lat, coords.lng)
    // Autocomplete needs the SDK loaded + the input element in the DOM
    initAutocomplete()
  } catch (err) {
    mapLoadError.value = err.message
    console.warn('Google Maps JS SDK unavailable:', err.message)
  }

  // Step 2 — Search nearby eco-shops via backend
  await loadPlaces()

  // If places finished loading before the map was ready (unlikely but possible),
  // add the markers now that mapInstance exists.
  if (mapInstance && allPlaces.value.length > 0) {
    addPlaceMarkers(allPlaces.value)
  }
})
</script>

<style scoped>
.eco-page {
  background: #f8faf8;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 16px 24px 0;
  box-sizing: border-box;
}

/* Hero — compact to give more height to the map */
.eco-hero {
  background: #edf5ef;
  border-radius: 20px;
  padding: 20px 40px;
  margin-bottom: 12px;
  text-align: center;
  flex-shrink: 0;
}

.hero-eyebrow {
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.eco-hero h1 {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.hero-subtitle {
  font-size: 15px;
  color: #475569;
  line-height: 1.5;
  max-width: 560px;
  margin: 0 auto 14px;
}

.fallback-notice {
  font-size: 14px !important;
  color: #92400e !important;
  background: #fef3c7;
  border-radius: 8px;
  padding: 6px 14px;
  display: inline-block;
  margin-top: 8px;
}

/* ── Skeleton loading cards ───────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position:  600px 0; }
}

.skeleton-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  padding: 22px 24px;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
}

.skeleton-bar {
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite linear;
}

.skeleton-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.skeleton-title  { height: 18px; width: 55%; }
.skeleton-badge  { height: 22px; width: 22%; border-radius: 999px; flex-shrink: 0; }
.skeleton-distance { height: 14px; width: 35%; margin-bottom: 10px; }
.skeleton-hint   { height: 12px; width: 48%; }

/* Address search bar (AC 1.1.1) */
.address-search-row {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.address-input-wrap {
  position: relative;
  width: 100%;
  max-width: 600px;
}

.address-search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.address-input {
  width: 100%;
  height: 52px;
  padding: 0 18px 0 44px;
  border: 2px solid #d1d5db;
  border-radius: 999px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: white;
  box-sizing: border-box;
}

.address-input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
}

.address-hint {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* Travel mode buttons */
.travel-mode-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.mode-btn {
  flex: 1;
  padding: 7px 10px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: background 0.15s, border-color 0.15s;
}

.mode-btn.active {
  background: #f0fdf4;
  border: 2px solid #16a34a;
  color: #166534;
}

/* Route result (AC 1.2.2) */
.route-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 14px;
  background: #f0fdf4;
  border-radius: 10px;
  border: 1px solid #bbf7d0;
}

.route-stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 700;
  color: #166534;
}

.route-divider {
  color: #86efac;
  font-size: 16px;
}

/* Controls */
.controls-row {
  display: flex;
  align-items: center;
  gap: 0;
  flex-wrap: wrap;
  margin-bottom: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px 20px;
  flex-shrink: 0;
}

.radius-label {
  font-weight: 600;
  font-size: 14px;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.radius-select {
  padding: 8px 32px 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background: white;
  padding-right: 28px;
}

.select-chevron {
  position: absolute;
  right: 8px;
  color: #64748b;
  pointer-events: none;
}

.controls-divider {
  width: 1px;
  height: 28px;
  background: #e5e7eb;
  margin: 0 20px;
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-row button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.filter-row button.active {
  background: #16a34a;
  color: white;
  border-color: #16a34a;
}

.filter-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Status messages (error / info banners above the layout) */
.status-message {
  margin-bottom: 20px;
  font-weight: 600;
  color: #334155;
}

.status-message.error { color: #b91c1c; }
.status-message.info  { color: #92400e; }

/* Empty state card — shown in the list column when search returns no results */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: white;
  border: 2px dashed #d1fae5;
  border-radius: 20px;
  gap: 8px;
}

.empty-state-icon {
  font-size: 40px;
  line-height: 1;
  margin-bottom: 4px;
}

.empty-state-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.empty-state-hint {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
  max-width: 260px;
}

/* Main layout — fills all remaining viewport height */
.content-layout {
  flex: 1;
  min-height: 0; /* crucial: lets flex children shrink below content size */
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 16px;
  padding-bottom: 16px;
}

/* Left sidebar — scrolls independently, map stays fixed */
.results-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
  padding-right: 2px;
}

/* Map column — static, fills full height */
.map-section {
  min-height: 0;
}

.map-container {
  width: 100%;
  height: 100%; /* fills the full column height */
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-error {
  text-align: center;
  padding: 24px;
  color: #64748b;
}

.map-error p {
  margin: 0 0 6px;
  font-size: 28px;
}

.map-error-detail {
  font-size: 13px !important;
  color: #94a3b8 !important;
}

/* Details panel — now sits at the top of the sidebar (gap handles spacing) */
.details-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
  position: relative;
  flex-shrink: 0;
}

.details-close {
  position: absolute;
  top: 14px;
  right: 14px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: background 150ms ease, color 150ms ease;
}

.details-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.details-panel h3 {
  font-size: 20px;
  color: #0f172a;
  margin: 0 0 8px;
  padding-right: 28px;
  line-height: 1.3;
}

.details-type-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 14px;
}

.details-type-badge.second_hand_shop { background: #dcfce7; color: #166534; }
.details-type-badge.donation_point   { background: #dbeafe; color: #1e40af; }
.details-type-badge.recycling         { background: #fef3c7; color: #92400e; }

.details-section {
  margin-bottom: 10px;
}

.details-panel p {
  margin: 0 0 10px;
  color: #475569;
  font-size: 15px;
  line-height: 1.6;
}

.details-panel a {
  color: #16a34a;
  word-break: break-all;
}

.hours-list {
  padding-left: 18px;
  margin: 6px 0 10px;
  color: #475569;
  font-size: 14px;
  line-height: 1.7;
}

.details-loading {
  font-size: 14px;
  color: #64748b;
  padding: 12px 0;
}

.details-error {
  font-size: 14px;
  color: #b91c1c;
  margin-bottom: 8px;
}

.directions-btn {
  margin-top: 6px;
  width: 100%;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px;
  font-weight: 600;
  cursor: pointer;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  transition: background 0.15s;
}

.directions-btn:hover { background: #15803d; }

/* Slide-up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Responsive — restore normal page flow on mobile */
@media (max-width: 900px) {
  .eco-page {
    height: auto;
    overflow: visible;
  }

  .page-container {
    overflow: visible;
    padding: 12px 16px;
  }

  .content-layout {
    grid-template-columns: 1fr;
    flex: none;
    padding-bottom: 24px;
  }

  .results-section {
    overflow: visible;
    max-height: none;
  }

  .map-section {
    order: -1; /* map above list on mobile */
  }

  .map-container {
    height: 320px; /* fixed height on mobile */
  }

  .eco-hero {
    padding: 20px 16px;
  }

  .eco-hero h1 {
    font-size: 24px;
  }

  .controls-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .controls-divider {
    display: none;
  }
}
</style>
