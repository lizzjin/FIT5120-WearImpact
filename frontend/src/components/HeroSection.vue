<template>
  <section class="hero">
    <div class="hero-text">
      <h1>Make Better Sustainable Fashion Choices</h1>
      <p>
        WearImpact helps users make more responsible fashion choices by discovering local eco-shop options and learning key sustainable fashion knowledge.
      </p>

      <div class="hero-buttons">
        <router-link to="/eco-shop" class="primary-btn">Explore Eco-Shops</router-link>
        <router-link to="/about" class="secondary-btn">Learn More</router-link>
      </div>
    </div>

    <div class="hero-image">
      <img
        src="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80"
        alt="Sustainable fashion"
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

.hero-text h1 {
  font-size: 56px;
  line-height: 1.05;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 20px;
  max-width: 580px;
}

.hero-text p {
  font-size: 20px;
  line-height: 1.6;
  color: #475569;
  max-width: 620px;
  margin-bottom: 28px;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: inline-block;
  text-decoration: none;
}

.primary-btn {
  background: #16a34a;
  color: white;
}

.secondary-btn {
  border: 2px solid #16a34a;
  color: #16a34a;
  background: white;
}

.hero-image img {
  width: 100%;
  height: 420px;
  object-fit: cover;
  object-position: 50% 28%;
  border-radius: 24px;
  display: block;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 32px 20px;
  }

  .hero-text h1 {
    font-size: 40px;
  }

  .hero-text p {
    font-size: 18px;
  }

  .hero-image img {
    height: 280px;
  }
}
</style>