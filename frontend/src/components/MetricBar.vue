<template>
  <div class="metric-row">
    <div class="metric-header">
      <div class="metric-labels">
        <span class="metric-label">{{ label }}</span>
        <span v-if="sublabel" class="metric-sublabel">{{ sublabel }}</span>
      </div>
      <strong class="metric-pct" :style="{ color: fillColor }">
        {{ value }}%
        <span v-if="rawScore != null && maxScore != null" class="metric-raw">
          ({{ rawScore }}/{{ maxScore }} pts)
        </span>
      </strong>
    </div>
    <div
      class="track"
      role="progressbar"
      :aria-valuenow="value"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`${label} score: ${value}%`"
    >
      <div class="fill" :style="{ width: `${value}%`, background: fillColor }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  sublabel: { type: String, default: null },
  value: Number,
  rawScore: { type: Number, default: null },
  maxScore: { type: Number, default: null },
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
.metric-row { margin-bottom: 18px; }

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}

.metric-labels { display: flex; flex-direction: column; gap: 2px; flex: 1; }

.metric-label { font-size: 14px; font-weight: 600; color: #1e293b; }

.metric-sublabel { font-size: 12px; color: #64748b; line-height: 1.4; }

.metric-pct {
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.metric-raw {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}

.track {
  width: 100%;
  height: 8px;
  background: #dcfce7;
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.5s ease;
}

@media (prefers-reduced-motion: reduce) {
  .fill {
    transition: none;
  }
}
</style>
