<template>
  <footer class="footer">
    <div class="footer-grid">
      <div class="footer-brand">
        <h2><span class="logo-wear">Wear</span><span class="logo-impact">Impact</span></h2>
        <p>
          Helping Australians make more informed, sustainable fashion choices — one purchase at a time.
        </p>
      </div>

      <div>
        <h4>Tools</h4>
        <ul>
          <li><router-link to="/eco-shop">Eco-Shop Navigator</router-link></li>
          <li><router-link to="/brand-search">Brand Search</router-link></li>
          <li><router-link to="/knowledge">Knowledge Hub</router-link></li>
        </ul>
      </div>

      <div>
        <h4>About</h4>
        <ul>
          <li><router-link to="/about">About WearImpact</router-link></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>© 2026 WearImpact. All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #07152d;
  color: white;
  padding: 56px 40px 24px;
  border-radius: 24px 24px 0 0;
  margin-top: 56px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 32px;
}

.footer h2 {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 16px;
}

.logo-wear   { color: #16a34a; }
.logo-impact { color: white; }

.footer h4 {
  color: white;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 600;
}

.footer-brand p {
  color: #d7e0ee;
  line-height: 1.7;
  max-width: 420px;
  font-size: 15px;
}

.footer ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer ul li {
  margin-bottom: 8px;
}

.footer a {
  color: #d7e0ee;
  text-decoration: none;
  font-size: 14px;
  transition: color 150ms ease;
}

.footer a:hover {
  color: #86efac;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  padding-top: 20px;
  text-align: center;
}

.footer-bottom p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}
</style>
