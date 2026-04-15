<template>
  <div class="brand-page">
    <Navbar />

    <div class="page-container">
      <!-- §4.2 Inline page header (no background box) -->
      <div class="brand-page-header">
        <h1>Brand Sustainability Scores</h1>
        <p>Search clothing brands to see their supply chain transparency, environmental, and governance scores.</p>
      </div>

      <!-- Search bar + button -->
      <div class="brand-search-wrap" role="search">
        <BrandSearchBar v-model="searchQuery" @search="handleSearch" />
        <button class="search-btn" @click="doSearch">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          Search
        </button>
      </div>

      <!-- Main layout: always visible once featured brands loaded -->
      <div v-if="showLayout" class="brand-layout">

        <!-- Left: results list -->
        <aside class="brand-list-panel">
          <div class="panel-title">
            <span>{{ committedQuery.trim() ? 'Results' : 'Featured Brands' }}</span>
            <span v-if="!isSearching && committedQuery.trim()" class="result-count">({{ searchResults.length }})</span>
          </div>

          <!-- Skeleton while loading -->
          <div v-if="isSearching || isFeaturedLoading" class="skeleton-list">
            <div v-for="n in 5" :key="n" class="skeleton-item">
              <div class="sk sk-avatar"></div>
              <div class="sk-lines">
                <div class="sk sk-line-long"></div>
                <div class="sk sk-line-short"></div>
              </div>
            </div>
          </div>

          <!-- Empty state (only for search) -->
          <div v-else-if="committedQuery.trim() && displayList.length === 0" class="empty-state">
            <p>{{ emptyMessage }}</p>
          </div>

          <!-- Brand list -->
          <div v-else class="brand-list">
            <BrandListItem
              v-for="item in displayList"
              :key="item.company_id"
              :brand="item"
              :is-active="selectedCompany?.company_id === item.company_id"
              @select="selectCompany"
            />
          </div>
        </aside>

        <!-- Right: detail panel -->
        <section class="brand-detail-panel" aria-live="polite">
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
                <div class="brand-avatar-large" :style="!detailLogoOk ? { background: avatarBg } : {}">
                  <img
                    v-if="detailLogoOk"
                    :src="detailLogoSrc"
                    :alt="companyDetail.company_name"
                    class="detail-logo-img"
                    @error="detailLogoOk = false"
                  />
                  <span v-else>{{ companyDetail.company_name.charAt(0).toUpperCase() }}</span>
                </div>
                <div>
                  <h2>{{ companyDetail.company_name }}</h2>
                  <span class="category-tag">{{ companyDetail.product_category === 'footwear' ? 'Footwear' : 'Apparel' }}</span>
                </div>
              </div>

              <div class="score-row">
                <div class="score-badge" :style="{ background: scoreBg, color: scoreColor, borderColor: scoreColor + '4d' }">
                  <div class="score-badge-inner">
                    <span class="score-number">{{ companyDetail.overall_score }}</span>
                    <span class="score-max">/100</span>
                  </div>
                  <span class="score-label-text">{{ companyDetail.score_label }}</span>
                </div>
              </div>
              <p class="score-desc">{{ scoreDescription }}</p>
            </div>

            <!-- Dimension scores -->
            <div class="detail-card">
              <h3>Sustainability Scores</h3>
              <p class="scores-desc">
                Three independently measured dimensions from the Fashion Transparency Index.
                Each bar shows how much of the maximum possible score this company achieved.
              </p>
              <MetricBar
                label="Governance & Policies"
                sublabel="Supplier code of conduct, senior accountability"
                :value="Math.round((companyDetail.governance_score / 6) * 100)"
                :raw-score="companyDetail.governance_score"
                :max-score="6"
              />
              <MetricBar
                label="Supply Chain Tracing"
                sublabel="Visibility across all production stages"
                :value="Math.round((companyDetail.tracing_score / 15) * 100)"
                :raw-score="companyDetail.tracing_score"
                :max-score="15"
              />
              <MetricBar
                label="Environmental Sustainability"
                sublabel="Fibre impact, emissions targets, sustainable materials"
                :value="Math.round((companyDetail.env_score / 21) * 100)"
                :raw-score="companyDetail.env_score"
                :max-score="21"
              />
            </div>

            <!-- Policy questions -->
            <div class="detail-card">
              <h3>Supply Chain Policies</h3>
              <p class="scores-desc">Whether this company has publicly committed to key supply chain and environmental standards.</p>
              <div class="policy-list">
                <PolicyRow
                  label="Supplier Code of Conduct published"
                  sublabel="The company has a formal, publicly available document setting ethical and labour standards for its suppliers."
                  :value="companyDetail.has_supplier_code"
                />
                <PolicyRow
                  label="Code of Conduct covers raw materials"
                  sublabel="The Supplier Code of Conduct extends beyond factories to cover raw material sourcing (e.g. cotton farms, textile mills)."
                  :value="companyDetail.code_covers_raw_materials"
                />
                <PolicyRow
                  label="Senior officer accountable for supply chain"
                  sublabel="A named executive (e.g. CEO or Chief Sustainability Officer) holds formal responsibility for supply chain ethics."
                  :value="companyDetail.has_senior_accountability"
                />
                <PolicyRow
                  label="Assessed fibre environmental impact"
                  sublabel="The company has formally evaluated the environmental footprint of the fibres used in its products."
                  :value="companyDetail.assessed_fibre_impact"
                />
                <PolicyRow
                  label="Emissions reduction target published"
                  sublabel="The company has publicly committed to a measurable greenhouse gas emissions reduction goal."
                  :value="companyDetail.has_emissions_target"
                />
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
              <a
                href="https://baptistworldaid.org.au/wp-content/uploads/2024/10/Ethical-Fashion-Report-2024-Appendix-1aec741f0a81f5f9.pdf"
                target="_blank"
                rel="noopener noreferrer"
                class="source-link"
              >
                View Full Report <ArrowRight :size="15" :stroke-width="2.5" class="cta-arrow" />
              </a>
            </div>
          </template>

          <!-- No selection prompt -->
          <div v-else class="no-selection">
            <p>Select a brand from the list to see its full sustainability profile.</p>
          </div>
        </section>
      </div>

      <!-- Loading featured brands on first mount — full-layout skeleton -->
      <div v-else class="brand-layout landing-skeleton">
        <!-- Left panel skeleton -->
        <div class="brand-list-panel">
          <div class="panel-title">
            <div class="sk sk-title-bar"></div>
          </div>
          <div class="skeleton-list">
            <div v-for="n in 6" :key="n" class="skeleton-item">
              <div class="sk sk-avatar"></div>
              <div class="sk-lines">
                <div class="sk sk-line-long"></div>
                <div class="sk sk-line-short"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right panel skeleton -->
        <div class="brand-detail-panel">
          <div class="detail-skeleton">
            <div class="sk sk-detail-header"></div>
            <div class="sk sk-detail-body"></div>
            <div class="sk sk-detail-body"></div>
            <div class="sk sk-detail-body-sm"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowRight, CheckCircle2, MinusCircle, XCircle } from 'lucide-vue-next'
