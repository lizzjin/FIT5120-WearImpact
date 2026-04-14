<template>
  <button
    class="brand-item"
    :class="{ active: isActive }"
    @click="$emit('select', brand)"
  >
    <!-- Logo or letter avatar -->
    <div class="brand-avatar" :style="!logoOk ? { background: avatarBg } : {}">
      <img
        v-if="logoOk"
        :src="logoSrc"
        :alt="brand.company_name"
        class="logo-img"
        @error="logoOk = false"
      />
      <span v-else>{{ brand.company_name.charAt(0).toUpperCase() }}</span>
    </div>

    <div class="brand-info">
      <h4>{{ brand.company_name }}</h4>
      <p v-if="brand.matched_brand && brand.matched_brand !== brand.company_name" class="matched-brand">
        via {{ brand.matched_brand }}
      </p>
      <p class="score-line">
        Ethical Score: <strong>{{ brand.overall_score }}</strong>
        <span class="score-label" :style="{ color: labelColor }">{{ brand.score_label }}</span>
      </p>
    </div>
  </button>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

defineEmits(['select'])

const props = defineProps({
  brand: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
})

const LABEL_COLORS = {
  'Great': '#16a34a',
  'Good': '#65a30d',
  "It's a Start": '#ca8a04',
  'Below Average': '#ea580c',
  'Avoid': '#dc2626',
}

const labelColor = computed(() => LABEL_COLORS[props.brand.score_label] || '#64748b')

const avatarBg = computed(() => {
  const palettes = ['#dbeafe', '#dcfce7', '#fef9c3', '#fce7f3', '#ede9fe', '#ffedd5']
  return palettes[props.brand.company_name.charCodeAt(0) % palettes.length]
})

// Clearbit logo with letter-avatar fallback
const logoOk = ref(true)
const logoSrc = computed(() => `https://logo.clearbit.com/${guessDomain(props.brand.company_name)}`)

watch(() => props.brand.company_name, () => { logoOk.value = true })

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
  }
  if (overrides[name]) return overrides[name]
  return name.toLowerCase().replace(/[^a-z0-9]/g, '') + '.com'
}
</script>

<style scoped>
.brand-item {
  width: 100%;
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border: none;
  background: white;
  border-bottom: 1px solid #edf1f5;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.brand-item:hover { background: #f8fafb; }
.brand-item.active { background: #edf5ef; }

.brand-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #334155;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 4px;
  background: white;
}

.brand-info h4 {
  margin-bottom: 2px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 600;
}

.matched-brand {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 2px;
}

.score-line {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.score-label {
  margin-left: 6px;
  font-weight: 600;
  font-size: 12px;
}
</style>
