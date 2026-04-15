<template>
  <router-link :to="link" class="feature-card">
    <div v-if="image" class="card-image">
      <img :src="image" :alt="title" loading="lazy" />
    </div>
    <div class="card-body">
      <div class="icon-box">
        <component :is="iconComponent" :size="32" :stroke-width="1.75" />
      </div>
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
      <span class="explore-link">
        Explore
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </span>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin, Search, BookOpen, Star } from 'lucide-vue-next'

const ICON_MAP = { MapPin, Search, BookOpen, Star }

const props = defineProps({
  icon: { type: String, default: 'Star' },
  title: String,
  description: String,
  link: { type: String, default: '/' },
  image: { type: String, default: null }
})

const iconComponent = computed(() => ICON_MAP[props.icon] ?? Star)
</script>

<style scoped>
.feature-card {
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 200ms ease, box-shadow 200ms ease, transform 200ms ease;
}

.feature-card:hover {
  border-color: #16a34a;
  box-shadow: 0 8px 28px rgba(22, 163, 74, 0.12);
  transform: translateY(-3px);
}

.card-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 400ms ease;
}

.feature-card:hover .card-image img {
  transform: scale(1.04);
}

.card-body {
  display: flex;
  flex-direction: column;
  padding: 24px;
  flex: 1;
}

.icon-box {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #f0fdf4;
  color: #16a34a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  border: 1px solid #bbf7d0;
  flex-shrink: 0;
}

.feature-card h3 {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #0f172a;
  line-height: 1.3;
}

.feature-card p {
  color: #475569;
  line-height: 1.65;
  margin-bottom: 20px;
  flex: 1;
  font-size: 15px;
}

.explore-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #16a34a;
  font-weight: 600;
  font-size: 14px;
  transition: gap 150ms ease;
}

.feature-card:hover .explore-link {
  gap: 10px;
}
</style>
