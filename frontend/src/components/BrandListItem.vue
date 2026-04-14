<template>
  <button
    class="brand-item"
    :class="{ active: isActive }"
    @click="$emit('select', brand)"
  >
    <div class="brand-avatar" :style="{ background: avatarBg }">
      {{ brand.company_name.charAt(0).toUpperCase() }}
    </div>

    <div class="brand-info">
      <h4>{{ brand.company_name }}</h4>
      <p v-if="brand.matched_brand && brand.matched_brand !== brand.company_name" class="matched-brand">
        via {{ brand.matched_brand }}
      </p>
      <p class="score-line">
        Score: <strong>{{ brand.overall_score }}</strong>
        <span class="score-label" :style="{ color: labelColor }">{{ brand.score_label }}</span>
      </p>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'

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

// Deterministic pastel background from company name
const avatarBg = computed(() => {
  const palettes = ['#dbeafe', '#dcfce7', '#fef9c3', '#fce7f3', '#ede9fe', '#ffedd5']
  const idx = props.brand.company_name.charCodeAt(0) % palettes.length
  return palettes[idx]
})
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

.brand-item:hover {
  background: #f8fafb;
}

.brand-item.active {
  background: #edf5ef;
}

.brand-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #334155;
  flex-shrink: 0;
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
