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
  if (props.value >= 75) return 'var(--color-score-great)'
  if (props.value >= 50) return 'var(--color-score-good)'
  if (props.value >= 30) return 'var(--color-score-start)'
  if (props.value >= 10) return 'var(--color-score-below)'
  return 'var(--color-score-avoid)'
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
.metric-sublabel { font-size: 12px; color: var(--color-text-subtle); line-height: 1.4; }

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
  color: var(--color-text-subtle);
}

.track {
  width: 100%;
  height: 8px;
  background: var(--color-primary-light);
  border-radius: var(--radius-pill);
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: var(--radius-pill);
  transition: width 600ms cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-reduced-motion: reduce) {
  .fill {
    transition: none;
  }
}
</style>
