<template>
  <div
    class="topic-card"
    :class="{ active: isActive }"
    @click="$emit('select', topic)"
  >
    <h3>{{ topic.title }}</h3>
  </div>
</template>

<script setup>
defineEmits(['select'])

defineProps({
  topic: {
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
.topic-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 20px;
  cursor: pointer;
  transition: 0.2s ease;
}

.topic-card:hover {
  border-color: #16a34a;
  transform: translateY(-2px);
}

.topic-card.active {
  border-color: #16a34a;
  background: #f0fdf4;
}

.topic-card h3 {
  font-size: 22px;
  color: #0f172a;
}
</style>