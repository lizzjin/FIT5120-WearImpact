<template>
  <div class="about-page">
    <Navbar />

    <div class="page-container">
      <section
        class="about-hero"
        v-motion
        :initial="{ opacity: 0, y: 24 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 600 } }"
      >
        <h1>About WearImpact</h1>
        <p>
          WearImpact helps users explore practical ways to support sustainable fashion
          through local action and accessible learning.
        </p>
      </section>

      <section class="about-content">
        <div
          v-for="(card, i) in contentCards"
          :key="card.title"
          class="content-card"
          v-motion
          :initial="{ opacity: 0, y: 28 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 150 * i } }"
        >
          <div class="card-accent"></div>
          <h2>{{ card.title }}</h2>
          <p>{{ card.body }}</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'

const contentCards = [
  {
    title: 'Our Purpose',
    body: 'WearImpact is designed to support more responsible clothing choices by helping users discover nearby second-hand shops, donation points, and textile recycling locations. It also provides simple sustainability knowledge to help users build awareness and take practical action.',
  },
  {
    title: 'What Users Can Do',
    body: 'Users can search for local eco-shop options, view useful location details, access directions, and explore key sustainable fashion topics such as materials, clothing waste, and responsible consumption.',
  },
]
</script>

<style scoped>
.about-page {
  background: var(--color-bg);
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

/* ── Hero ──────────────────────────────────────────────────────────────────── */
.about-hero {
  background: linear-gradient(135deg, #edf5ef 0%, #dcfce7 100%);
  border-radius: 24px;
  padding: 48px 40px;
  margin-bottom: 28px;
  text-align: center;
}

.about-hero h1 {
  font-size: 44px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.about-hero p {
  font-size: 18px;
  color: var(--color-text-muted);
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto;
}

/* ── Content cards ─────────────────────────────────────────────────────────── */
.about-content {
  display: grid;
  gap: 24px;
}

.content-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  padding: 32px 32px 32px 36px;
  box-shadow: var(--shadow-card);
  position: relative;
  overflow: hidden;
  transition: box-shadow 300ms ease, transform 300ms ease;
}

.content-card:hover {
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

/* Green left accent bar */
.card-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--color-primary);
  border-radius: 4px 0 0 4px;
}

.content-card h2 {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 14px;
}

.content-card p {
  font-size: 17px;
  color: var(--color-text-muted);
  line-height: 1.8;
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .about-hero h1 {
    font-size: 32px;
  }

  .content-card h2 {
    font-size: 22px;
  }

  .content-card p,
  .about-hero p {
    font-size: 15px;
  }
}
</style>
