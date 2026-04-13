<template>
  <div class="step-card">
    <div class="step-circle">{{ step }}</div>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  step: String,
  title: String,
  description: String
})
</script>

<style scoped>
.step-card {
  background: white;
  border-radius: 22px;
  padding: 32px 24px;
  text-align: center;
  border: 1px solid #e5e7eb;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.step-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #16a34a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  font-weight: 700;
  font-size: 22px;
}

.step-card h3 {
  font-size: 30px;
  margin-bottom: 12px;
  color: #0f172a;
}

.step-card p {
  color: #475569;
  line-height: 1.6;
}
</style>