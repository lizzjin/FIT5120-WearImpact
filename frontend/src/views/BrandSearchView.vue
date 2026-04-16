<template>
  <div class="brand-page">
    <Navbar />

    <div class="page-container">
      <!-- Page header -->
      <div class="brand-page-header">
        <h1>Brand Sustainability Scores</h1>
        <p>Search clothing brands to see their supply chain transparency, environmental, and governance scores.</p>
      </div>

      <!-- Search bar + button -->
      <div class="brand-search-wrap" role="search">
        <BrandSearchBar v-model="searchQuery" @search="handleSearch" />
        <button class="search-btn" @click="doSearch">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          Search
        </button>
      </div>

      <!-- Section label row -->
      <div class="grid-label-row">
        <span class="grid-section-label">
          {{ committedQuery.trim() ? 'Search Results' : 'Featured Brands' }}
          <span v-if="!isSearching && committedQuery.trim()" class="result-count">
            {{ searchResults.length }} found
          </span>
        </span>
        <span v-if="!committedQuery.trim() && !isFeaturedLoading" class="grid-sublabel">
          Click any card to see full sustainability details
        </span>
      </div>

      <!-- Card grid -->
      <div class="brand-card-grid">

        <!-- Skeleton: initial load or searching -->
        <template v-if="isFeaturedLoading || isSearching">
          <div v-for="n in PAGE_SIZE" :key="n" class="brand-card brand-card--skeleton">
            <div class="sk-identity">
              <div class="sk sk-avatar"></div>
              <div class="sk-text">
                <div class="sk sk-line-long"></div>
                <div class="sk sk-line-short"></div>
              </div>
            </div>
            <div class="sk sk-score-block"></div>
            <div class="sk-mini-rows">
              <div v-for="r in 3" :key="r" class="sk-mini-row">
                <div class="sk sk-mini-label"></div>
                <div class="sk sk-mini-track"></div>
              </div>
            </div>
            <div class="sk sk-cta-bar"></div>
          </div>
        </template>

        <!-- Featured load error -->
        <div v-else-if="featuredLoadError && !committedQuery.trim()" class="empty-state">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/>
            </svg>
          </div>
          <p class="empty-title">Could not load brands</p>
          <p class="empty-sub">Backend unavailable. Please try refreshing the page.</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="committedQuery.trim() && displayList.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <p class="empty-title">No brands found</p>
          <p class="empty-sub">{{ emptyMessage }}</p>
        </div>

        <!-- Brand cards (paginated) -->
        <template v-else>
          <button
            v-for="item in paginatedList"
            :key="item.company_id"
            class="brand-card"
            :class="{ 'brand-card--active': selectedCompany?.company_id === item.company_id }"
            @click="openModal(item)"
          >
            <!-- Identity: logo + name -->
            <div class="card-identity">
              <div
                class="card-avatar"
                :style="logoErrors[item.company_id] ? { background: getAvatarBg(item.company_name) } : {}"
              >
                <img
                  v-if="!logoErrors[item.company_id]"
                  :src="getLogoSrc(item.company_name)"
                  :alt="item.company_name"
                  class="card-logo-img"
                  @error="onCardLogoError(item.company_id)"
                />
                <span v-else class="avatar-letter">{{ item.company_name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="card-name-block">
                <p class="card-brand-name">{{ item.company_name }}</p>
                <p v-if="item.matched_brand && item.matched_brand !== item.company_name" class="card-matched">
                  via {{ item.matched_brand }}
                </p>
              </div>
            </div>

            <!-- Score -->
            <div class="card-score-area">
              <div class="card-score-number-wrap">
                <span class="card-score-num" :style="{ color: getLabelColor(item.score_label) }">
                  {{ item.overall_score }}
                </span>
                <span class="card-score-denom">/100</span>
              </div>
              <span
                class="card-label-pill"
                :style="{ background: getLabelBg(item.score_label), color: getLabelColor(item.score_label) }"
              >{{ item.score_label }}</span>
            </div>

            <!-- Dimension mini-bars (prefetched detail) -->
            <div class="card-mini-bars">
              <template v-if="companyDetails[item.company_id]">
                <div
                  v-for="dim in getCardDims(item.company_id)"
                  :key="dim.label"
                  class="mini-bar-row"
                >
                  <span class="mini-bar-label">{{ dim.label }}</span>
                  <div class="mini-bar-track">
                    <div
                      class="mini-bar-fill"
                      :style="{ width: dim.pct + '%', background: miniBarColor(dim.pct) }"
                    ></div>
                  </div>
                  <span class="mini-bar-pct">{{ dim.pct }}%</span>
                </div>
              </template>
              <template v-else>
                <div v-for="r in 3" :key="r" class="sk-mini-row">
                  <div class="sk sk-mini-label"></div>
                  <div class="sk sk-mini-track"></div>
                </div>
              </template>
            </div>

            <!-- CTA row -->
            <div class="card-footer">
              <span class="card-cta-text">View Full Profile</span>
              <ArrowRight :size="14" :stroke-width="2.5" class="card-arrow" />
            </div>
          </button>
        </template>
      </div>

      <!-- Pagination -->
      <div v-if="!isFeaturedLoading && !isSearching && totalPages > 1" class="pagination">
        <button
          class="page-nav-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
          aria-label="Previous page"
        >
          <ChevronLeft :size="15" /> Prev
        </button>

        <div class="page-numbers">
          <template v-for="p in visiblePages" :key="p">
            <span v-if="p === '...'" class="page-ellipsis">…</span>
            <button
              v-else
              class="page-number"
              :class="{ 'page-number--active': p === currentPage }"
              @click="goToPage(p)"
              :aria-label="`Page ${p}`"
              :aria-current="p === currentPage ? 'page' : undefined"
            >{{ p }}</button>
          </template>
        </div>

        <button
          class="page-nav-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
          aria-label="Next page"
        >
          Next <ChevronRight :size="15" />
        </button>
      </div>
    </div>

    <!-- ── Centered detail modal ────────────────────────────────────────────── -->
    <Transition name="modal-fade">
      <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal-panel" role="dialog" aria-modal="true" aria-label="Brand sustainability detail">

          <button class="modal-close" @click="closeModal" aria-label="Close">
            <X :size="18" :stroke-width="2" />
          </button>

          <div class="modal-scroll">
            <!-- Loading skeleton -->
            <div v-if="isLoadingDetail" class="detail-skeleton">
              <div class="sk sk-detail-header"></div>
              <div class="sk sk-detail-body"></div>
              <div class="sk sk-detail-body"></div>
              <div class="sk sk-detail-body-sm"></div>
            </div>

            <!-- Detail content -->
            <template v-else-if="companyDetail">
              <!-- Brand summary -->
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
                    <span class="category-tag">
                      {{ companyDetail.product_category === 'footwear' ? 'Footwear' : 'Apparel' }}
                    </span>
                  </div>
                </div>

                <div class="score-row">
                  <div
                    class="score-badge"
                    :style="{ background: scoreBg, color: scoreColor, borderColor: scoreColor + '4d' }"
                  >
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

              <!-- Supply chain policies -->
              <div class="detail-card">
                <h3>Supply Chain Policies</h3>
                <p class="scores-desc">
                  Whether this company has publicly committed to key supply chain and environmental standards.
                </p>
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

              <!-- Sub-brands -->
              <div v-if="companyDetail.brands.length > 1" class="detail-card">
                <h3>Brands under this Company</h3>
                <div class="brands-chip-list">
                  <span v-for="b in companyDetail.brands" :key="b.brand_name" class="brand-chip">
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
                  View Full Report
                  <ArrowRight :size="15" :stroke-width="2.5" class="cta-arrow" />
                </a>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ArrowRight, CheckCircle2, ChevronLeft, ChevronRight, MinusCircle, X, XCircle } from 'lucide-vue-next'
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import BrandSearchBar from '../components/BrandSearchBar.vue'
import MetricBar from '../components/MetricBar.vue'
import Navbar from '../components/Navbar.vue'
import { fetchAllCompanies, fetchCompanyDetail, searchBrands } from '../services/brandService'

// ── PolicyRow inline component ────────────────────────────────────────────────
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
// ─────────────────────────────────────────────────────────────────────────────

// ── Label color / bg maps ─────────────────────────────────────────────────────
const LABEL_COLORS = {
  'Great':         '#16a34a',
  'Good':          '#65a30d',
  "It's a Start":  '#ca8a04',
  'Below Average': '#ea580c',
  'Avoid':         '#dc2626',
}
const LABEL_BG = {
  'Great':         '#dcfce7',
  'Good':          '#ecfccb',
  "It's a Start":  '#fef9c3',
  'Below Average': '#ffedd5',
  'Avoid':         '#fee2e2',
}
const LABEL_DESCRIPTIONS = {
  'Great':         'This company leads on sustainability and transparency.',
  'Good':          'Good overall performance with some room to improve.',
  "It's a Start":  'Some initiatives in place but significant gaps remain.',
  'Below Average': 'Limited transparency and sustainability efforts.',
  'Avoid':         'Very little evidence of sustainable or ethical practices.',
}

function getLabelColor(label) { return LABEL_COLORS[label] || '#64748b' }
function getLabelBg(label)    { return LABEL_BG[label]    || '#f1f5f9' }

// ── Mini-bar color (traffic-light by percentage) ──────────────────────────────
function miniBarColor(pct) {
  if (pct >= 60) return '#16a34a'
  if (pct >= 35) return '#d97706'
  return '#dc2626'
}

// ── Avatar / logo helpers ─────────────────────────────────────────────────────
const AVATAR_PALETTE = ['#dbeafe', '#dcfce7', '#fef9c3', '#fce7f3', '#ede9fe', '#ffedd5']
function getAvatarBg(name) {
  return AVATAR_PALETTE[name.charCodeAt(0) % AVATAR_PALETTE.length]
}

function getLogoSrc(name, size = 40) {
  return `https://img.logo.dev/${guessDomain(name)}?token=pk_LbFI27UJRDWnSoDCC_4GYA&size=${size}`
}

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

// ── Card logo error tracking ──────────────────────────────────────────────────
const logoErrors = reactive({})
function onCardLogoError(companyId) {
  logoErrors[companyId] = true
}

// ── Detail cache (prefetched per-company) ─────────────────────────────────────
// Keyed by company_id. undefined = not yet fetched, null = fetch failed, object = loaded.
const companyDetails = reactive({})

async function prefetchDetails(companies) {
  await Promise.allSettled(
    companies.map(async (c) => {
      if (companyDetails[c.company_id] !== undefined) return // already cached or failed
      try {
        companyDetails[c.company_id] = await fetchCompanyDetail(c.company_id)
      } catch {
        companyDetails[c.company_id] = null
      }
    })
  )
}

function getCardDims(companyId) {
  const d = companyDetails[companyId]
  if (!d) return []
  return [
    { label: 'Governance',   pct: Math.round((d.governance_score / 6)  * 100) },
    { label: 'Tracing',      pct: Math.round((d.tracing_score   / 15) * 100) },
    { label: 'Environment',  pct: Math.round((d.env_score       / 21) * 100) },
  ]
}

// ── Search state ──────────────────────────────────────────────────────────────
const searchQuery       = ref('')
const committedQuery    = ref('')
const searchResults     = ref([])
const featuredCompanies = ref([])
const featuredTotal     = ref(0)
const featuredLoadError = ref(false)
const isFeaturedLoading = ref(true)
const isSearching       = ref(false)
const emptyMessage      = ref('No brands found. Try a different spelling.')

const displayList = computed(() =>
  committedQuery.value.trim() ? searchResults.value : featuredCompanies.value
)

// ── Pagination ────────────────────────────────────────────────────────────────
const PAGE_SIZE   = 9
const currentPage = ref(1)

// Featured uses server-side total; search uses client-side result count.
const totalPages = computed(() => {
  if (committedQuery.value.trim()) {
    return Math.ceil(searchResults.value.length / PAGE_SIZE)
  }
  return Math.ceil(featuredTotal.value / PAGE_SIZE)
})

// Featured: API already returns current page; search: slice locally.
const paginatedList = computed(() => {
  if (committedQuery.value.trim()) {
    const start = (currentPage.value - 1) * PAGE_SIZE
    return searchResults.value.slice(start, start + PAGE_SIZE)
  }
  return featuredCompanies.value
})

// Smart page number list: first, last, current ±2 with ellipsis gaps.
const visiblePages = computed(() => {
  const total   = totalPages.value
  const current = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const pages = new Set([1, total, current])
  for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
    pages.add(i)
  }

  const sorted = [...pages].sort((a, b) => a - b)
  const result = []
  let prev = 0
  for (const p of sorted) {
    if (p - prev > 1) result.push('...')
    result.push(p)
    prev = p
  }
  return result
})

