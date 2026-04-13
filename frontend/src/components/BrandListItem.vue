<template>
  <button
    class="brand-item"
    :class="{ active: isActive }"
    @click="$emit('select', brand)"
  >
    <div class="brand-avatar">{{ brand.shortName }}</div>

    <div class="brand-info">
      <h4>{{ brand.name }}</h4>
      <p>
        Score: <strong>{{ brand.score }}</strong>
        <span>{{ brand.ratingLabel }}</span>
      </p>
    </div>
  </button>
</template>

<script setup>
defineEmits(['select'])

defineProps({
  brand: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.brand-item {
  width: 100%;
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: none;
  background: white;
  border-bottom: 1px solid #edf1f5;
  text-align: left;
  cursor: pointer;
}

.brand-item.active {
  background: #edf5ef;
}

.brand-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #eef1f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #334155;
  flex-shrink: 0;
}

.brand-info h4 {
  margin-bottom: 4px;
  font-size: 18px;
  color: #0f172a;
}

.brand-info p {
  font-size: 14px;
  color: #64748b;
}
</style>