import { computed, defineComponent, h, onMounted, ref, watch } from 'vue'
import BrandListItem from '../components/BrandListItem.vue'
import BrandSearchBar from '../components/BrandSearchBar.vue'
import MetricBar from '../components/MetricBar.vue'
import Navbar from '../components/Navbar.vue'
import { fetchCompanyDetail, searchBrands } from '../services/brandService'

// ── PolicyRow: icon + colored label, no box ─────────────────────────────────
const POLICY_CONFIG = {
  Yes:     { icon: CheckCircle2, color: '#16a34a' },
  No:      { icon: XCircle,      color: '#be123c' },
  Partial: { icon: MinusCircle,  color: '#92400e' },
}

const PolicyRow = defineComponent({
  props: { label: String, sublabel: String, value: String },
  setup(props) {
    return () => {
      const cfg = POLICY_CONFIG[props.value] ?? { icon: MinusCircle, color: '#94a3b8' }
      return h('div', {
        style: {
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          gap: '12px', padding: '12px 0', borderBottom: '1px solid #e5e7eb',
        },
      }, [
        h('div', { style: { display: 'flex', flexDirection: 'column', gap: '3px', flex: '1' } }, [
          h('span', { style: { fontSize: '14px', color: '#1e293b', fontWeight: '600' } }, props.label),
          props.sublabel
            ? h('span', { style: { fontSize: '13px', color: '#64748b', lineHeight: '1.4' } }, props.sublabel)
            : null,
        ]),
        h('span', {
          style: {
            display: 'inline-flex', alignItems: 'center', gap: '5px',
            fontSize: '13px', fontWeight: '600', flexShrink: '0', color: cfg.color,
          },
        }, [
          h(cfg.icon, { size: 16, strokeWidth: 2.5 }),
          h('span', {}, props.value),
        ]),
      ])
    }
  },
})
// ────────────────────────────────────────────────────────────────────────────

