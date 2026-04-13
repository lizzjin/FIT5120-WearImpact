<template>
  <div class="eco-page">
    <Navbar />
    <div class="page-container">
      <section class="eco-hero">
        <h1>Local Eco-Shop Navigator</h1>
        <p>
          Find nearby second-hand shops, donation points, and textile recycling
          locations in your area.
        </p>
        <p v-if="isFallbackLocation" class="fallback-notice">
          Showing results near Melbourne CBD — allow location access for personalised results.
        </p>

        <!-- AC 1.1.1 — manual address input with Google Places Autocomplete -->
        <div class="address-search-row">
          <input
            ref="addressSearchInput"
            type="text"
            class="address-input"
            placeholder="Or type a suburb or address to search…"
            autocomplete="off"
          />
        </div>
      </section>

      <!-- Radius selector + type filters -->
      <div class="controls-row">
        <label class="radius-label">
          Search radius:
          <select v-model="radiusKm" @change="loadPlaces" class="radius-select">
            <option :value="2">2 km</option>
            <option :value="5">5 km</option>
            <option :value="10">10 km</option>
            <option :value="20">20 km</option>
          </select>
        </label>

        <div class="filter-row">
          <button
            v-for="typeOption in filterOptions"
            :key="typeOption.value"
            :class="{ active: activeFilter === typeOption.value }"
            @click="setFilter(typeOption.value)"
          >
            {{ typeOption.label }}
          </button>
        </div>
      </div>

      <!-- Non-loading status messages -->
      <div v-if="errorMessage" class="status-message error">{{ errorMessage }}</div>
      <div v-else-if="!isLoading && apiMessage" class="status-message info">{{ apiMessage }}</div>

      <!-- Main layout: list + map -->
      <div class="content-layout">
        <!-- Results list -->
        <div class="results-section">
          <!-- Skeleton cards shown while loading (replaces plain text spinner) -->
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
            <p
              v-if="filteredPlaces.length === 0 && !errorMessage && !apiMessage"
              class="status-message"
            >
              No results match the selected filter.
            </p>
            <LocationCard
              v-for="place in filteredPlaces"
              :key="place.place_id"
              :place="place"
              :is-selected="selectedPlaceId === place.place_id"
              @select="handleCardSelect(place)"
            />
          </template>
        </div>

        <!-- Google Map + details panel -->
        <div class="map-section">
          <!-- Map container — filled by Google Maps SDK on mount -->
          <div ref="mapContainer" class="map-container">
            <!-- Shown only when the SDK fails to load (no key, network error) -->
            <div v-if="mapLoadError" class="map-error">
              <p>🗺️ Map unavailable</p>
              <p class="map-error-detail">{{ mapLoadError }}</p>
            </div>
          </div>

          <!-- Place details panel — appears below the map when a card / marker is selected -->
          <transition name="slide-up">
            <div v-if="selectedDetails" class="details-panel">
              <button class="details-close" @click="clearSelection" aria-label="Close details">✕</button>

              <h3>{{ selectedDetails.name }}</h3>
              <span class="details-type-badge" :class="selectedDetails.type">
                {{ typeLabel(selectedDetails.type) }}
              </span>

              <!-- Loading skeleton while fetching full details from backend -->
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

                <!-- AC 1.2.1 / 1.2.2 — travel mode + inline directions -->
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
                  Get Directions
                </button>

                <!-- Route result: distance + estimated time (AC 1.2.2) -->
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Navbar from '../components/Navbar.vue'
import LocationCard from '../components/LocationCard.vue'
import { Car, PersonStanding, Bus, Route, Clock } from 'lucide-vue-next'
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

const isLoading = ref(false)
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
  { label: 'All',         value: 'all' },
  { label: 'Second-hand', value: 'second_hand_shop' },
  { label: 'Donation',    value: 'donation_point' },
  { label: 'Recycling',   value: 'recycling' },
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
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

/* Hero */
.eco-hero {
  background: #edf5ef;
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 24px;
  text-align: center;
}

.eco-hero h1 {
  font-size: 48px;
  color: #0f172a;
  margin-bottom: 12px;
}

.eco-hero p {
  font-size: 18px;
  color: #475569;
  line-height: 1.6;
  max-width: 760px;
  margin: 0 auto 8px;
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
  margin-top: 18px;
  display: flex;
  justify-content: center;
}

.address-input {
  width: 100%;
  max-width: 520px;
  padding: 12px 18px;
  border: 2px solid #d1d5db;
  border-radius: 999px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: white;
}

.address-input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.12);
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
  border-color: #16a34a;
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
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.radius-label {
  font-weight: 600;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 8px;
}

.radius-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

.filter-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-row button {
  padding: 9px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
}

.filter-row button.active {
  background: #16a34a;
  color: white;
  border-color: #16a34a;
}

/* Status messages */
.status-message {
  margin-bottom: 20px;
  font-weight: 600;
  color: #334155;
}

.status-message.error { color: #b91c1c; }
.status-message.info  { color: #92400e; }

/* Main layout */
.content-layout {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 24px;
  align-items: start;
}

.results-section {
  display: grid;
  gap: 18px;
}

/* Map area */
.map-section {
  position: sticky;
  top: 24px;
}

.map-container {
  width: 100%;
  height: 500px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  background: #e2e8f0;
  /* Flex layout so the error message centres inside the container */
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

/* Details panel */
.details-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 24px;
  margin-top: 16px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
  position: relative;
}

.details-close {
  position: absolute;
  top: 14px;
  right: 14px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #64748b;
  line-height: 1;
}

.details-close:hover { color: #0f172a; }

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

/* Responsive */
@media (max-width: 900px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .map-section {
    position: static;
    /* On mobile, show map above the list */
    order: -1;
  }

  .eco-hero h1 {
    font-size: 34px;
  }
}
</style>
