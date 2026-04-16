<template>
  <div class="eco-page">
    <Navbar />
    <div class="map-viewport">

      <!-- ── Left sidebar overlay ── -->
      <aside class="sidebar">
        <!-- Compact page header -->
        <div class="sidebar-header">
          <p class="sidebar-eyebrow">NEARBY ECO-LOCATIONS</p>
          <h2 class="sidebar-title">Find Eco-Friendly Fashion Near You</h2>
          <p class="sidebar-subtitle">
            Discover second-hand shops, donation points, and textile recycling near you.
          </p>
        </div>

        <!-- Address search -->
        <div class="address-search-row">
          <div class="address-input-wrap">
            <Search class="address-search-icon" :size="16" :stroke-width="2" />
            <input
              ref="addressSearchInput"
              type="text"
              class="address-input"
              placeholder="Type a suburb or address to search…"
              autocomplete="off"
              @input="handleAddressInput"
              @focus="onAddressFocus"
              @blur="onAddressBlur"
              @keydown.down.prevent="highlightSuggestionDown"
              @keydown.up.prevent="highlightSuggestionUp"
              @keydown.esc.prevent="clearAddressSuggestions"
              @keydown.enter.prevent="searchAddress"
            />
            <div
              v-if="showAddressSuggestions && (addressSuggestions.length > 0 || addressSuggestionsLoading)"
              class="address-suggestion-panel"
            >
              <div v-if="addressSuggestionsLoading" class="address-suggestion-loading">
                Searching addresses...
              </div>
              <button
                v-for="(suggestion, index) in addressSuggestions"
                v-else
                :key="suggestion.id"
                class="address-suggestion-item"
                :class="{ active: highlightedSuggestionIndex === index }"
                type="button"
                @mousedown.prevent="applyAddressSuggestion(suggestion)"
              >
                <span class="address-suggestion-title">{{ suggestion.title }}</span>
                <span class="address-suggestion-subtitle">{{ suggestion.subtitle }}</span>
              </button>
            </div>
          </div>
        </div>

        <p v-if="isFallbackLocation" class="fallback-notice">
          Showing results near Melbourne CBD — allow location access for personalised results.
        </p>

        <!-- Radius + filter controls -->
        <div class="controls-row">
          <label class="radius-label">
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
          <div class="filter-row">
            <button
              v-for="typeOption in filterOptions"
              :key="typeOption.value"
              class="filter-btn"
              :class="{ active: activeFilter === typeOption.value }"
              :aria-pressed="activeFilter === typeOption.value"
              @click="setFilter(typeOption.value)"
            >
              <span v-if="typeOption.color" class="filter-dot" :style="{ background: typeOption.color }"></span>
              {{ typeOption.label }}
            </button>
          </div>
        </div>

        <!-- Status messages -->
        <div v-if="errorMessage" class="status-message error">{{ errorMessage }}</div>
        <div v-else-if="!isLoading && apiMessage" class="status-message info">{{ apiMessage }}</div>

        <!-- Results list (scrollable) -->
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
              v-if="
                filteredPlaces.length === 0 &&
                !errorMessage &&
                !apiMessage &&
                hasSearched
              "
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
                  <button
                    class="details-close"
                    @click="clearSelection"
                    aria-label="Close details"
                  >
                    <X :size="18" :stroke-width="2.5" />
                  </button>

                  <h3>{{ selectedDetails.name }}</h3>
                  <span
                    class="details-type-badge"
                    :class="selectedDetails.type"
                  >
                    {{ typeLabel(selectedDetails.type) }}
                  </span>

                  <div v-if="detailsLoading" class="details-loading">
                    Loading details…
                  </div>

                  <template v-else>
                    <p v-if="selectedDetails.address">
                      <strong>Address:</strong> {{ selectedDetails.address }}
                    </p>

                    <div
                      v-if="selectedDetails.opening_hours?.length"
                      class="details-section"
                    >
                      <strong>Opening Hours:</strong>
                      <ul class="hours-list">
                        <li
                          v-for="line in selectedDetails.opening_hours"
                          :key="line"
                        >
                          {{ line }}
                        </li>
                      </ul>
                    </div>

                    <p v-if="selectedDetails.phone">
                      <strong>Phone:</strong>
                      <a :href="`tel:${selectedDetails.phone}`">{{
                        selectedDetails.phone
                      }}</a>
                    </p>

                    <p v-if="selectedDetails.website">
                      <strong>Website:</strong>
                      <a
                        :href="selectedDetails.website"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {{ selectedDetails.website }}
                      </a>
                    </p>

                    <p v-if="detailsError" class="details-error">
                      {{ detailsError }}
                    </p>

                    <div class="travel-mode-row">
                      <button
                        v-for="mode in travelModes"
                        :key="mode.value"
                        :class="{ active: travelMode === mode.value }"
                        class="mode-btn"
                        @click="travelMode = mode.value"
                      >
                        <component
                          :is="mode.icon"
                          :size="15"
                          :stroke-width="2"
                        />
                        {{ mode.label }}
                      </button>
                    </div>

                    <button
                      class="directions-btn"
                      @click="getDirections(selectedDetails)"
                    >
                      <Navigation2 :size="15" :stroke-width="2" />
                      Get Directions
                    </button>

                    <div v-if="routeInfo" class="route-info">
                      <span class="route-stat">
                        <Route :size="14" :stroke-width="2.2" />
                        {{ routeInfo.distance }}
                      </span>
                      <span class="route-divider">·</span>
                      <span class="route-stat">
                        <Clock :size="14" :stroke-width="2.2" />
                        {{ routeInfo.duration }}
                      </span>
                    </div>
                  </template>
                </div>
              </transition>
            </template>
          </template>
        </div>
      </aside>

      <!-- ── Full-screen map ── -->
      <div class="map-section">
        <button
          v-if="userLat !== null && userLng !== null"
          class="map-recenter-btn"
          type="button"
          @click="recenterToUser"
        >
          Recenter to My Location
        </button>
        <div ref="mapContainer" class="map-container">
          <div v-if="mapLoadError" class="map-error">
            <p>🗺️ Map unavailable</p>
            <p class="map-error-detail">{{ mapLoadError }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  watch,
  nextTick,
} from "vue";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import Navbar from "../components/Navbar.vue";
import LocationCard from "../components/LocationCard.vue";
import {
  CarFront,
  Footprints,
  BusFront,
  Route,
  Clock,
  Search,
  X,
  Navigation2,
  ChevronDown,
} from "lucide-vue-next";
import {
  getUserCoordinates,
  fetchNearbyPlaces,
  fetchPlaceDetails,
} from "../services/locationService";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const mapContainer = ref(null);
const mapLoadError = ref("");

