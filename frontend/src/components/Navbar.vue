<template>
  <nav class="navbar">
    <router-link to="/" class="logo">
      <span class="text-primary font-extrabold">Wear</span><span class="text-text font-extrabold">Impact</span>
    </router-link>

    <!-- Desktop nav links -->
    <div class="nav-links">
      <router-link
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="nav-link"
      >
        {{ link.label }}
      </router-link>
    </div>

    <!-- Mobile hamburger button -->
    <button
      class="hamburger"
      :class="{ open: mobileOpen }"
      @click="mobileOpen = !mobileOpen"
      :aria-expanded="mobileOpen"
      aria-label="Toggle navigation menu"
    >
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
    </button>

    <!-- Mobile overlay menu -->
    <Transition name="mobile-menu">
      <div v-if="mobileOpen" class="mobile-overlay" @click.self="mobileOpen = false">
        <div class="mobile-panel">
          <router-link
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="mobile-link"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </router-link>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const mobileOpen = ref(false)
const route = useRoute()

// Close mobile menu on route change
watch(() => route.path, () => { mobileOpen.value = false })

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/eco-shop', label: 'Eco-Shop' },
  { to: '/brand-search', label: 'Brand Search' },
  { to: '/knowledge', label: 'Knowledge Hub' },
  { to: '/about', label: 'About' },
]
</script>

<style scoped>
/* ── Navbar bar ────────────────────────────────────────────────────────── */
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 32px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px) saturate(1.6);
  -webkit-backdrop-filter: blur(16px) saturate(1.6);
  border-bottom: 1px solid var(--color-border);
  transition: box-shadow var(--transition-base);
}

/* ── Logo ──────────────────────────────────────────────────────────────── */
.logo {
  font-size: 22px;
  letter-spacing: -0.3px;
  text-decoration: none;
  transition: opacity var(--transition-base);
}
.logo:hover { opacity: 0.8; }

/* ── Desktop links ─────────────────────────────────────────────────────── */
.nav-links {
  display: flex;
  gap: 2px;
  align-items: center;
}

.nav-link {
  font-weight: 500;
  font-size: 15px;
  color: var(--color-text-muted);
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 10px;
  position: relative;
  transition: color var(--transition-base), background-color var(--transition-base);
}

.nav-link:hover {
  color: var(--color-text);
  background-color: var(--color-surface-alt);
}

/* Active: green bottom indicator bar */
.nav-link.router-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 14px;
  right: 14px;
  height: 2.5px;
  background: var(--color-primary);
  border-radius: 2px;
}

/* ── Hamburger (hidden on desktop) ─────────────────────────────────────── */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 36px;
  height: 36px;
  padding: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 8px;
  transition: background var(--transition-base);
}

.hamburger:hover { background: var(--color-surface-alt); }

.hamburger-line {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--color-text);
  border-radius: 2px;
  transition: transform 300ms ease, opacity 200ms ease;
  transform-origin: center;
}

.hamburger.open .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger.open .hamburger-line:nth-child(2) {
  opacity: 0;
}
.hamburger.open .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* ── Mobile overlay (hidden on desktop) ────────────────────────────────── */
.mobile-overlay {
  display: none;
}

/* ── Mobile menu transition ────────────────────────────────────────────── */
.mobile-menu-enter-active { transition: opacity 250ms ease; }
.mobile-menu-leave-active { transition: opacity 200ms ease; }
.mobile-menu-enter-from,
.mobile-menu-leave-to { opacity: 0; }

.mobile-menu-enter-active .mobile-panel {
  animation: slideDown 280ms cubic-bezier(0.22, 1, 0.36, 1);
}
.mobile-menu-leave-active .mobile-panel {
  animation: slideUp 200ms ease forwards;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-12px); }
}

/* ── Responsive ────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .navbar {
    padding: 12px 20px;
  }

  .nav-links { display: none; }
  .hamburger { display: flex; }

  .mobile-overlay {
    display: block;
    position: fixed;
    inset: 0;
    top: 57px; /* navbar height */
    z-index: 49;
    background: rgba(10, 18, 32, 0.3);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
  }

  .mobile-panel {
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
    padding: 8px 16px 16px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .mobile-link {
    display: block;
    padding: 14px 16px;
    font-size: 16px;
    font-weight: 500;
    color: var(--color-text-muted);
    text-decoration: none;
    border-radius: 12px;
    transition: color var(--transition-base), background var(--transition-base);
  }

  .mobile-link:hover,
  .mobile-link:active {
    color: var(--color-text);
    background: var(--color-surface-alt);
  }

  .mobile-link.router-link-active {
    color: var(--color-primary);
    font-weight: 600;
    background: var(--color-primary-lighter);
  }
}
</style>
