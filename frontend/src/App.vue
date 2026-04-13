<!-- <template>
  <div class="home-page">
    <HeroSection />

    <section class="stats-section">
      <div class="stats-grid">
        <StatsCard
          v-for="item in statsData"
          :key="item.id"
          :title="item.title"
          :description="item.description"
        />
      </div>
    </section>

    <section class="features-section">
      <div class="section-heading">
        <h2>Core Features for Iteration 1</h2>
        <p>
          Explore the first set of tools designed to support local sustainable fashion action.
        </p>
      </div>

      <div class="features-grid">
        <FeatureCard
          v-for="item in featureData"
          :key="item.id"
          :title="item.title"
          :description="item.description"
        />
      </div>
    </section>

    <section class="steps-section">
      <div class="section-heading">
        <h2>How It Works</h2>
        <p>Simple steps to explore sustainable fashion options in your local area.</p>
      </div>

      <div class="steps-grid">
        <StepCard
          v-for="item in stepsData"
          :key="item.id"
          :step="item.step"
          :title="item.title"
          :description="item.description"
        />
      </div>
    </section>

    <section class="cta-section">
      <h2>Ready to Explore Sustainable Fashion Locally?</h2>
      <p>Start with nearby eco-shops and practical sustainability knowledge.</p>
      <button class="cta-button">Start Exploring</button>
    </section>

    <FooterSection />
  </div>
</template>

<script setup>
import HeroSection from './components/HeroSection.vue'
import StatsCard from './components/StatsCard.vue'
import FeatureCard from './components/FeatureCard.vue'
import StepCard from './components/StepCard.vue'
import FooterSection from './components/FooterSection.vue'
import { statsData, featureData, stepsData } from './data/homeContent'

</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
  background: #f8faf8;
}
.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.features-section,
.steps-section {
  padding: 20px 0;
}

.section-heading {
  text-align: center;
  margin-bottom: 28px;
}

.section-heading h2 {
  font-size: 40px;
  color: #0f172a;
  margin-bottom: 10px;
}

.section-heading p {
  font-size: 18px;
  color: #475569;
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.steps-section {
  background: #f3f4f6;
  padding: 48px 28px;
  border-radius: 24px;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.cta-section {
  text-align: center;
  padding: 48px 20px 24px;
}

.cta-section h2 {
  font-size: 42px;
  color: #0f172a;
  margin-bottom: 12px;
}

.cta-section p {
  font-size: 18px;
  color: #475569;
  margin-bottom: 24px;
}

.cta-button {
  display: inline-block;
  background: #16a34a;
  color: white;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

@media (max-width: 900px) {
  .stats-grid,
  .features-grid,
  .steps-grid {
    grid-template-columns: 1fr;
  }

  .section-heading h2,
  .cta-section h2 {
    font-size: 32px;
  }

  .section-heading p,
  .cta-section p {
    font-size: 16px;
  }
}
</style> -->
<template>
  <div class="app-container">
    <router-view />
  </div>
</template>