const isLoading = ref(true); // true from the start so skeleton shows immediately
const hasSearched = ref(false); // flips to true after the first loadPlaces() completes
const errorMessage = ref("");
const apiMessage = ref("");
const isFallbackLocation = ref(false);

const userLat = ref(null);
const userLng = ref(null);
const radiusKm = ref(5);

const allPlaces = ref([]);
const activeFilter = ref("all");

const selectedPlaceId = ref(null);
const selectedDetails = ref(null);
const detailsLoading = ref(false);
const detailsError = ref("");
const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || "";
const mapboxStyleUrl =
  import.meta.env.VITE_MAPBOX_STYLE_URL || "mapbox://styles/mapbox/streets-v12";

// Manual address search input element ref.
const addressSearchInput = ref(null);
const addressSuggestions = ref([]);
const showAddressSuggestions = ref(false);
const addressSuggestionsLoading = ref(false);
const highlightedSuggestionIndex = ref(-1);
let addressSuggestDebounceTimer = null;
let addressSuggestAbortController = null;
const addressSearchSuggestTypes =
  "poi,address,street,place,postcode,locality,neighborhood";
const SEARCHBOX_SUGGEST_MIN_LIMIT = 1;
const SEARCHBOX_SUGGEST_MAX_LIMIT = 10;
const SEARCHBOX_DEFAULT_SUGGEST_LIMIT = 8;
let addressSearchSessionToken = "";

// Route info shown in the details panel after Get Directions (AC 1.2.2)
const routeInfo = ref(null); // { distance: '5.2 km', duration: '12 mins' } or null

// Travel mode selection for directions
const travelMode = ref("DRIVING");

// Map objects — kept outside reactive state to avoid Vue proxying DOM objects.
let mapInstance = null;
let activePopup = null;
let routeAnimationFrame = null;
let lastDashAnimationTimestamp = 0;
let dashSequenceIndex = 0;
const markerMap = {}; // place_id -> mapboxgl.Marker
let userMarker = null;  // DOM-based user location marker


const ROUTE_SOURCE_ID = "eco-route-source";
const ROUTE_GLOW_LAYER_ID = "eco-route-glow-layer";
const ROUTE_MAIN_LAYER_ID = "eco-route-main-layer";
const ROUTE_DASH_LAYER_ID = "eco-route-dash-layer";

const ROUTE_DASH_SEQUENCES = {
  DRIVING: [
    [0, 4, 3],
    [0.4, 4, 2.6],
    [0.8, 4, 2.2],
    [1.2, 4, 1.8],
    [1.6, 4, 1.4],
    [2, 4, 1],
    [2.4, 4, 0.6],
    [2.8, 4, 0.2],
  ],
  WALKING: [
    [0, 2.2, 2.2],
    [0.3, 2.2, 1.9],
    [0.6, 2.2, 1.6],
    [0.9, 2.2, 1.3],
    [1.2, 2.2, 1],
    [1.5, 2.2, 0.7],
  ],
  TRANSIT: [
    [0, 5, 3],
    [0.5, 5, 2.5],
    [1, 5, 2],
    [1.5, 5, 1.5],
    [2, 5, 1],
  ],
};

let activeDashSequence = ROUTE_DASH_SEQUENCES.DRIVING;

// ---------------------------------------------------------------------------
// Filter options — values match the 'type' field returned by the backend
// ---------------------------------------------------------------------------

const filterOptions = [
  { label: "All", value: "all", color: null },
  { label: "Second-hand", value: "second_hand_shop", color: "#16a34a" },
  { label: "Donation", value: "donation_point", color: "#2563eb" },
  { label: "Recycling", value: "recycling", color: "#d97706" },
];

const travelModes = [
  { label: "Drive", value: "DRIVING", icon: CarFront },
  { label: "Walk", value: "WALKING", icon: Footprints },
  { label: "Transit", value: "TRANSIT", icon: BusFront },
];

const filteredPlaces = computed(() => {
  if (activeFilter.value === "all") return allPlaces.value;
  return allPlaces.value.filter((p) => p.type === activeFilter.value);
});

// ---------------------------------------------------------------------------
// Marker icon helpers
// ---------------------------------------------------------------------------

// Colour per eco-place type — also used in the legend / filter chips
const TYPE_COLOURS = {
  second_hand_shop: "#16a34a",
  donation_point: "#2563eb",
  recycling: "#d97706",
};

/**
 * Escape text before injecting it into popup HTML.
 */
function escapeHtml(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function typeLabel(type) {
  return (
    {
      second_hand_shop: "Second-hand",
      donation_point: "Donation",
      recycling: "Recycling",
    }[type] || type
  );
}

function createEmptyRouteGeoJson() {
  return {
    type: "FeatureCollection",
    features: [],
  };
}

function createRouteGeoJson(coordinates) {
  if (!coordinates || coordinates.length === 0) {
    return createEmptyRouteGeoJson();
  }

  return {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: {
          type: "LineString",
          coordinates,
        },
      },
    ],
  };
}


