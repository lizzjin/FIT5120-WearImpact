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
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  padding: 22px 24px;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.1s;
}

.location-card:hover {
  border-color: #16a34a;
  box-shadow: 0 6px 20px rgba(22, 163, 74, 0.12);
  transform: translateY(-1px);
}

.location-card.selected {
  border-color: #16a34a;
  border-left: 4px solid #16a34a;
  background: #f0fdf4;
}

.location-card:focus-visible {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
}

/* Header row */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.location-card h3 {
  font-size: 18px;
  color: #0f172a;
  margin: 0;
  line-height: 1.4;
}

/* Type badge */
.type-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.type-badge.second_hand_shop { background: #dcfce7; color: #166534; }
.type-badge.donation_point   { background: #dbeafe; color: #1e40af; }
.type-badge.recycling         { background: #fef3c7; color: #92400e; }

/* Distance */
.distance {
  margin: 0 0 8px;
  color: #475569;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.distance-icon {
  flex-shrink: 0;
  color: #64748b;
}

/* Hint text */
.hint {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
}
</style>
