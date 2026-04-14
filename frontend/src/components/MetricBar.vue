<template>
  <div class="metric-row">
    <div class="metric-header">
      <span class="metric-label">{{ label }}</span>
      <span class="metric-value">
        <strong>{{ value }}%</strong>
        <span v-if="raw" class="metric-raw">({{ raw }})</span>
      </span>
    </div>
    <div class="track">
      <div class="fill" :style="{ width: `${value}%`, background: fillColor }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: Number,
  raw: { type: String, default: null },
})

const fillColor = computed(() => {
  if (props.value >= 75) return '#16a34a'
  if (props.value >= 50) return '#65a30d'
  if (props.value >= 30) return '#ca8a04'
  if (props.value >= 10) return '#ea580c'
  return '#dc2626'
})
</script>

<style scoped>
.metric-row {
  margin-bottom: 16px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.metric-label {
  font-size: 14px;
  color: #334155;
}

.metric-value {
  font-size: 13px;
  color: #0f172a;
}

.metric-value strong {
  font-weight: 700;
}

.metric-raw {
  margin-left: 4px;
  color: #94a3b8;
  font-size: 12px;
}

.track {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.5s ease;
}
</style>