// Reset to page 1 when the committed query changes (new search or clearing search).
watch(committedQuery, () => { currentPage.value = 1 })

async function goToPage(p) {
  currentPage.value = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
  if (committedQuery.value.trim()) {
    // Search mode: data already in searchResults, just prefetch new slice
    prefetchDetails(paginatedList.value)
  } else {
    // Featured mode: fetch the new page from the server
    await loadFeaturedPage(p)
  }
}

async function loadFeaturedPage(page) {
  isFeaturedLoading.value = true
  featuredLoadError.value = false
  try {
    const data = await fetchAllCompanies(page, PAGE_SIZE)
    featuredCompanies.value = data.results
    featuredTotal.value     = data.total
    currentPage.value       = page
    prefetchDetails(data.results)
  } catch {
    featuredLoadError.value = true
  } finally {
    isFeaturedLoading.value = false
  }
}

// ── Modal state ───────────────────────────────────────────────────────────────
const showModal       = ref(false)
const selectedCompany = ref(null)
const companyDetail   = ref(null)
const isLoadingDetail = ref(false)

watch(showModal, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

async function openModal(item) {
  selectedCompany.value = item
  showModal.value = true

  // Use cached detail if already prefetched
  const cached = companyDetails[item.company_id]
  if (cached) {
    companyDetail.value = cached
    isLoadingDetail.value = false
    return
  }

  isLoadingDetail.value = true
  companyDetail.value = null
  try {
    const detail = await fetchCompanyDetail(item.company_id)
    companyDetails[item.company_id] = detail
    companyDetail.value = detail
  } catch {
    // stays null — modal shows nothing
  } finally {
    isLoadingDetail.value = false
  }
}

function closeModal() {
  showModal.value = false
}

// ── Detail computed values (for modal) ───────────────────────────────────────
const scoreColor      = computed(() => getLabelColor(companyDetail.value?.score_label))
const scoreBg         = computed(() => getLabelBg(companyDetail.value?.score_label))
const scoreDescription = computed(() => LABEL_DESCRIPTIONS[companyDetail.value?.score_label] || '')

const avatarBg = computed(() =>
  companyDetail.value ? getAvatarBg(companyDetail.value.company_name) : '#dbeafe'
)

const detailLogoOk  = ref(true)
const detailLogoSrc = computed(() =>
  companyDetail.value ? getLogoSrc(companyDetail.value.company_name, 80) : ''
)
watch(companyDetail, () => { detailLogoOk.value = true })

// ── Data fetching ─────────────────────────────────────────────────────────────
onMounted(() => loadFeaturedPage(1))

function doSearch() {
  handleSearch(searchQuery.value)
}

async function handleSearch(query) {
  const q = query.trim()
  committedQuery.value = q

  if (!q) {
    searchResults.value = []
    showModal.value = false
    await loadFeaturedPage(1)
    return
  }

  isSearching.value = true
  selectedCompany.value = null
  companyDetail.value = null
  showModal.value = false

  try {
    const data = await searchBrands(q)
    searchResults.value = data.results ?? []
    emptyMessage.value = data.message || 'No brands found. Try a different spelling.'
    // Prefetch detail for search results' first page
    prefetchDetails(searchResults.value.slice(0, PAGE_SIZE))
  } catch {
    searchResults.value = []
    emptyMessage.value = 'Search failed. Please try again.'
  } finally {
    isSearching.value = false
  }
}
</script>

<style scoped>
/* ── Page shell ──────────────────────────────────────────────────────────────── */
.brand-page {
  background: #f8faf8;
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 32px 72px;
}

/* ── Page header ─────────────────────────────────────────────────────────────── */
.brand-page-header {
  margin-bottom: 24px;
}

.brand-page-header h1 {
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.brand-page-header p {
  font-size: 15px;
  color: #64748b;
  max-width: 600px;
  line-height: 1.6;
  margin: 0;
}

/* ── Search bar ──────────────────────────────────────────────────────────────── */
.brand-search-wrap {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 32px;
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
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.search-btn:hover { background: #15803d; }

/* ── Section label row ───────────────────────────────────────────────────────── */
.grid-label-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.grid-section-label {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-count {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 10px;
  border-radius: 999px;
}

.grid-sublabel {
  font-size: 14px;
  color: #94a3b8;
}

/* ── Card grid ───────────────────────────────────────────────────────────────── */
.brand-card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* ── Brand card ──────────────────────────────────────────────────────────────── */
.brand-card {
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  text-align: left;
  transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
  position: relative;
  overflow: hidden;
}

/* Green accent bar on the left side */
.brand-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #16a34a;
  opacity: 0;
  transition: opacity 0.2s ease;
  border-radius: 20px 0 0 20px;
}

.brand-card:hover {
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.1);
  transform: translateY(-2px);
  border-color: #d1fae5;
}

.brand-card:hover::before,
.brand-card--active::before {
  opacity: 1;
}

.brand-card--active {
  border-color: #86efac;
  background: #f0fdf4;
}

/* Card identity row */
.card-identity {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #334155;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: white;
}

.card-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 5px;
  background: white;
}

.avatar-letter { line-height: 1; }

.card-name-block { min-width: 0; }

.card-brand-name {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-matched {
  font-size: 12px;
  color: #94a3b8;
  margin: 3px 0 0;
}

/* Score area */
.card-score-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.card-score-number-wrap {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.card-score-num {
  font-size: 40px;
  font-weight: 800;
  line-height: 1;
}

.card-score-denom {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 500;
}

.card-label-pill {
  font-size: 12px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 999px;
  white-space: nowrap;
}

/* Dimension mini-bars */
.card-mini-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-bar-label {
  font-size: 11px;
  color: #64748b;
  width: 74px;
  flex-shrink: 0;
  font-weight: 500;
}

.mini-bar-track {
  flex: 1;
  height: 5px;
  background: #f1f5f9;
  border-radius: 999px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.5s ease;
}

.mini-bar-pct {
  font-size: 11px;
  color: #94a3b8;
  width: 28px;
  text-align: right;
  flex-shrink: 0;
}

/* Card footer / CTA */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}

.card-cta-text {
  font-size: 13px;
  font-weight: 600;
  color: #16a34a;
}

.card-arrow {
  color: #16a34a;
  transition: transform 0.15s ease;
}

.brand-card:hover .card-arrow {
  transform: translateX(4px);
}

/* ── Skeleton cards ───────────────────────────────────────────────────────────── */
.brand-card--skeleton { pointer-events: none; }

.sk {
  background: linear-gradient(90deg, #f0f2f5 25%, #e8eaed 50%, #f0f2f5 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.sk-identity {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sk-avatar   { width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0; }
.sk-text     { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.sk-line-long  { height: 14px; width: 70%; }
.sk-line-short { height: 12px; width: 45%; }
.sk-score-block { height: 48px; border-radius: 12px; }

.sk-mini-rows { display: flex; flex-direction: column; gap: 8px; }
.sk-mini-row  { display: flex; align-items: center; gap: 8px; }
.sk-mini-label { width: 60px; height: 10px; flex-shrink: 0; }
.sk-mini-track { flex: 1; height: 5px; border-radius: 999px; }

.sk-cta-bar { height: 12px; width: 50%; border-radius: 6px; }

/* Skeleton detail (modal) */
.detail-skeleton   { display: flex; flex-direction: column; gap: 16px; }
.sk-detail-header  { height: 160px; border-radius: 20px; }
.sk-detail-body    { height: 180px; border-radius: 20px; }
.sk-detail-body-sm { height: 100px; border-radius: 20px; }

/* ── Empty state ─────────────────────────────────────────────────────────────── */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 72px 24px;
  gap: 12px;
}

.empty-icon  { opacity: 0.35; color: #94a3b8; }
.empty-title { font-size: 16px; font-weight: 600; color: #64748b; margin: 0; }
.empty-sub   { font-size: 14px; color: #94a3b8; margin: 0; }

/* ── Pagination ──────────────────────────────────────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
}

.page-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.page-nav-btn:hover:not(:disabled) {
  background: #f0fdf4;
  border-color: #86efac;
  color: #16a34a;
}

.page-nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-number {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1.5px solid #e5e7eb;
  background: white;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-number:hover:not(.page-number--active) {
  background: #f8faf8;
  border-color: #d1d5db;
}

.page-number--active {
  background: #16a34a;
  border-color: #16a34a;
  color: white;
}

.page-ellipsis {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #94a3b8;
  user-select: none;
}

/* ── Modal backdrop ──────────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 18, 32, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* ── Modal panel ─────────────────────────────────────────────────────────────── */
.modal-panel {
  width: 100%;
  max-width: 640px;
  max-height: 88vh;
  background: #f8faf8;
  border-radius: 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow:
    0 24px 64px rgba(15, 23, 42, 0.22),
    0 4px 16px rgba(15, 23, 42, 0.08);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1.5px solid #e5e7eb;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  z-index: 1;
  flex-shrink: 0;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.modal-close:hover {
  background: #f1f5f9;
  border-color: #d1d5db;
  color: #0f172a;
}

.modal-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 56px 24px 28px; /* top padding clears close button */
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Detail cards (inside modal) ─────────────────────────────────────────────── */
.detail-card {
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  padding: 22px;
}

.detail-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.brand-summary-header {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.brand-avatar-large {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 22px;
  color: #334155;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.detail-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 6px;
  background: white;
}

.brand-summary-header h2 {
  font-size: 20px;
  font-weight: 800;
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

.score-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.score-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 22px;
  border-radius: 14px;
  border: 2px solid transparent;
}

.score-badge-inner {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.score-number     { font-size: 36px; font-weight: 800; line-height: 1; }
.score-max        { font-size: 15px; font-weight: 500; opacity: 0.65; }
.score-label-text { font-size: 14px; font-weight: 700; }
.score-desc       { font-size: 14px; color: #475569; line-height: 1.6; margin: 0; }

.scores-desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 16px;
  line-height: 1.5;
}

.policy-list { margin-bottom: 14px; }

.fibre-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.fibre-label { font-size: 14px; color: #334155; }
.fibre-value { font-size: 14px; font-weight: 700; color: #0f172a; }

.brands-chip-list { display: flex; flex-wrap: wrap; gap: 8px; }

.brand-chip {
  background: #f1f5f9;
  color: #334155;
  padding: 5px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
}

.data-source-box { background: #f0f9ff; border-color: #bae6fd; }
.data-source-box p { color: #334155; line-height: 1.7; font-size: 14px; margin: 0 0 14px; }

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: #0369a1;
  color: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.source-link:hover { background: #075985; }
.source-link .cta-arrow { transition: transform 0.15s ease; }
.source-link:hover .cta-arrow { transform: translateX(3px); }

/* ── Modal transition (scale + fade) ─────────────────────────────────────────── */
.modal-fade-enter-active { transition: opacity 240ms ease; }
.modal-fade-leave-active { transition: opacity 200ms ease; }
.modal-fade-enter-from,
.modal-fade-leave-to     { opacity: 0; }

.modal-fade-enter-active .modal-panel {
  animation: modalScaleIn 280ms cubic-bezier(0.22, 1, 0.36, 1);
}
.modal-fade-leave-active .modal-panel {
  animation: modalScaleOut 200ms ease forwards;
}

@keyframes modalScaleIn {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to   { opacity: 1; transform: scale(1)    translateY(0);    }
}

@keyframes modalScaleOut {
  from { opacity: 1; transform: scale(1); }
  to   { opacity: 0; transform: scale(0.95); }
}

/* ── Responsive ──────────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .brand-card-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-container { padding: 24px 16px 56px; }
  .brand-page-header h1 { font-size: 26px; }
  .brand-search-wrap { flex-direction: column; }
  .search-btn { width: 100%; justify-content: center; }
  .brand-card-grid { grid-template-columns: 1fr; gap: 14px; }
  .modal-panel { max-height: 94vh; border-radius: 20px; }
  .pagination { flex-wrap: wrap; }
}
</style>
