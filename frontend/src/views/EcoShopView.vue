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
      </section>

      <SearchBar @search="handleSearch" />

      <div class="filter-row">
        <button
          v-for="type in filterOptions"
          :key="type"
          :class="{ active: activeFilter === type }"
          @click="setFilter(type)"
        >
          {{ type }}
        </button>
      </div>

      <div v-if="isLoading" class="status-message">Loading locations...</div>
      <div v-else-if="errorMessage" class="status-message error">{{ errorMessage }}</div>
      <div v-else-if="searched && displayedLocations.length === 0" class="status-message error">
        No results found.
      </div>

      <div class="content-layout">
        <div class="results-section">
          <LocationCard
            v-for="location in displayedLocations"
            :key="location.id"
            :location="location"
          />
        </div>

        <div class="map-placeholder">
          <h3>Map Area</h3>
          <p>Map integration will be added later.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import { ref, onMounted } from 'vue'
import SearchBar from '../components/SearchBar.vue'
import LocationCard from '../components/LocationCard.vue'
import { fetchLocations } from '../services/locationService'

const filterOptions = ['All', 'Second-hand', 'Donation', 'Recycling']

const searched = ref(false)
const searchQuery = ref('')
const activeFilter = ref('All')
const displayedLocations = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

async function loadLocations() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const data = await fetchLocations({
      query: searchQuery.value,
      filter: activeFilter.value
    })
    displayedLocations.value = data
  } catch (error) {
    console.error('Failed to load locations:', error)
    errorMessage.value = 'Failed to load locations. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function handleSearch(query) {
  searched.value = true
  searchQuery.value = query
  loadLocations()
}

function setFilter(type) {
  activeFilter.value = type
  loadLocations()
}

onMounted(() => {
  loadLocations()
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
  margin: 0 auto;
}
.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.filter-row button {
  padding: 10px 18px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
}

.filter-row button.active {
  background: #16a34a;
  color: white;
  border-color: #16a34a;
}

.status-message {
  margin-bottom: 20px;
  font-weight: 600;
  color: #334155;
}

.status-message.error {
  color: #b91c1c;
}

.content-layout {
  display: grid;
  grid-template-columns: 1.3fr 0.8fr;
  gap: 24px;
}

.results-section {
  display: grid;
  gap: 18px;
}

.map-placeholder {
  background: white;
  border: 2px dashed #cbd5e1;
  border-radius: 20px;
  padding: 28px;
  min-height: 500px;
}

.map-placeholder h3 {
  font-size: 28px;
  color: #0f172a;
  margin-bottom: 10px;
}

.map-placeholder p {
  color: #64748b;
}

@media (max-width: 900px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .eco-hero h1 {
    font-size: 34px;
  }
}
</style>