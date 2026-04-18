<template>
  <div
    class="location-card"
    :class="{ selected: isSelected }"
    @click="$emit('select', place)"
    @keydown.enter="$emit('select', place)"
    @keydown.space.prevent="$emit('select', place)"
    role="button"
    tabindex="0"
    :aria-pressed="isSelected"
  >
    <div class="card-header">
      <h3>{{ place.name }}</h3>
      <span class="type-badge" :class="place.type">{{ typeLabel }}</span>
    </div>

    <p class="distance">
      <MapPin class="distance-icon" :size="14" :stroke-width="2.2" />
      {{ place.distance_km }} km away
    </p>

    <p v-if="!isSelected" class="hint">Click to view details &amp; directions</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin } from 'lucide-vue-next'

const props = defineProps({
  place: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
})

defineEmits(['select'])

const TYPE_LABELS = {
  second_hand_shop: 'Second-hand',
  donation_point:   'Donation',
  recycling:        'Recycling',
}

const typeLabel = computed(() => TYPE_LABELS[props.place.type] || props.place.type)
</script>

<style scoped>
.location-card {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: 22px 24px;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition:
    border-color 200ms ease,
    box-shadow 200ms ease,
    transform 150ms ease,
    background 200ms ease;
}

.location-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 20px rgba(22, 163, 74, 0.12);
  transform: translateY(-2px);
}

.location-card.selected {
  border-color: var(--color-primary);
  border-left: 4px solid var(--color-primary);
  background: var(--color-primary-lighter);
}

.location-card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.location-card h3 {
  font-size: 18px;
  color: var(--color-text);
  margin: 0;
  line-height: 1.4;
}

.type-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.type-badge.second_hand_shop { background: #dcfce7; color: #166534; }
.type-badge.donation_point   { background: #dbeafe; color: #1e40af; }
.type-badge.recycling         { background: #fef3c7; color: #92400e; }

.distance {
  margin: 0 0 8px;
  color: var(--color-text-muted);
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.distance-icon {
  flex-shrink: 0;
  color: var(--color-text-subtle);
}

.hint {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-faint);
}
</style>
