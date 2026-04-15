<template>
  <section class="hero">
    <div class="hero-text">
      <p class="eyebrow">FOR SUSTAINABLE FASHION IN AUSTRALIA</p>
      <h1>Your guide to shopping fashion sustainably</h1>
      <p class="subtitle">
        WearImpact shows you where to find second-hand shops near you,
        how transparent your favourite brands really are, and why
        sustainable fashion choices matter.
      </p>

      <div class="hero-buttons">
        <router-link to="/eco-shop" class="primary-btn">Find Eco-Shops Near Me</router-link>
        <router-link to="/brand-search" class="secondary-btn">Check a Brand's Score</router-link>
      </div>

      <p class="trust-line">Free to use · No account needed · Based on Australian locations</p>
    </div>

    <div class="hero-image">
      <img
        src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=900&q=80"
        alt="Person browsing clothes in a second-hand op-shop"
      />
    </div>
  </section>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 48px;
  align-items: center;
  background: #edf5ef;
  border-radius: 24px;
  padding: 56px 48px;
  margin-bottom: 20px;
}

.eyebrow {
  font-size: 13px;
  font-weight: 600;
  color: #16a34a;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 16px;
}

.hero-text h1 {
  font-size: 52px;
  line-height: 1.05;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 20px;
  max-width: 520px;
}

.subtitle {
  font-size: 20px;
  line-height: 1.6;
  color: #475569;
  max-width: 560px;
  margin-bottom: 28px;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.primary-btn,
.secondary-btn {
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: inline-block;
  text-decoration: none;
  font-size: 15px;
}

.primary-btn {
  background: #16a34a;
  color: white;
  transition: background 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}

.primary-btn:hover {
  background: #15803d;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(22, 163, 74, 0.3);
}

.secondary-btn {
  border: 2px solid #16a34a;
  color: #16a34a;
  background: white;
  transition: background 150ms ease, color 150ms ease, transform 150ms ease;
}

.secondary-btn:hover {
  background: #f0fdf4;
  transform: translateY(-1px);
}

.trust-line {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.hero-image img {
  width: 100%;
  height: 420px;
  object-fit: cover;
  object-position: 50% 40%;
  border-radius: 24px;
  display: block;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 32px 20px;
  }

  .hero-text h1 {
    font-size: 38px;
  }

  .subtitle {
    font-size: 18px;
  }

  .hero-image img {
    height: 280px;
  }
}
</style>