function ensureUserMarker() {
  if (!mapInstance || userLat.value === null || userLng.value === null) return;

  if (userMarker) {
    userMarker.setLngLat([userLng.value, userLat.value]);
    return;
  }

  const el = document.createElement("div");
  el.className = "eco-user-marker";

  const dot = document.createElement("div");
  dot.className = "eco-user-dot";
  el.appendChild(dot);

  userMarker = new mapboxgl.Marker({ element: el, anchor: "center" })
    .setLngLat([userLng.value, userLat.value])
    .addTo(mapInstance);
}

function isStyleLoadError(rawMessage = "") {
  const message = rawMessage.toLowerCase();
  return (
    message.includes("style") ||
    message.includes("access token") ||
    message.includes("unauthorized") ||
    message.includes("forbidden") ||
    message.includes("not found")
  );
}

function initMap(lat, lng) {
  if (!mapContainer.value) return;

  if (!mapboxToken) {
    mapLoadError.value = "Add VITE_MAPBOX_ACCESS_TOKEN to frontend/.env.local";
    return;
  }

  mapboxgl.accessToken = mapboxToken;
  mapInstance = new mapboxgl.Map({
    container: mapContainer.value,
    style: mapboxStyleUrl,
    center: [lng, lat],
    zoom: 13.8,
  });

  mapInstance.addControl(new mapboxgl.NavigationControl(), "top-right");

  mapInstance.on("load", () => {
    mapLoadError.value = "";
    ensureRouteLayers();
    syncUserMarkerPosition();
    if (filteredPlaces.value.length > 0) {
      addPlaceMarkers(filteredPlaces.value);
    }
  });

  mapInstance.on("error", (event) => {
    const rawMessage = event?.error?.message || "";
    if (isStyleLoadError(rawMessage)) {
      mapLoadError.value =
        "Map style failed to load. Check your Mapbox token and style URL.";
      return;
    }
    // Non-style map errors should not hide the map with a global unavailable message.
  });

  syncUserMarkerPosition();
}

// ---------------------------------------------------------------------------
// Map marker management
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Address search — Mapbox Geocoding API (manual input + Enter)
// ---------------------------------------------------------------------------

function clearAddressSuggestions() {
  showAddressSuggestions.value = false;
  addressSuggestions.value = [];
  highlightedSuggestionIndex.value = -1;
}

function createAddressSearchSessionToken() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  return `wearimpact-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function ensureAddressSearchSessionToken() {
  if (!addressSearchSessionToken) {
    addressSearchSessionToken = createAddressSearchSessionToken();
  }
}

function resetAddressSearchSessionToken() {
  addressSearchSessionToken = createAddressSearchSessionToken();
}

function normaliseSuggestion(suggestion) {
  const fullText =
    suggestion.full_address ||
    suggestion.place_formatted ||
    suggestion.name ||
    "";
  return {
    id: suggestion.mapbox_id || suggestion.name || fullText,
    title: suggestion.name || fullText,
    subtitle:
      suggestion.full_address || suggestion.place_formatted || "Australia",
    placeName: fullText || suggestion.name || "",
    mapboxId: suggestion.mapbox_id || "",
  };
}

function clampSearchBoxSuggestLimit(limit) {
  const safeLimit = Number.isFinite(limit)
    ? Math.floor(limit)
    : SEARCHBOX_DEFAULT_SUGGEST_LIMIT;
  return Math.max(
    SEARCHBOX_SUGGEST_MIN_LIMIT,
    Math.min(SEARCHBOX_SUGGEST_MAX_LIMIT, safeLimit),
  );
}

async function fetchSearchBoxSuggestions(
  keyword,
  { limit = SEARCHBOX_DEFAULT_SUGGEST_LIMIT, signal } = {},
) {
  ensureAddressSearchSessionToken();
  const endpoint = "https://api.mapbox.com/search/searchbox/v1/suggest";
  const safeLimit = clampSearchBoxSuggestLimit(limit);
  const params = new URLSearchParams({
    access_token: mapboxToken,
    q: keyword,
    country: "AU",
    language: "en",
    limit: String(safeLimit),
    session_token: addressSearchSessionToken,
    types: addressSearchSuggestTypes,
  });

  if (userLat.value !== null && userLng.value !== null) {
    params.set("proximity", `${userLng.value},${userLat.value}`);
  }

  const response = await fetch(`${endpoint}?${params.toString()}`, { signal });
  if (!response.ok) {
    let errorDetail = "";
    try {
      const errorBody = await response.json();
      errorDetail =
        errorBody?.message?.error ||
        errorBody?.message ||
        errorBody?.error ||
        "";
    } catch {
      errorDetail = "";
    }
    const suffix = errorDetail ? `: ${errorDetail}` : "";
    throw new Error(
      `Address suggestion failed (HTTP ${response.status})${suffix}`,
    );
  }

  const payload = await response.json();
  return payload.suggestions || [];
}

async function fetchSearchBoxRetrieve(mapboxId, { signal } = {}) {
  ensureAddressSearchSessionToken();
  const endpoint = `https://api.mapbox.com/search/searchbox/v1/retrieve/${encodeURIComponent(mapboxId)}`;
  const params = new URLSearchParams({
    access_token: mapboxToken,
    session_token: addressSearchSessionToken,
  });

  const response = await fetch(`${endpoint}?${params.toString()}`, { signal });
  if (!response.ok) {
    let errorDetail = "";
    try {
      const errorBody = await response.json();
      errorDetail =
        errorBody?.message?.error ||
        errorBody?.message ||
        errorBody?.error ||
        "";
    } catch {
      errorDetail = "";
    }
    const suffix = errorDetail ? `: ${errorDetail}` : "";
    throw new Error(
      `Address retrieve failed (HTTP ${response.status})${suffix}`,
    );
  }

  const payload = await response.json();
  const feature = payload.features?.[0];
  const coordinates = feature?.geometry?.coordinates;
  if (!Array.isArray(coordinates) || coordinates.length < 2) {
    return null;
  }

  return {
    lng: coordinates[0],
    lat: coordinates[1],
    fullAddress:
      feature?.properties?.full_address || feature?.properties?.name || "",
  };
}

