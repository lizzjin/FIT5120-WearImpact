<template>
  <div class="location-card">
    <h3>{{ location.name }}</h3>
    <p><strong>Type:</strong> {{ location.type }}</p>
    <p><strong>Distance:</strong> {{ location.distance }}</p>
    <p><strong>Address:</strong> {{ location.address }}</p>
    <p><strong>Opening Hours:</strong> {{ location.openingHours }}</p>
    <button>Get Directions</button>
  </div>
</template>

<script setup>
defineProps({
  location: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.location-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.location-card h3 {
  font-size: 24px;
  color: #0f172a;
  margin-bottom: 16px;
}

.location-card p {
  margin-bottom: 10px;
  color: #475569;
  line-height: 1.7;
  font-size: 17px;
}

.location-card button {
  margin-top: 14px;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}
</style>