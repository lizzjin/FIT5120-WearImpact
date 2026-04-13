<template>
  <div class="stats-card">
    <div class="icon-box">{{ icon }}</div>

    <div class="stats-text">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: '•'
  },
  title: String,
  description: String
})
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
  background: #f8fafc;
  color: #16a34a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 16px;
}

.stats-text h3 {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.stats-text p {
  font-size: 15px;
  color: #64748b;
  line-height: 1.5;
}
</style>