const searchQuery = ref('')       // mirrors the input box — changes on every keystroke
const committedQuery = ref('')    // the query that was actually submitted — only changes on Search/Enter
const searchResults = ref([])
const featuredCompanies = ref([])
const isFeaturedLoading = ref(true)
const selectedCompany = ref(null)
const companyDetail = ref(null)
const isSearching = ref(false)
const isLoadingDetail = ref(false)
const emptyMessage = ref('No brands found. Try a different spelling.')

// Show layout once featured brands are loaded
const showLayout = computed(() => !isFeaturedLoading.value)

// Left panel title and list are driven by committedQuery, not the live input
const displayList = computed(() =>
  committedQuery.value.trim() ? searchResults.value : featuredCompanies.value
)

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

// logo.dev logo with letter-avatar fallback
const detailLogoOk = ref(true)
const detailLogoSrc = computed(() =>
  companyDetail.value
    ? `https://img.logo.dev/${guessDomain(companyDetail.value.company_name)}?token=pk_LbFI27UJRDWnSoDCC_4GYA&size=80`
    : ''
)
watch(companyDetail, () => { detailLogoOk.value = true })

function guessDomain(name) {
  const overrides = {
    'H&M': 'hm.com', 'H&M Group': 'hm.com',
    'Inditex': 'inditex.com',
    'Levi Strauss & Co': 'levi.com',
    'PVH Corp': 'pvh.com',
    'VF Corporation': 'vfc.com',
    'Hanesbrands': 'hanes.com',
    'Fast Retailing': 'fastretailing.com',
    'Kering': 'kering.com',
    'LVMH': 'lvmh.com',
    'Adidas': 'adidas.com',
    'Nike': 'nike.com',
    'Puma': 'puma.com',
    'Patagonia': 'patagonia.com',
  }
  if (overrides[name]) return overrides[name]
  return name.toLowerCase().replace(/[^a-z0-9]/g, '') + '.com'
}

// Load a set of well-known brands to show before any search
const FEATURED_QUERIES = ['Nike', 'Patagonia', 'H&M', 'Adidas', 'Zara', "Levi's"]

onMounted(async () => {
  try {
    const results = await Promise.all(
      FEATURED_QUERIES.map(q => searchBrands(q).catch(() => ({ results: [] })))
    )
    const seen = new Set()
    const companies = []
    for (const res of results) {
      const first = res.results?.[0]
      if (first && !seen.has(first.company_id)) {
        seen.add(first.company_id)
        companies.push(first)
      }
    }
    featuredCompanies.value = companies
    // Auto-select the first featured company
    if (companies.length > 0) {
      await selectCompany(companies[0])
    }
  } catch {
    // silently fall through — isFeaturedLoading will be cleared in finally
  } finally {
    isFeaturedLoading.value = false
  }
})

function doSearch() {
  handleSearch(searchQuery.value)
}

