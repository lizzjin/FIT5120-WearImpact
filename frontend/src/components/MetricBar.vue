<template>
  <div class="metric-row">
    <div class="metric-header">
      <span class="metric-label">{{ label }}</span>
      <span class="metric-value">
        <span v-if="raw" class="metric-raw">{{ raw }}</span>
        <strong :style="{ color: fillColor }">{{ value }}%</strong>
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
  margin-bottom: 18px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #334155;
  flex: 1;
}

.metric-value {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.metric-value strong {
  font-size: 14px;
  font-weight: 700;
  min-width: 38px;
  text-align: right;
}

.metric-raw {
  font-size: 12px;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2px 7px;
  border-radius: 6px;
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
