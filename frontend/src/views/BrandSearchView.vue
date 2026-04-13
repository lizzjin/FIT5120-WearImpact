<template>
  <div class="brand-page">
    <Navbar />

    <div class="page-container">
      <section class="brand-hero">
        <h1>Brand Environmental Transparency</h1>
        <p>
          Search and evaluate clothing brands based on their sustainability performance.
        </p>
      </section>

      <div class="brand-search-wrap">
        <BrandSearchBar v-model="searchQuery" @search="handleSearch" />
      </div>

      <div class="brand-layout">
        <aside class="brand-list-panel">
          <div class="panel-title">Brands ({{ filteredBrands.length }})</div>

          <div class="brand-list">
            <BrandListItem
              v-for="brand in filteredBrands"
              :key="brand.id"
              :brand="brand"
              :is-active="selectedBrand && selectedBrand.id === brand.id"
              @select="selectBrand"
            />
          </div>
        </aside>

        <section v-if="selectedBrand" class="brand-detail-panel">
          <div class="detail-card brand-summary">
            <div class="brand-summary-header">
              <div class="brand-avatar-large">{{ selectedBrand.shortName }}</div>

              <div>
                <h2>{{ selectedBrand.name }}</h2>
                <p>{{ selectedBrand.description }}</p>
              </div>
            </div>

            <div class="score-box">
              <span>Sustainability Score:</span>
              <strong>{{ selectedBrand.score }}/100</strong>
              <span>{{ selectedBrand.ratingLabel }}</span>
            </div>
          </div>

          <div class="detail-card">
            <h3>Performance Metrics</h3>

            <MetricBar
              label="Supply Chain Transparency"
              :value="selectedBrand.transparency"
            />
            <MetricBar
              label="Sustainable Materials Usage"
              :value="selectedBrand.materials"
            />

            <div class="commitment">
              <h4>Carbon Commitment</h4>
              <p>{{ selectedBrand.carbonCommitment }}</p>
            </div>
          </div>

          <div class="detail-card">
            <h3>Certifications & Standards</h3>
            <div class="tag-list">
              <span
                v-for="item in selectedBrand.certifications"
                :key="item"
                class="tag"
              >
                {{ item }}
              </span>

              <span
                v-if="selectedBrand.certifications.length === 0"
                class="empty-tag"
              >
                No certifications listed
              </span>
            </div>
          </div>

          <div class="detail-card data-source-box">
            <h3>Data Sources</h3>
            <p>{{ selectedBrand.dataSource }}</p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Navbar from '../components/Navbar.vue'
import BrandSearchBar from '../components/BrandSearchBar.vue'
import BrandListItem from '../components/BrandListItem.vue'
import MetricBar from '../components/MetricBar.vue'
import { brandData } from '../data/brandData'

const searchQuery = ref('')

const filteredBrands = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) return brandData

  return brandData.filter((brand) =>
    brand.name.toLowerCase().includes(query)
  )
})

const selectedBrand = ref(brandData[0])

function handleSearch() {
  if (
    filteredBrands.value.length > 0 &&
    !filteredBrands.value.find((item) => item.id === selectedBrand.value?.id)
  ) {
    selectedBrand.value = filteredBrands.value[0]
  }
}

function selectBrand(brand) {
  selectedBrand.value = brand
}
</script>

<style scoped>
.brand-page {
  background: #f8faf8;
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.brand-hero {
  background: #edf5ef;
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 24px;
  text-align: center;
}

.brand-hero h1 {
  font-size: 48px;
  color: #0f172a;
  margin-bottom: 12px;
}

.brand-hero p {
  font-size: 18px;
  color: #475569;
  line-height: 1.6;
  max-width: 760px;
  margin: 0 auto;
}

.brand-search-wrap {
  margin-bottom: 28px;
}

.brand-layout {
  display: grid;
  grid-template-columns: 330px 1fr;
  gap: 24px;
}
.brand-list-panel,
.detail-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.panel-title {
  padding: 18px 18px 14px;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1px solid #edf1f5;
}

.brand-list {
  max-height: 650px;
  overflow-y: auto;
}

.brand-detail-panel {
  display: grid;
  gap: 18px;
}

.brand-summary {
  padding: 24px;
}

.brand-summary-header {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.brand-avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #eef1f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24px;
  color: #334155;
  flex-shrink: 0;
}

.brand-summary h2 {
  font-size: 24px;
  color: #0f172a;
  margin-bottom: 8px;
}

.brand-summary p {
  color: #475569;
  line-height: 1.6;
}

.score-box {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #e8f7e9;
  padding: 12px 16px;
  border-radius: 12px;
  color: #166534;
  font-size: 18px;
}

.score-box strong {
  font-size: 22px;
}

.detail-card {
  padding: 24px;
}

.detail-card h3 {
  font-size: 22px;
  margin-bottom: 18px;
  color: #0f172a;
}

.commitment h4 {
  margin-top: 12px;
  margin-bottom: 6px;
  color: #334155;
}

.commitment p {
  color: #0f172a;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag,
.empty-tag {
  background: #e8f7e9;
  color: #166534;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 14px;
}

.data-source-box {
  background: #f5f9ff;
  border-color: #c7ddff;
}

.data-source-box p {
  color: #334155;
  line-height: 1.7;
}

@media (max-width: 900px) {
  .brand-layout {
    grid-template-columns: 1fr;
  }

  .brand-hero h1 {
    font-size: 34px;
  }
}
</style>