<template>
  <div class="brand-page">
    <Navbar />

    <div class="page-container">
      <section class="brand-hero">
        <h1>Brand Transparency</h1>
        <p>
          Search clothing brands and see how they score on supply chain transparency,
          environmental sustainability, and ethical governance.
        </p>
      </section>

      <div class="brand-search-wrap">
        <BrandSearchBar v-model="searchQuery" @search="handleSearch" />
      </div>

      <!-- Search results layout -->
      <div v-if="searchQuery.trim()" class="brand-layout">

        <!-- Left: results list -->
        <aside class="brand-list-panel">
          <div class="panel-title">
            Results
            <span v-if="!isSearching" class="result-count">({{ searchResults.length }})</span>
          </div>

          <!-- Skeleton while loading -->
          <div v-if="isSearching" class="skeleton-list">
            <div v-for="n in 5" :key="n" class="skeleton-item">
              <div class="sk sk-avatar"></div>
              <div class="sk-lines">
                <div class="sk sk-line-long"></div>
                <div class="sk sk-line-short"></div>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else-if="searchResults.length === 0" class="empty-state">
            <p>{{ emptyMessage }}</p>
          </div>

          <!-- Results -->
          <div v-else class="brand-list">
            <BrandListItem
              v-for="item in searchResults"
              :key="item.company_id"
              :brand="item"
              :is-active="selectedCompany?.company_id === item.company_id"
              @select="selectCompany"
            />
          </div>
        </aside>

        <!-- Right: detail panel -->
        <section class="brand-detail-panel">
          <!-- Skeleton while loading detail -->
          <div v-if="isLoadingDetail" class="detail-skeleton">
            <div class="sk sk-detail-header"></div>
            <div class="sk sk-detail-body"></div>
            <div class="sk sk-detail-body"></div>
          </div>

          <!-- Detail content -->
          <template v-else-if="companyDetail">
            <!-- Header card -->
            <div class="detail-card brand-summary">
              <div class="brand-summary-header">
                <div class="brand-avatar-large" :style="{ background: avatarBg }">
                  {{ companyDetail.company_name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h2>{{ companyDetail.company_name }}</h2>
                  <span class="category-tag">{{ companyDetail.product_category === 'footwear' ? 'Footwear' : 'Apparel' }}</span>
                </div>
              </div>

              <div class="score-row">
                <div class="score-badge" :style="{ background: scoreBg, color: scoreColor }">
                  <span class="score-number">{{ companyDetail.overall_score }}</span>
                  <span class="score-max">/100</span>
                  <span class="score-label-text">{{ companyDetail.score_label }}</span>
                </div>
                <p class="score-desc">{{ scoreDescription }}</p>
              </div>
            </div>

            <!-- Dimension scores -->
            <div class="detail-card">
              <h3>Sustainability Scores</h3>
              <MetricBar
                label="Governance & Policies"
                :value="Math.round((companyDetail.governance_score / 6) * 100)"
                :raw="`${companyDetail.governance_score} / 6`"
              />
              <MetricBar
                label="Supply Chain Tracing"
                :value="Math.round((companyDetail.tracing_score / 15) * 100)"
                :raw="`${companyDetail.tracing_score} / 15`"
              />
              <MetricBar
                label="Environmental Sustainability"
                :value="Math.round((companyDetail.env_score / 21) * 100)"
                :raw="`${companyDetail.env_score} / 21`"
              />
            </div>

            <!-- Policy questions -->
            <div class="detail-card">
              <h3>Supply Chain Policies</h3>
              <div class="policy-list">
                <PolicyRow label="Supplier Code of Conduct" :value="companyDetail.has_supplier_code" />
                <PolicyRow label="Code covers raw materials level" :value="companyDetail.code_covers_raw_materials" />
                <PolicyRow label="Senior officer accountability" :value="companyDetail.has_senior_accountability" />
                <PolicyRow label="Assessed environmental fibre impact" :value="companyDetail.assessed_fibre_impact" />
                <PolicyRow label="Published emissions reduction target" :value="companyDetail.has_emissions_target" />
              </div>

              <div class="fibre-row">
                <span class="fibre-label">Sustainable fibres in final product</span>
                <span class="fibre-value">{{ companyDetail.sustainable_fibre_pct }}</span>
              </div>
            </div>

            <!-- Brands under this company -->
            <div v-if="companyDetail.brands.length > 1" class="detail-card">
              <h3>Brands under this Company</h3>
              <div class="brands-chip-list">
                <span
                  v-for="b in companyDetail.brands"
                  :key="b.brand_name"
                  class="brand-chip"
                >
                  {{ b.brand_name }}
                  <span class="chip-score">{{ b.score }}</span>
                </span>
              </div>
            </div>

            <!-- Data source -->
            <div class="detail-card data-source-box">
              <h3>Data Source</h3>
              <p>
                Scores are derived from the <strong>Fashion Transparency Index</strong> (Australian market).
                Data reflects publicly available corporate disclosures on supply chain policies,
                environmental commitments, and fibre sourcing.
              </p>
            </div>
          </template>

          <!-- No selection prompt -->
          <div v-else class="no-selection">
            <p>Select a brand from the list to see its full sustainability profile.</p>
          </div>
        </section>
      </div>

      <!-- Landing state before any search -->
      <div v-else class="landing-hint">
        <p>Start typing a brand name above — e.g. <em>Zara</em>, <em>Patagonia</em>, <em>H&amp;M</em></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, ref } from 'vue'
import BrandListItem from '../components/BrandListItem.vue'
import BrandSearchBar from '../components/BrandSearchBar.vue'
import MetricBar from '../components/MetricBar.vue'
import Navbar from '../components/Navbar.vue'
import { fetchCompanyDetail, searchBrands } from '../services/brandService'

// ── Inline PolicyRow component ──────────────────────────────────────────────
const POLICY_STYLES = {
  Yes: { bg: '#dcfce7', color: '#16a34a' },
  No: { bg: '#fee2e2', color: '#dc2626' },
  Partial: { bg: '#fef9c3', color: '#ca8a04' },
}

const PolicyRow = defineComponent({
  props: { label: String, value: String },
  setup(props) {
    return () => {
      const style = POLICY_STYLES[props.value] || { bg: '#f1f5f9', color: '#64748b' }
      return h('div', { class: 'policy-row' }, [
        h('span', { class: 'policy-label' }, props.label),
        h('span', { class: 'policy-badge', style: { background: style.bg, color: style.color } }, props.value),
      ])
    }
  },
})
// ────────────────────────────────────────────────────────────────────────────

const searchQuery = ref('')
const searchResults = ref([])
const selectedCompany = ref(null)
const companyDetail = ref(null)
const isSearching = ref(false)
const isLoadingDetail = ref(false)
const emptyMessage = ref('No brands found. Try a different spelling.')

const LABEL_COLORS = {
  Great: '#16a34a',
  Good: '#65a30d',
  "It's a Start": '#ca8a04',
  'Below Average': '#ea580c',
  Avoid: '#dc2626',
}
const LABEL_BG = {
  Great: '#dcfce7',
  Good: '#ecfccb',
  "It's a Start": '#fef9c3',
  'Below Average': '#ffedd5',
  Avoid: '#fee2e2',
}
const LABEL_DESCRIPTIONS = {
  Great: 'This company leads on sustainability and transparency.',
  Good: 'Good overall performance with some room to improve.',
  "It's a Start": 'Some initiatives in place but significant gaps remain.',
  'Below Average': 'Limited transparency and sustainability efforts.',
  Avoid: 'Very little evidence of sustainable or ethical practices.',
}

const scoreColor = computed(() => LABEL_COLORS[companyDetail.value?.score_label] || '#64748b')
const scoreBg = computed(() => LABEL_BG[companyDetail.value?.score_label] || '#f1f5f9')
const scoreDescription = computed(() => LABEL_DESCRIPTIONS[companyDetail.value?.score_label] || '')
const avatarBg = computed(() => {
  if (!companyDetail.value) return '#dbeafe'
  const palettes = ['#dbeafe', '#dcfce7', '#fef9c3', '#fce7f3', '#ede9fe', '#ffedd5']
  return palettes[companyDetail.value.company_name.charCodeAt(0) % palettes.length]
})

async function handleSearch(query) {
  const q = query.trim()
  if (!q) {
    searchResults.value = []
    selectedCompany.value = null
    companyDetail.value = null
    return
  }

  isSearching.value = true
  selectedCompany.value = null
  companyDetail.value = null

  try {
    const data = await searchBrands(q)
    searchResults.value = data.results ?? []
    emptyMessage.value = data.message || 'No brands found. Try a different spelling.'

    // Auto-select first result
    if (searchResults.value.length > 0) {
      await selectCompany(searchResults.value[0])
    }
  } catch (err) {
    console.error('Brand search error:', err)
    searchResults.value = []
    emptyMessage.value = 'Search failed. Please try again.'
  } finally {
    isSearching.value = false
  }
}

async function selectCompany(item) {
  selectedCompany.value = item
  isLoadingDetail.value = true
  companyDetail.value = null

  try {
    companyDetail.value = await fetchCompanyDetail(item.company_id)
  } catch (err) {
    console.error('Company detail error:', err)
  } finally {
    isLoadingDetail.value = false
  }
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

/* Hero */
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

/* Search bar */
.brand-search-wrap {
  margin-bottom: 28px;
}

/* Landing hint */
.landing-hint {
  text-align: center;
  padding: 60px 0;
  color: #94a3b8;
  font-size: 17px;
}

.landing-hint em {
  color: #64748b;
  font-style: normal;
  font-weight: 500;
}

/* Two-column layout */
.brand-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  align-items: start;
}

/* Left panel */
.brand-list-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
  overflow: hidden;
}

