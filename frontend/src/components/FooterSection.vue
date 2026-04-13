<template>
  <footer class="footer">
    <div class="footer-grid">
      <div>
        <h2>WearImpact</h2>
        <p>
Supporting sustainable fashion through local action and learning.
        </p>
      </div>

      <div>
        <h4>Tools</h4>
        <ul>
          <li><router-link to="/eco-shop">Eco-Shop</router-link></li>
          <li><router-link to="/knowledge">Knowledge Hub</router-link></li>
          <li><router-link to="/about">About</router-link></li>
        </ul>
      </div>

      <div>
        <h4>About</h4>
        <p>
Helping users find local eco-shop options and build sustainable fashion awareness.
        </p>
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
  grid-template-columns: 1.3fr 1fr 1.2fr;
  gap: 40px;
  margin-bottom: 32px;
}

.footer h2,
.footer h4 {
  margin-bottom: 16px;
}

.footer p,
.footer li,
.footer a {
  color: #d7e0ee;
  line-height: 1.7;
  text-decoration: none;
}

.footer-brand p {
  max-width: 420px;
}
.footer ul {
  list-style: none;
  padding: 0;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  padding-top: 20px;
  text-align: center;
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}
</style>