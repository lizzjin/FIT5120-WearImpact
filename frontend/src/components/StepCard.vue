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
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  transition: box-shadow 200ms ease, transform 200ms ease;
}

.step-card:hover {
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
  transform: translateY(-2px);
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #16a34a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-weight: 700;
  font-size: 18px;
}

.step-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #0f172a;
}

.step-card p {
  font-size: 14px;
  color: #475569;
  line-height: 1.65;
}
</style>