async function handleSearch(query) {
  const q = query.trim()
  committedQuery.value = q  // lock in the submitted query

  if (!q) {
    // Empty search → go back to featured brands
    searchResults.value = []
    if (featuredCompanies.value.length > 0 && !companyDetail.value) {
      await selectCompany(featuredCompanies.value[0])
    }
    return
  }

  isSearching.value = true
  selectedCompany.value = null
  companyDetail.value = null

  try {
    const data = await searchBrands(q)
    searchResults.value = data.results ?? []
    emptyMessage.value = data.message || 'No brands found. Try a different spelling.'

    if (searchResults.value.length > 0) {
      await selectCompany(searchResults.value[0])
    }
  } catch {
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
  } catch {
    // detail stays null — the panel will show the no-selection prompt
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

/* §4.2 Inline page header */
.brand-page-header {
  margin-bottom: 16px;
}

.brand-page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.brand-page-header p {
  font-size: 15px;
  color: #64748b;
  max-width: 700px;
  line-height: 1.5;
  margin: 0;
}

/* Search bar + button row */
.brand-search-wrap {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 28px;
}

.brand-search-wrap > :first-child { flex: 1; }

.search-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.search-btn:hover { background: #15803d; }


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

.result-count { font-weight: 400; color: #94a3b8; font-size: 14px; }
.brand-list {
  max-height: 600px;
  overflow-y: auto;
  position: relative;
}

/* Bottom fade hint for scrollability */
.brand-list-panel {
  position: relative;
}

.brand-list-panel::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(transparent, white);
  pointer-events: none;
  border-radius: 0 0 20px 20px;
}

/* Skeletons */
.skeleton-list { padding: 8px 0; }
.skeleton-item { display: flex; gap: 12px; align-items: center; padding: 14px 16px; border-bottom: 1px solid #edf1f5; }
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
.detail-skeleton { display: flex; flex-direction: column; gap: 18px; }
.sk-detail-header { height: 140px; border-radius: 20px; }
.sk-detail-body { height: 120px; border-radius: 20px; }
.sk-detail-body-sm { height: 80px; border-radius: 20px; }
.sk-title-bar { height: 16px; width: 120px; border-radius: 6px; }

.landing-skeleton { pointer-events: none; }

.empty-state, .no-selection { padding: 32px 20px; text-align: center; color: #94a3b8; font-size: 15px; }

/* Right panel */
.brand-detail-panel { display: flex; flex-direction: column; gap: 18px; }

.detail-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
  padding: 24px;
}

.detail-card h3 { font-size: 18px; font-weight: 700; margin-bottom: 6px; color: #0f172a; }

/* Brand summary */
.brand-summary-header { display: flex; gap: 18px; align-items: flex-start; margin-bottom: 20px; }

.brand-avatar-large {
  width: 56px; height: 56px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 24px; color: #334155;
  flex-shrink: 0; overflow: hidden;
  border: 1px solid #e5e7eb;
}

.detail-logo-img { width: 100%; height: 100%; object-fit: contain; padding: 6px; background: white; }

.brand-summary-header h2 { font-size: 22px; color: #0f172a; margin-bottom: 6px; }

.category-tag {
  font-size: 12px; background: #f1f5f9; color: #475569;
  padding: 3px 10px; border-radius: 999px; font-weight: 500;
}

.score-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 12px; }

.score-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  border-radius: 14px;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.score-badge-inner {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.score-number { font-size: 36px; font-weight: 800; line-height: 1; }
.score-max { font-size: 16px; font-weight: 500; opacity: 0.7; }
.score-label-text { font-size: 14px; font-weight: 700; }
.score-desc { color: #475569; font-size: 15px; line-height: 1.6; margin: 0; }

/* Scores section description */
.scores-desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 20px;
  line-height: 1.5;
}

/* Policy rows */
.policy-list { display: flex; flex-direction: column; gap: 0; margin-bottom: 16px; }

.fibre-row {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid #f1f5f9;
}

.fibre-label { font-size: 14px; color: #334155; }
.fibre-value { font-weight: 700; font-size: 14px; color: #0f172a; }

/* Brands chips */
.brands-chip-list { display: flex; flex-wrap: wrap; gap: 10px; }

.brand-chip {
  background: #f1f5f9; color: #334155;
  padding: 6px 14px; border-radius: 999px;
  font-size: 14px;
}

/* Data source */
.data-source-box { background: #f5f9ff; border-color: #c7ddff; }
.data-source-box p { color: #334155; line-height: 1.7; font-size: 14px; margin: 0 0 14px; }

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: #1d4ed8;
  color: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.source-link:hover { background: #1e40af; }

.source-link .cta-arrow {
  transition: transform 150ms ease;
}

.source-link:hover .cta-arrow {
  transform: translateX(3px);
}

@media (max-width: 900px) {
  .brand-layout { grid-template-columns: 1fr; }
  .brand-page-header h1 { font-size: 26px; }
  .brand-search-wrap { flex-direction: column; }
  .search-btn { width: 100%; justify-content: center; }
}
</style>