async function fetchAddressSuggestions(keyword) {
  if (!mapboxToken) return;

  if (addressSuggestAbortController) {
    addressSuggestAbortController.abort();
  }
  addressSuggestAbortController = new AbortController();
  addressSuggestionsLoading.value = true;

  try {
    const suggestions = await fetchSearchBoxSuggestions(keyword, {
      limit: SEARCHBOX_DEFAULT_SUGGEST_LIMIT,
      signal: addressSuggestAbortController.signal,
    });
    addressSuggestions.value = suggestions.map(normaliseSuggestion);
    showAddressSuggestions.value = addressSuggestions.value.length > 0;
    highlightedSuggestionIndex.value =
      addressSuggestions.value.length > 0 ? 0 : -1;
  } catch (err) {
    if (err.name !== "AbortError") {
      clearAddressSuggestions();
    }
  } finally {
    addressSuggestionsLoading.value = false;
  }
}

function handleAddressInput() {
  const keyword = addressSearchInput.value?.value?.trim() || "";
  ensureAddressSearchSessionToken();

  if (addressSuggestDebounceTimer) {
    window.clearTimeout(addressSuggestDebounceTimer);
  }

  if (!keyword || keyword.length < 2) {
    if (addressSuggestAbortController) {
      addressSuggestAbortController.abort();
    }
    clearAddressSuggestions();
    return;
  }

  addressSuggestDebounceTimer = window.setTimeout(() => {
    fetchAddressSuggestions(keyword);
  }, 220);
}

function onAddressFocus() {
  ensureAddressSearchSessionToken();
  if (addressSuggestions.value.length > 0) {
    showAddressSuggestions.value = true;
  }
}

function onAddressBlur() {
  window.setTimeout(() => {
    showAddressSuggestions.value = false;
  }, 120);
}

function highlightSuggestionDown() {
  if (addressSuggestions.value.length === 0) return;
  showAddressSuggestions.value = true;
  highlightedSuggestionIndex.value =
    (highlightedSuggestionIndex.value + 1 + addressSuggestions.value.length) %
    addressSuggestions.value.length;
}

function highlightSuggestionUp() {
  if (addressSuggestions.value.length === 0) return;
  showAddressSuggestions.value = true;
  highlightedSuggestionIndex.value =
    (highlightedSuggestionIndex.value - 1 + addressSuggestions.value.length) %
    addressSuggestions.value.length;
}

async function updateUserLocationAndSearch(lat, lng) {
  userLat.value = lat;
  userLng.value = lng;
  isFallbackLocation.value = false;

  if (mapInstance) {
    mapInstance.flyTo({ center: [lng, lat], zoom: 14.2, duration: 900 });
  }
  syncUserMarkerPosition();

  clearRoute();
  clearSelection();
  await loadPlaces();
}

async function applyAddressSuggestion(suggestion) {
  if (!suggestion) return;

  try {
    let resolved = null;

    if (suggestion.mapboxId) {
      resolved = await fetchSearchBoxRetrieve(suggestion.mapboxId);
    }

    if (!resolved && suggestion.placeName) {
      const fallbackData = await fetchMapboxGeocoding(suggestion.placeName, {
        limit: 1,
      });
      const fallbackTop = fallbackData.features?.[0];
      if (fallbackTop?.center?.length >= 2) {
        resolved = {
          lng: fallbackTop.center[0],
          lat: fallbackTop.center[1],
          fullAddress: fallbackTop.place_name || suggestion.placeName,
        };
      }
    }

    if (!resolved) {
      errorMessage.value =
        "Address not found. Try a different suburb or street.";
      return;
    }

    if (addressSearchInput.value) {
      addressSearchInput.value.value =
        resolved.fullAddress || suggestion.placeName || suggestion.title;
    }

    clearAddressSuggestions();
    await updateUserLocationAndSearch(resolved.lat, resolved.lng);
    resetAddressSearchSessionToken();
  } catch (err) {
    errorMessage.value =
      err.message || "Address search failed. Please try again.";
  }
}

async function searchAddress() {
  if (
    showAddressSuggestions.value &&
    highlightedSuggestionIndex.value >= 0 &&
    addressSuggestions.value[highlightedSuggestionIndex.value]
  ) {
    await applyAddressSuggestion(
      addressSuggestions.value[highlightedSuggestionIndex.value],
    );
    return;
  }

  const keyword = addressSearchInput.value?.value?.trim();
  if (!keyword) return;

  if (!mapboxToken) {
    errorMessage.value = "Address search requires VITE_MAPBOX_ACCESS_TOKEN.";
    return;
  }

  try {
    const suggestions = await fetchSearchBoxSuggestions(keyword, { limit: 1 });
    const topSuggestion = suggestions[0]
      ? normaliseSuggestion(suggestions[0])
      : null;

    if (topSuggestion) {
      await applyAddressSuggestion(topSuggestion);
      return;
    }

    const fallbackData = await fetchMapboxGeocoding(keyword, { limit: 1 });
    const fallbackTop = fallbackData.features?.[0];
    if (!fallbackTop?.center || fallbackTop.center.length < 2) {
      errorMessage.value =
        "Address not found. Try a different suburb or street.";
      return;
    }

    clearAddressSuggestions();
    await updateUserLocationAndSearch(
      fallbackTop.center[1],
      fallbackTop.center[0],
    );
    resetAddressSearchSessionToken();
  } catch (err) {
    errorMessage.value =
      err.message || "Address search failed. Please try again.";
  }
}

