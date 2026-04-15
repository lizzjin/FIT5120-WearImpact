<template>
  <nav class="navbar">
    <router-link to="/" class="logo">
      <span class="logo-wear">Wear</span><span class="logo-impact">Impact</span>
    </router-link>
    <div class="nav-links">
      <router-link to="/" aria-current="page">Home</router-link>
      <router-link to="/eco-shop">Eco-Shop</router-link>
      <router-link to="/brand-search">Brand Search</router-link>
      <router-link to="/knowledge">Knowledge Hub</router-link>
      <router-link to="/about">About</router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.logo {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.3px;
  text-decoration: none;
  transition: opacity 150ms ease;
}

.logo:hover { opacity: 0.8; }

.logo-wear   { color: #16a34a; }
.logo-impact { color: #0f172a; }

.nav-links {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.nav-links a {
  font-weight: 500;
  font-size: 15px;
  color: #475569;
  text-decoration: none;
  padding: 7px 12px;
  border-radius: 8px;
  transition: color 150ms ease, background-color 150ms ease;
}

.nav-links a:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

/* Active state: underline + tint background */
.nav-links a.router-link-active:not(.nav-cta) {
  color: #16a34a;
  background-color: #f0fdf4;
  font-weight: 600;
  text-decoration: underline;
  text-decoration-color: #16a34a;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
}


@media (max-width: 900px) {
  .navbar {
    flex-direction: column;
    gap: 12px;
    padding: 14px 20px;
  }

  .nav-links {
    gap: 4px;
    justify-content: center;
  }

}
</style>
