<template>
  <div class="feature-card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <router-link :to="link" class="explore-link">Explore</router-link>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  description: String, 
  link: {
    type: String,
    default: '/'
  }
})
</script>

<style scoped>
.feature-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
  min-height: 200px;
  text-align: center;
}

.feature-card h3 {
  font-size: 24px;
  margin-bottom: 14px;
  color: #0f172a;
}

.feature-card p {
  color: #475569;
  line-height: 1.7;
  margin-bottom: 20px;
}

.explore-link {
  color: #16a34a;
  font-weight: 600;
  text-decoration: none;
}
</style>