async function fetchMapboxGeocoding(keyword, { limit, signal } = {}) {
  const endpoint = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(keyword)}.json`;

  const params = new URLSearchParams({
    access_token: mapboxToken,
    country: "au",
    limit: String(limit || 5),
    autocomplete: "true",
    language: "en",
  });
  if (userLat.value !== null && userLng.value !== null) {
    params.set("proximity", `${userLng.value},${userLat.value}`);
  }

  const response = await fetch(`${endpoint}?${params.toString()}`, { signal });
  if (!response.ok) {
    let errorDetail = "";
    try {
      const errorBody = await response.json();
      errorDetail =
        errorBody?.message?.error ||
        errorBody?.message ||
        errorBody?.error ||
        "";
    } catch {
      errorDetail = "";
    }
    const suffix = errorDetail ? `: ${errorDetail}` : "";
    throw new Error(`Address search failed (HTTP ${response.status})${suffix}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Route helpers (AC 1.2.1 / 1.2.2)
// ---------------------------------------------------------------------------

function clearRoute() {
  stopRouteAnimation();
  if (mapInstance && mapInstance.getSource(ROUTE_SOURCE_ID)) {
    mapInstance.getSource(ROUTE_SOURCE_ID).setData(createEmptyRouteGeoJson());
  }
  routeInfo.value = null;
}

function closeActivePopup() {
  if (activePopup) {
    activePopup.remove();
    activePopup = null;
  }
}

/** Parse a #rrggbb hex string into an rgba() value for CSS custom properties. */
function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function createMarkerElement(colour) {
  const markerEl = document.createElement("button");
  markerEl.type = "button";
  markerEl.className = "eco-map-marker";
  markerEl.style.background = colour;
  // Supply the ring color as a CSS custom property for the box-shadow animation
  markerEl.style.setProperty("--ring-rgba", hexToRgba(colour, 0.55));

  const markerCore = document.createElement("span");
  markerCore.className = "eco-map-marker-core";
  markerEl.appendChild(markerCore);

  return markerEl;
}

function syncUserMarkerPosition() {
  if (!mapInstance) return;
  if (userLat.value === null || userLng.value === null) return;
  ensureUserMarker();
}

function requestCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported in this browser."));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      () => reject(new Error("Could not get your current location.")),
      {
        timeout: 12000,
        maximumAge: 0,
        enableHighAccuracy: true,
      },
    );
  });
}

async function recenterToUser() {
  if (!mapInstance) return;

  try {
    const coords = await requestCurrentLocation();
    userLat.value = coords.lat;
    userLng.value = coords.lng;
    isFallbackLocation.value = false;
    syncUserMarkerPosition();

    if (addressSearchInput.value) addressSearchInput.value.value = '';
    clearAddressSuggestions();

    mapInstance.flyTo({
      center: [coords.lng, coords.lat],
      zoom: 14.2,
      duration: 900,
      essential: true,
    });

    clearRoute();
    clearSelection();
    await loadPlaces();
  } catch (err) {
    errorMessage.value = err.message || "Unable to refresh current location.";
  }
}

function ensureRouteLayers() {
  if (!mapInstance || !mapInstance.isStyleLoaded()) return;

  if (!mapInstance.getSource(ROUTE_SOURCE_ID)) {
    mapInstance.addSource(ROUTE_SOURCE_ID, {
      type: "geojson",
      data: createEmptyRouteGeoJson(),
    });
  }

  if (!mapInstance.getLayer(ROUTE_GLOW_LAYER_ID)) {
    mapInstance.addLayer({
      id: ROUTE_GLOW_LAYER_ID,
      type: "line",
      source: ROUTE_SOURCE_ID,
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": "#16a34a",
        "line-width": 14,
        "line-opacity": 0.2,
        "line-blur": 1.2,
      },
    });
  }

  if (!mapInstance.getLayer(ROUTE_MAIN_LAYER_ID)) {
    mapInstance.addLayer({
      id: ROUTE_MAIN_LAYER_ID,
      type: "line",
      source: ROUTE_SOURCE_ID,
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": "#15803d",
        "line-width": 6,
        "line-opacity": 0.94,
      },
    });
  }

  if (!mapInstance.getLayer(ROUTE_DASH_LAYER_ID)) {
    mapInstance.addLayer({
      id: ROUTE_DASH_LAYER_ID,
      type: "line",
      source: ROUTE_SOURCE_ID,
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": "#dcfce7",
        "line-width": 3,
        "line-opacity": 0.95,
        "line-dasharray": ROUTE_DASH_SEQUENCES.DRIVING[0],
      },
    });
  }
}

function setRouteVisualStyle(mode) {
  if (!mapInstance) return;
  if (!mapInstance.getLayer(ROUTE_MAIN_LAYER_ID)) return;

  const visualMode = mode || "DRIVING";
  activeDashSequence =
    ROUTE_DASH_SEQUENCES[visualMode] || ROUTE_DASH_SEQUENCES.DRIVING;

  if (visualMode === "WALKING") {
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-color", "#2563eb");
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-width", 9);
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-opacity", 0.12);

    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-color", "#1d4ed8");
    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-width", 3.5);
    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-opacity", 0.9);

    mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-color", "#eff6ff");
    mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-width", 2.2);
    return;
  }

  if (visualMode === "TRANSIT") {
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-color", "#ea580c");
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-width", 12);
    mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-opacity", 0.2);

    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-color", "#f97316");
    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-width", 5);
    mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-opacity", 0.95);

    mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-color", "#ffedd5");
    mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-width", 3);
    return;
  }

  mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-color", "#16a34a");
  mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-width", 14);
  mapInstance.setPaintProperty(ROUTE_GLOW_LAYER_ID, "line-opacity", 0.2);

  mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-color", "#15803d");
  mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-width", 6);
  mapInstance.setPaintProperty(ROUTE_MAIN_LAYER_ID, "line-opacity", 0.94);

  mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-color", "#dcfce7");
  mapInstance.setPaintProperty(ROUTE_DASH_LAYER_ID, "line-width", 3);
}

