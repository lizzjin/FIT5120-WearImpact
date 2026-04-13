<template>
  <div class="metric-row">
    <div class="metric-header">
      <span>{{ label }}</span>
      <strong>{{ value }}%</strong>
    </div>
    <div class="track">
      <div class="fill" :style="{ width: `${value}%` }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: Number
})
</script>

<style scoped>
.metric-row {
  margin-bottom: 18px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #334155;
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
  background: #2563eb;
  border-radius: 999px;
}
</style>