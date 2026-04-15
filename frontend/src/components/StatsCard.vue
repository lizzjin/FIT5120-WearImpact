<template>
  <div class="stats-card">
    <div class="icon-box">
      <component :is="iconComponent" :size="28" :stroke-width="1.75" />
    </div>

    <div class="stats-text">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Recycle, Search, Leaf, Star } from 'lucide-vue-next'

const ICON_MAP = { Recycle, Search, Leaf, Star }

const props = defineProps({
  icon: {
    type: String,
    default: 'Star'
  },
  title: String,
  description: String
})

const iconComponent = computed(() => ICON_MAP[props.icon] ?? Star)
</script>

<style scoped>
.stats-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
}

.icon-box {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: #f0fdf4;
  color: #16a34a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  border: 1px solid #bbf7d0;
}

.stats-text h3 {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.stats-text p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}
</style>