function stopRouteAnimation() {
  if (routeAnimationFrame) {
    window.cancelAnimationFrame(routeAnimationFrame);
    routeAnimationFrame = null;
  }
  lastDashAnimationTimestamp = 0;
  dashSequenceIndex = 0;
}

function startRouteAnimation() {
  stopRouteAnimation();

  const animate = (timestamp) => {
    if (!mapInstance || !mapInstance.getLayer(ROUTE_DASH_LAYER_ID)) return;

    if (timestamp - lastDashAnimationTimestamp > 90) {
      dashSequenceIndex = (dashSequenceIndex + 1) % activeDashSequence.length;
      mapInstance.setPaintProperty(
        ROUTE_DASH_LAYER_ID,
        "line-dasharray",
        activeDashSequence[dashSequenceIndex],
      );
      lastDashAnimationTimestamp = timestamp;
    }

    routeAnimationFrame = window.requestAnimationFrame(animate);
  };

  routeAnimationFrame = window.requestAnimationFrame(animate);
}

function formatDistance(distanceMeters = 0) {
  const km = distanceMeters / 1000;
  if (km >= 10) return `${km.toFixed(0)} km`;
  return `${km.toFixed(1)} km`;
}

function formatDuration(durationSeconds = 0) {
  const totalMinutes = Math.round(durationSeconds / 60);
  if (totalMinutes < 60) return `${totalMinutes} mins`;

  const hours = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  if (mins === 0) return `${hours} hr`;
  return `${hours} hr ${mins} mins`;
}

function mapTravelModeToProfile(mode) {
  if (mode === "TRANSIT") return "driving";
  if (mode === "WALKING") return "walking";
  return "driving";
}

async function fetchDirectionsRoute(
  profile,
  originLng,
  originLat,
  destinationLng,
  destinationLat,
) {
  const endpoint = `https://api.mapbox.com/directions/v5/mapbox/${profile}/${originLng},${originLat};${destinationLng},${destinationLat}`;
  const params = new URLSearchParams({
    access_token: mapboxToken,
    alternatives: "false",
    geometries: "geojson",
    overview: "full",
    steps: "false",
  });

  const response = await fetch(`${endpoint}?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Directions request failed (HTTP ${response.status})`);
  }

  const payload = await response.json();
  return payload.routes?.[0] || null;
}

function fitRouteBounds(routeCoordinates) {
  if (!mapInstance || routeCoordinates.length === 0) return;

  const bounds = routeCoordinates.reduce(
    (acc, coord) => acc.extend(coord),
    new mapboxgl.LngLatBounds(routeCoordinates[0], routeCoordinates[0]),
  );

  mapInstance.fitBounds(bounds, {
    padding: { top: 80, right: 80, bottom: 80, left: 420 },
    duration: 1000,
  });
}

function drawRouteOnMap(routeCoordinates, mode) {
  if (!mapInstance) return;

  ensureRouteLayers();
  setRouteVisualStyle(mode);

  const source = mapInstance.getSource(ROUTE_SOURCE_ID);

  if (source) {
    source.setData(createRouteGeoJson(routeCoordinates));
    startRouteAnimation();
    fitRouteBounds(routeCoordinates);
  }
}

function addPlaceMarkers(places) {
  if (!mapInstance) return;

  // Remove all existing place markers from the map
  Object.values(markerMap).forEach((m) => m.remove());
  Object.keys(markerMap).forEach((k) => delete markerMap[k]);
  closeActivePopup();

  // Keep user location marker anchored to the latest geolocation.
  syncUserMarkerPosition();

  places.forEach((place) => {
    const colour = TYPE_COLOURS[place.type] || "#16a34a";
    const markerElement = createMarkerElement(colour);
    const marker = new mapboxgl.Marker({
      element: markerElement,
      anchor: "bottom",
    })
      .setLngLat([place.lng, place.lat])
      .addTo(mapInstance);

    const popup = new mapboxgl.Popup({
      offset: 20,
      closeButton: false,
    }).setHTML(
      `<div class="eco-map-popup">
        <strong>${escapeHtml(place.name)}</strong>
        <span>${place.distance_km} km away</span>
      </div>`,
    );

    markerElement.addEventListener("click", () => {
      closeActivePopup();
      popup.setLngLat([place.lng, place.lat]).addTo(mapInstance);
      activePopup = popup;
      handleCardSelect(place);
    });

    markerMap[place.place_id] = marker;
  });
}

// ---------------------------------------------------------------------------
// Data loading — Step 2
// ---------------------------------------------------------------------------

async function loadPlaces() {
  isLoading.value = true;
  errorMessage.value = "";
  apiMessage.value = "";
  allPlaces.value = [];

  try {
    const data = await fetchNearbyPlaces({
      lat: userLat.value,
      lng: userLng.value,
      radiusKm: radiusKm.value,
    });

    allPlaces.value = data.results || [];
    apiMessage.value = data.message || "";

    if (mapInstance) {
      addPlaceMarkers(allPlaces.value);
    }
  } catch (err) {
    errorMessage.value =
      err.message || "Failed to load eco-shops. Please try again.";
  } finally {
    isLoading.value = false;
    hasSearched.value = true;
  }
}

// ---------------------------------------------------------------------------
// Card / marker selection → fetch place details (Step 4)
// ---------------------------------------------------------------------------