.panel-title {
  padding: 16px 18px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1px solid #edf1f5;
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-count {
  font-weight: 400;
  color: #94a3b8;
  font-size: 14px;
}

.brand-list {
  max-height: 600px;
  overflow-y: auto;
}

/* Skeleton loading */
.skeleton-list {
  padding: 8px 0;
}

.skeleton-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #edf1f5;
}

.sk {
  background: linear-gradient(90deg, #f0f2f5 25%, #e8eaed 50%, #f0f2f5 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.sk-avatar { width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.sk-line-long { height: 14px; width: 70%; }
.sk-line-short { height: 12px; width: 45%; }

/* Detail skeleton */
.detail-skeleton { display: flex; flex-direction: column; gap: 18px; }
.sk-detail-header { height: 140px; border-radius: 20px; }
.sk-detail-body { height: 120px; border-radius: 20px; }

/* Empty + no-selection */
.empty-state, .no-selection {
  padding: 32px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 15px;
}

/* Right: detail cards */
.brand-detail-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
  padding: 24px;
}

.detail-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 18px;
  color: #0f172a;
}

/* Brand summary header */
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24px;
  color: #334155;
  flex-shrink: 0;
}

.brand-summary-header h2 {
  font-size: 22px;
  color: #0f172a;
  margin-bottom: 6px;
}

.category-tag {
  font-size: 12px;
  background: #f1f5f9;
  color: #475569;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 500;
}

/* Score badge */
.score-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.score-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  padding: 10px 18px;
  border-radius: 12px;
  flex-shrink: 0;
}

.score-number {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.score-max {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.7;
}

.score-label-text {
  font-size: 15px;
  font-weight: 700;
  margin-left: 8px;
}

.score-desc {
  color: #475569;
  font-size: 14px;
  margin: 0;
  flex: 1;
}

/* Policy rows */
.policy-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.policy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.policy-label {
  font-size: 14px;
  color: #334155;
  flex: 1;
}

.policy-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.fibre-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  margin-top: 4px;
}

.fibre-label {
  font-size: 14px;
  color: #334155;
}

.fibre-value {
  font-weight: 700;
  font-size: 14px;
  color: #0f172a;
}

/* Brands chip list */
.brands-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.brand-chip {
  background: #f1f5f9;
  color: #334155;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chip-score {
  background: #e2e8f0;
  color: #475569;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

/* Data source */
.data-source-box {
  background: #f5f9ff;
  border-color: #c7ddff;
}

.data-source-box p {
  color: #334155;
  line-height: 1.7;
  font-size: 14px;
  margin: 0;
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
