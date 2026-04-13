<template>
  <div class="home-page">
    <Navbar />

    <HeroSection />

    <section class="stats-section">
      <div class="stats-grid">
<StatsCard
  v-for="item in statsData"
  :key="item.id"
  :icon="item.icon"
  :title="item.title"
  :description="item.description"
/>
      </div>
    </section>
<section class="features-section"></section>
<div class="section-heading">
  <h2>How WearImpact Helps</h2>
  <p>
    Explore practical ways to take local action and learn more about sustainable fashion.
  </p>
</div>

<div class="features-grid features-grid-two">
  <FeatureCard
    v-for="item in featureData"
    :key="item.id"
    :title="item.title"
    :description="item.description"
    :link="item.link"
  />
</div>

      <div class="features-grid">
        <FeatureCard
          v-for="item in featureCardsWithLinks"
          :key="item.id"
          :title="item.title"
          :description="item.description"
          :link="item.link"
        />
      </div>


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
      <router-link to="/eco-shop" class="cta-button">Start Exploring</router-link>
    </section>

    <FooterSection />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import HeroSection from '../components/HeroSection.vue'
import StatsCard from '../components/StatsCard.vue'
import FeatureCard from '../components/FeatureCard.vue'
import StepCard from '../components/StepCard.vue'
import FooterSection from '../components/FooterSection.vue'
import { statsData, featureData, stepsData } from '../data/homeContent'
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.stats-section {
  padding: 14px 0 18px;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.stats-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 64px;
  align-items: center;
  padding: 22px 0;
}
.section-heading {
  text-align: center;
  margin-bottom: 28px;
}

.section-heading h2 {
  font-size: 42px;
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
.features-grid-two {
  max-width: 1100px;
  margin: 0 auto;
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
  font-size: 52px;
  color: #0f172a;
  margin-bottom: 12px;
}

.cta-section p {
  font-size: 20px;
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
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

  .section-heading h2,
  .cta-section h2 {
    font-size: 34px;
  }

  .section-heading p,
  .cta-section p {
    font-size: 18px;
  }

</style>