async function handleCardSelect(place) {
  // Second click on the same card collapses the panel
  if (selectedPlaceId.value === place.place_id) {
    clearSelection();
    return;
  }

  selectedPlaceId.value = place.place_id;
  // Immediately show an optimistic stub so the panel appears without delay
  selectedDetails.value = { name: place.name, type: place.type };
  detailsLoading.value = true;
  detailsError.value = "";

  // Pan map to the selected marker
  if (mapInstance) {
    mapInstance.flyTo({
      center: [place.lng, place.lat],
      zoom: 14.6,
      duration: 700,
    });
  }

  try {
    const details = await fetchPlaceDetails(place.place_id);
    selectedDetails.value = { ...details, lat: place.lat, lng: place.lng };
  } catch (err) {
    detailsError.value = "Could not load details. Please try again.";
  } finally {
    detailsLoading.value = false;
    // Scroll the details panel into view — block:'nearest' means minimum scroll only
    await nextTick();
    const panel = document.querySelector(".details-panel");
    if (panel) panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function clearSelection() {
  selectedPlaceId.value = null;
  selectedDetails.value = null;
  detailsError.value = "";
  closeActivePopup();
  clearRoute();
}

// ---------------------------------------------------------------------------
// Directions — Step 5 (Mapbox Directions with animated route line)
// ---------------------------------------------------------------------------

async function getDirections(place) {
  if (!place?.lat || !place?.lng) return;

  if (!mapboxToken) {
    detailsError.value = "Directions require VITE_MAPBOX_ACCESS_TOKEN.";
    return;
  }

  // Clear any previous route before drawing a new one
  clearRoute();
  detailsError.value = "";

  try {
    const profile = mapTravelModeToProfile(travelMode.value);
    const route = await fetchDirectionsRoute(
      profile,
      userLng.value,
      userLat.value,
      place.lng,
      place.lat,
    );

    const routeCoordinates = route?.geometry?.coordinates || [];

    if (!route || routeCoordinates.length === 0) {
      throw new Error("No route found for the selected destination.");
    }

    drawRouteOnMap(routeCoordinates, travelMode.value);

    const leg = route.legs?.[0];

    routeInfo.value = {
      distance: formatDistance(leg?.distance),
      duration: formatDuration(leg?.duration),
    };
  } catch (err) {
    detailsError.value =
      err.message || "Could not generate directions. Please try again.";
    routeInfo.value = null;
  }
}

// ---------------------------------------------------------------------------
// Filter
// ---------------------------------------------------------------------------

function setFilter(value) {
  activeFilter.value = value;
}

// Sync map markers with the active filter so hidden types don't appear
watch(filteredPlaces, (places) => {
  if (mapInstance) addPlaceMarkers(places);
});

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

onMounted(async () => {
  // Step 1 — Obtain user GPS coordinates (or fall back to Melbourne CBD)
  const coords = await getUserCoordinates();
  userLat.value = coords.lat;
  userLng.value = coords.lng;
  isFallbackLocation.value = coords.isFallback;

  // Step 3 — Initialise Mapbox map (frontend rendering only).
  initMap(coords.lat, coords.lng);

  // Step 2 — Search nearby eco-shops via backend
  await loadPlaces();

  if (mapInstance && allPlaces.value.length > 0) {
    addPlaceMarkers(filteredPlaces.value);
  }
});

onBeforeUnmount(() => {
  stopRouteAnimation();
  if (addressSuggestDebounceTimer) {
    window.clearTimeout(addressSuggestDebounceTimer);
    addressSuggestDebounceTimer = null;
  }
  if (addressSuggestAbortController) {
    addressSuggestAbortController.abort();
    addressSuggestAbortController = null;
  }
  closeActivePopup();

  Object.values(markerMap).forEach((marker) => marker.remove());
  Object.keys(markerMap).forEach((key) => delete markerMap[key]);

  if (userMarker) {
    userMarker.remove();
    userMarker = null;
  }

  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
});
</script>

<style scoped>
/* ── Page shell ─────────────────────────────────────────────────────────── */
.eco-page {
  background: #ffffff;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Remove the navbar's bottom margin so there's no gap above the map */
:deep(.navbar) {
  margin-bottom: 0;
}

/* Full-bleed map viewport — fills everything below the navbar */
.map-viewport {
  flex: 1;
  min-height: 0;
  position: relative;
}

/* ── Left sidebar overlay (Google Maps style) ───────────────────────────── */
.sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 420px;
  z-index: 10;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.12);
}

/* Compact sidebar header */
.sidebar-header {
  padding: 20px 20px 4px;
  flex-shrink: 0;
  border-bottom: 1px solid #f0f4f0;
}

.sidebar-eyebrow {
  font-size: 10px;
  font-weight: 700;
  color: #16a34a;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 4px;
}

.sidebar-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
  line-height: 1.25;
}

.sidebar-subtitle {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
  margin: 0;
}

.fallback-notice {
  font-size: 13px !important;
  color: #92400e !important;
  background: #fef3c7;
  border-radius: 8px;
  padding: 6px 14px;
  margin: 0 16px 4px;
  flex-shrink: 0;
}

/* ── Skeleton loading cards ───────────────────────────────────────────── */
@keyframes shimmer {
  0% {
    background-position: -600px 0;
  }
  100% {
    background-position: 600px 0;
  }
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
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
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

.skeleton-title {
  height: 18px;
  width: 55%;
}
.skeleton-badge {
  height: 22px;
  width: 22%;
  border-radius: 999px;
  flex-shrink: 0;
}
.skeleton-distance {
  height: 14px;
  width: 35%;
  margin-bottom: 10px;
}
.skeleton-hint {
  height: 12px;
  width: 48%;
}

/* Address search bar */
.address-search-row {
  padding: 12px 16px 4px;
  flex-shrink: 0;
}

.address-input-wrap {
  position: relative;
  width: 100%;
  z-index: 12;
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
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
  background: white;
  box-sizing: border-box;
}

.address-input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
}

.address-suggestion-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  border: 1px solid #dbe4ee;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.14);
  overflow: hidden;
  max-height: 280px;
  overflow-y: auto;
}

