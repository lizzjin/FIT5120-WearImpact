<template>
  <div class="about-page">
    <Navbar />

    <div class="page-container">
      <section class="about-hero">
        <h1>About WearImpact</h1>
        <p>
          WearImpact helps users explore practical ways to support sustainable fashion
          through local action and accessible learning.
        </p>
      </section>

      <section class="about-content">
        <div class="content-card">
          <h2>Our Purpose</h2>
          <p>
            WearImpact is designed to support more responsible clothing choices by
            helping users discover nearby second-hand shops, donation points, and
            textile recycling locations. It also provides simple sustainability knowledge
            to help users build awareness and take practical action.
          </p>
        </div>

        <div class="content-card">
          <h2>What Users Can Do</h2>
          <p>
            Users can search for local eco-shop options, view useful location details,
            access directions, and explore key sustainable fashion topics such as
            materials, clothing waste, and responsible consumption.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
</script>

<style scoped>
.about-page {
  background: #f8faf8;
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

.about-hero {
  background: #edf5ef;
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 24px;
  text-align: center;
}

.about-hero h1 {
  font-size: 48px;
  color: #0f172a;
  margin-bottom: 12px;
}

.about-hero p {
  font-size: 18px;
  color: #475569;
  line-height: 1.6;
  max-width: 760px;
  margin: 0 auto;
}

.about-content {
  display: grid;
  gap: 24px;
}

.content-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.content-card h2 {
  font-size: 32px;
  color: #0f172a;
  margin-bottom: 16px;
}

.content-card p {
  font-size: 18px;
  color: #475569;
  line-height: 1.8;
}

</style>