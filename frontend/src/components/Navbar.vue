<template>
  <nav class="navbar">
<router-link to="/" class="logo">WearImpact</router-link>
    <div class="nav-links">
      <router-link to="/">Home</router-link>
      <router-link to="/eco-shop">Eco-Shop</router-link>
      <router-link to="/brand-search">Brand Search</router-link>
      <router-link to="/knowledge">Knowledge Hub</router-link>
      <router-link to="/about">About</router-link>

    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.logo {
  font-size: 30px;
  font-weight: 800;
  color: #16a34a;
}

.nav-links {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
}

.nav-links a {
  font-weight: 500;
  color: #334155;
  text-decoration: none;
}

.nav-links a.router-link-active {
  color: #16a34a;
}

@media (max-width: 900px) {
  .navbar {
    flex-direction: column;
    gap: 16px;
  }
}
</style>