.address-suggestion-loading {
  padding: 12px 14px;
  font-size: 13px;
  color: #64748b;
  text-align: left;
}

.address-suggestion-item {
  width: 100%;
  border: none;
  border-bottom: 1px solid #eef2f7;
  background: #ffffff;
  cursor: pointer;
  text-align: left;
  padding: 11px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.address-suggestion-item:last-child {
  border-bottom: none;
}

.address-suggestion-item:hover,
.address-suggestion-item.active {
  background: #f0fdf4;
}

.address-suggestion-title {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.35;
}

.address-suggestion-subtitle {
  font-size: 12px;
  color: #64748b;
  line-height: 1.35;
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
  transition:
    background 0.15s,
    border-color 0.15s;
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

/* Controls — lives inside the sidebar, no card chrome */
.controls-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 16px 10px;
  flex-shrink: 0;
  border-bottom: 1px solid #f0f4f0;
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

.filter-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  width: 100%;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
  transition:
    background 0.15s,
    color 0.15s,
    border-color 0.15s;
}

.filter-btn.active {
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

/* Status messages — inside sidebar */
.status-message {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  flex-shrink: 0;
}

.status-message.error {
  color: #b91c1c;
}
.status-message.info {
  color: #92400e;
}

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

/* Results list — scrolls independently inside sidebar */
.results-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 12px 16px;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
}

/* Full-screen map section */
.map-section {
  position: absolute;
  inset: 0;
}

/* Recenter button — offset right of sidebar */
.map-recenter-btn {
  position: absolute;
  top: 14px;
  left: calc(420px + 14px);
  z-index: 2;
  border: 1px solid #bbf7d0;
  background: rgba(240, 253, 244, 0.97);
  color: #166534;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 14px rgba(22, 163, 74, 0.18);
  transition:
    transform 120ms ease,
    box-shadow 120ms ease;
}

.map-recenter-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 16px rgba(22, 163, 74, 0.22);
}

.map-container {
  width: 100%;
  height: 100%;
  border-radius: 0;
  overflow: hidden;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.mapboxgl-ctrl-group) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.18);
}

:deep(.mapboxgl-ctrl-group button) {
  width: 34px;
  height: 34px;
}

:deep(.eco-map-marker) {
  width: 22px;
  height: 22px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
  outline: none;
}

:deep(.eco-map-marker-core) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
}

:deep(.eco-map-marker:hover) {
  transform: scale(1.08);
}

:deep(.mapboxgl-popup-content) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.16);
  padding: 0;
}

:deep(.mapboxgl-popup-tip) {
  border-top-color: #ffffff !important;
}

:deep(.eco-map-popup) {
  min-width: 170px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

:deep(.eco-map-popup strong) {
  font-size: 13px;
  color: #0f172a;
}

:deep(.eco-map-popup span) {
  font-size: 12px;
  color: #64748b;
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
  transition:
    background 150ms ease,
    color 150ms ease;
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

.details-type-badge.second_hand_shop {
  background: #dcfce7;
  color: #166534;
}
.details-type-badge.donation_point {
  background: #dbeafe;
  color: #1e40af;
}
.details-type-badge.recycling {
  background: #fef3c7;
  color: #92400e;
}

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

.directions-btn:hover {
  background: #15803d;
}

/* Slide-up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Responsive — sidebar slides to bottom on mobile */
@media (max-width: 768px) {
  .eco-page {
    height: 100vh;
    overflow: hidden;
  }

  .map-viewport {
    display: flex;
    flex-direction: column;
  }

  .sidebar {
    position: relative;
    width: 100%;
    height: 50vh;
    box-shadow: 0 -4px 24px rgba(15, 23, 42, 0.1);
    order: 2;
  }

  .map-section {
    position: relative;
    flex: 1;
    min-height: 0;
    order: 1;
  }

  .map-container {
    position: absolute;
    inset: 0;
  }

  .map-recenter-btn {
    top: 10px;
    left: 10px;
    font-size: 11px;
    padding: 6px 10px;
  }

  .address-suggestion-panel {
    max-height: 200px;
  }
}
</style>

<!-- Non-scoped: @keyframes must be global — scoped blocks hash the name and break animation references -->
<style>
/*
 * box-shadow spread-radius animation:
 * ✅ no transform → no compositing-layer conflict with Mapbox marker translate
 * ✅ rendered entirely by compositor — markers stay pinned to their coordinates
 */

/* ── User location dot pulse ─────────────────────────────────────────────── */
@keyframes eco-user-pulse {
  0%   { box-shadow: 0 2px 8px rgba(14,165,233,0.55), 0 0 0 0   rgba(14,165,233,0.55); }
  70%  { box-shadow: 0 2px 8px rgba(14,165,233,0.55), 0 0 0 18px rgba(14,165,233,0);   }
  100% { box-shadow: 0 2px 8px rgba(14,165,233,0.55), 0 0 0 0   rgba(14,165,233,0);   }
}

.eco-user-marker {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.eco-user-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #0ea5e9;
  border: 2.5px solid #ffffff;
  animation: eco-user-pulse 2.2s ease-out infinite;
  pointer-events: none;
}

/* ── Shop / donation / recycling marker pulse ────────────────────────────── */
@keyframes eco-marker-pulse {
  0%   { box-shadow: 0 0 0 0   var(--ring-rgba), 0 3px 10px rgba(15,23,42,0.22); }
  70%  { box-shadow: 0 0 0 11px transparent,     0 3px 10px rgba(15,23,42,0.22); }
  100% { box-shadow: 0 0 0 0   transparent,      0 3px 10px rgba(15,23,42,0.22); }
}

.eco-map-marker {
  --ring-rgba: rgba(22, 163, 74, 0.5); /* default green; overridden per-marker via JS */
  animation: eco-marker-pulse 2.6s ease-out infinite;
}
</style>
