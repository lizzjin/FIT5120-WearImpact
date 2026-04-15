<template>
  <div class="home-page" ref="pageRef">
    <Navbar />

    <!-- §1 Hero — split: warm cream left / editorial image right -->
    <section class="snap-section s-hero">
      <div class="s-hero-left section-animate">
        <p class="eyebrow">FOR SUSTAINABLE FASHION IN AUSTRALIA</p>
        <h1>Look good.<br />Feel good.<br />Choose better.</h1>
        <p class="hero-sub">
          Fast fashion gives instant joy.<br />
          But its impact lasts far longer than trends.
        </p>
        <p class="hero-stat">
          Every year, Australians throw away <strong>220,000 tonnes</strong> of clothing.
          Most of it was bought with good intentions.
        </p>
        <span class="scroll-hint">Scroll to explore <span class="bounce">↓</span></span>
      </div>
      <div class="s-hero-right">
        <img
          src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80"
          alt="Minimal fashion store"
        />
      </div>
    </section>

    <!-- §2 Sound Familiar? — full-bleed dark overlay (editorial standard for emotional copy) -->
    <section class="snap-section s-familiar">
      <img
        class="bg-img"
        src="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1600&q=80"
        alt=""
      />
      <div class="bg-overlay"></div>
      <div class="s-familiar-content section-animate">
        <h2>Sound familiar?</h2>
        <div class="questions">
          <p>"Bought something because it was on sale?"</p>
          <p>"Worn an outfit once, then forgot about it?"</p>
          <p>"Have clothes in your wardrobe you never touch?"</p>
        </div>
        <p class="familiar-stat">
          You're not alone —
          <strong>84% of Australians</strong> own clothes they haven't worn in over a year.
        </p>
      </div>
    </section>

    <!-- §3 Hidden Cost — impact data on dark environmental image -->
    <section class="snap-section s-cost">
      <img
        class="bg-img"
        src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=1600&q=80"
        alt=""
      />
      <div class="bg-overlay dark"></div>
      <div class="s-cost-content section-animate">
        <p class="eyebrow light">THE HIDDEN COST OF EVERY TREND</p>
        <div class="stat-row">
          <div v-for="stat in impactStats" :key="stat.number" class="stat-card">
            <p class="stat-num">{{ stat.number }}</p>
            <p class="stat-lbl">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- §4 Bridge — transition from problem to solution -->
    <section class="snap-section s-bridge">
      <div class="s-bridge-left section-animate">
        <h2>Sustainable choices<br />shouldn't feel hard.</h2>
        <p class="bridge-sub">You don't need to stop loving fashion.</p>
        <p class="bridge-em">You just need better information.</p>
        <p class="bridge-hint">Here's how WearImpact helps ↓</p>
      </div>
      <div class="s-bridge-right">
        <img
          src="https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1200&q=80"
          alt="Sustainable fashion choices"
        />
      </div>
    </section>

    <!-- §5–7 Solution sections — each is a problem + solution + CTA link -->
    <section
      v-for="(sol, i) in solutions"
      :key="sol.id"
      class="snap-section s-solution"
      :class="{ reverse: i % 2 === 1 }"
    >
      <div class="sol-text section-animate">
        <p class="sol-problem">{{ sol.problem }}</p>
        <h2>{{ sol.title }}</h2>
        <p class="sol-desc">{{ sol.description }}</p>
        <router-link :to="sol.link" class="sol-cta">
          {{ sol.cta }} <ArrowRight :size="17" :stroke-width="2.5" class="cta-arrow" />
        </router-link>
      </div>
      <div class="sol-image">
        <img :src="sol.image" :alt="sol.title" />
      </div>
    </section>

    <!-- Footer gets its own snap point so it's always reachable -->
    <div class="footer-snap">
      <FooterSection />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import FooterSection from '../components/FooterSection.vue'
import { ArrowRight } from 'lucide-vue-next'

const pageRef = ref(null)
let currentIndex = 0
let isAnimating = false  // used only for keyboard lock
let rafId = null
let lastWheelTime = 0
const WHEEL_THROTTLE = 120 // ms — filters duplicate events from the same scroll notch
let observer = null

const impactStats = [
  {
    number: '220,000 t',
    label: 'of clothing sent to landfill every year in Australia'
  },
  {
    number: '14.5M t',
    label: 'of CO₂ from fashion-related carbon emissions'
  },
  {
    number: '1.8B t',
    label: 'of water used by the global fashion industry annually'
  }
]

const solutions = [
  {
    id: 5,
    problem: "You want to shop sustainably — but you don't know where to start.",
    title: 'Find second-hand stores near you.',
    description:
      'WearImpact maps every op-shop, donation point and textile recycling centre within your chosen radius\u00A0— with directions and opening hours.',
    cta: 'Find Eco-Shops Near Me',
    link: '/eco-shop',
    image:
      'https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?auto=format&fit=crop&w=1200&q=80'
  },
  {
    id: 6,
    problem: 'A brand says "sustainable." But is it really?',
    title: 'See how transparent your brands are.',
    description:
      'Search any clothing brand and see its real score\u00A0—\u00A0across policy, environment, and supply chain\u00A0—\u00A0based on the Fashion Transparency Index.',
    cta: 'Search a Brand',
    link: '/brand-search',
    image:
      'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80'
  },
  {
    id: 7,
    problem: "It's hard to choose better when you don't know what to look for.",
    title: 'Learn what actually matters.',
    description:
      'WearImpact breaks down the real issues\u00A0—\u00A0materials, supply chains, waste\u00A0—\u00A0in plain language so you can make more informed choices.',
    cta: 'Start Learning',
    link: '/knowledge',
    image:
      'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=1200&q=80'
  }
]

function getSections() {
  const page = pageRef.value
  if (!page) return []
  return [...page.querySelectorAll('.snap-section, .footer-snap')]
}

// Ease-in-out cubic — smooth deceleration at both ends
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
}

// RAF-based scrollTop animation — no browser scroll engine involved.
// If called while an animation is running, it immediately snaps to that
// animation's target and starts the new one — zero wait, instant response.
function scrollToSection(index) {
  const page = pageRef.value
  const sections = getSections()
  if (index < 0 || index >= sections.length || !page) return

  // Cancel any running animation — keep scrollTop exactly where it is
  // so the new animation continues from the current mid-scroll position
  // without any visual jump or flash.
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }

  currentIndex = index
  isAnimating = true

  const startTop = page.scrollTop // current position, may be mid-animation
  const targetTop = sections[index].offsetTop
  const distance = targetTop - startTop
  const duration = 600 // shorter = snappier response
  const startTime = performance.now()

  function step(now) {
    const elapsed = now - startTime
    const t = Math.min(elapsed / duration, 1)
    page.scrollTop = startTop + distance * easeInOutCubic(t)

    if (t < 1) {
      rafId = requestAnimationFrame(step)
    } else {
      page.scrollTop = targetTop
      rafId = null
      isAnimating = false
    }
  }

  rafId = requestAnimationFrame(step)
}

// Throttle filters rapid-fire events from the same scroll notch (typically
// 3–5 events within ~30ms on Windows). Each distinct notch advances one section.
function onWheel(e) {
  e.preventDefault()
  const now = Date.now()
  if (now - lastWheelTime < WHEEL_THROTTLE) return
  lastWheelTime = now
  scrollToSection(currentIndex + (e.deltaY > 0 ? 1 : -1))
}

function onKeyDown(e) {
  if (isAnimating) return
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault()
    scrollToSection(currentIndex + 1)
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault()
    scrollToSection(currentIndex - 1)
  }
}

onMounted(() => {
  const page = pageRef.value
  if (!page) return

  document.documentElement.style.overflow = 'hidden'
  document.body.style.overflow = 'hidden'

  page.addEventListener('wheel', onWheel, { passive: false })
  window.addEventListener('keydown', onKeyDown)

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target.querySelector('.section-animate')
          if (el) el.classList.add('animate-in')
        }
      })
    },
    { threshold: 0.05, root: page }
  )

  page.querySelectorAll('.snap-section').forEach((el) => observer.observe(el))
})

onUnmounted(() => {
  const page = pageRef.value
  page?.removeEventListener('wheel', onWheel)
  window.removeEventListener('keydown', onKeyDown)
  if (rafId) cancelAnimationFrame(rafId)
  observer?.disconnect()
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ── Scroll container — RAF-driven section transitions ── */
.home-page {
  height: 100vh;
  overflow-y: scroll;
  scroll-behavior: auto; /* Must be auto — native smooth scroll would fight the RAF loop */
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
}

.footer-snap {
  /* No scroll-snap-align needed — JS scrollToSection handles navigation */
}

/* Remove navbar's default bottom margin inside this container */
.home-page :deep(.navbar) {
  margin-bottom: 0;
}

/* ── Shared section base ── */
.snap-section {
  height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
}

/* Full-bleed background image helper */
.bg-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 18, 32, 0.55);
  z-index: 1;
}

.bg-overlay.dark {
  background: rgba(5, 10, 20, 0.75);
}

/* ── Section enter animation ── */
.section-animate {
  opacity: 0;
  transform: translateY(32px);
  transition:
    opacity 750ms cubic-bezier(0.22, 1, 0.36, 1),
    transform 750ms cubic-bezier(0.22, 1, 0.36, 1);
}

.section-animate.animate-in {
  opacity: 1;
  transform: translateY(0);
}

/* ── Shared eyebrow ── */
.eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #16a34a;
  margin-bottom: 20px;
}

.eyebrow.light {
  color: rgba(255, 255, 255, 0.45);
  margin-bottom: 48px;
}

/* ─────────────────────────────────────────
   §1  Hero
───────────────────────────────────────── */
.s-hero {
  background: #f6f0e6;
  flex-direction: row;
}

.s-hero-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 64px;
  position: relative;
  z-index: 1;
}

.s-hero-left h1 {
  font-size: 62px;
  font-weight: 800;
  line-height: 1.02;
  color: #0f172a;
  margin-bottom: 24px;
}

.hero-sub {
  font-size: 18px;
  color: #4b5563;
  line-height: 1.7;
  margin-bottom: 20px;
}

.hero-stat {
  font-size: 14px;
  color: #64748b;
  line-height: 1.65;
  border-left: 3px solid #16a34a;
  padding-left: 16px;
  margin-bottom: 36px;
  max-width: 420px;
}

.hero-stat strong {
  color: #0f172a;
  font-weight: 700;
}

.scroll-hint {
  font-size: 13px;
  color: #9ca3af;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.bounce {
  display: inline-block;
  animation: bounce 1.5s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(7px); }
}

.s-hero-right {
  flex: 1;
  position: relative;
}

.s-hero-right img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
}

/* ─────────────────────────────────────────
   §2  Sound Familiar? — dark overlay
───────────────────────────────────────── */
.s-familiar {
  align-items: center;
  justify-content: center;
}

.s-familiar-content {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 720px;
  padding: 0 48px;
  color: white;
}

.s-familiar-content h2 {
  font-size: 58px;
  font-weight: 800;
  line-height: 1.05;
  color: white;
  margin-bottom: 36px;
}

.questions {
  margin-bottom: 44px;
}

.questions p {
  font-size: 22px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.6;
  margin-bottom: 10px;
}

.familiar-stat {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.7;
}

.familiar-stat strong {
  color: #86efac;
  font-weight: 700;
}

/* ─────────────────────────────────────────
   §3  Hidden Cost
───────────────────────────────────────── */
.s-cost {
  align-items: center;
  justify-content: center;
}

.s-cost-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 0 48px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  max-width: 920px;
}

.stat-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px 32px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: border-color 200ms ease, background 200ms ease;
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.08);
}

.stat-num {
  font-size: 44px;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 14px;
  letter-spacing: -0.02em;
}

.stat-lbl {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.6;
}

/* ─────────────────────────────────────────
   §4  Bridge
───────────────────────────────────────── */
.s-bridge {
  background: #faf7f2;
  flex-direction: row;
}

.s-bridge-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 72px;
}

.s-bridge-left h2 {
  font-size: 52px;
  font-weight: 800;
  line-height: 1.08;
  color: #0f172a;
  margin-bottom: 28px;
}

.bridge-sub {
  font-size: 19px;
  color: #475569;
  line-height: 1.65;
  margin-bottom: 6px;
}

.bridge-em {
  font-size: 19px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.65;
  margin-bottom: 36px;
}

.bridge-hint {
  font-size: 15px;
  font-weight: 600;
  color: #16a34a;
  letter-spacing: 0.01em;
}

.s-bridge-right {
  flex: 1;
  position: relative;
}

.s-bridge-right img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
}

/* ─────────────────────────────────────────
   §5–7  Solution sections
───────────────────────────────────────── */
.s-solution {
  flex-direction: row;
  background: white;
}

.s-solution.reverse {
  flex-direction: row-reverse;
  background: #f0fdf4;
}

.sol-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 72px;
}

.sol-problem {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #94a3b8;
  margin-bottom: 16px;
}

.sol-text h2 {
  font-size: 46px;
  font-weight: 800;
  line-height: 1.1;
  color: #0f172a;
  margin-bottom: 20px;
}

.sol-desc {
  font-size: 17px;
  color: #475569;
  line-height: 1.75;
  margin-bottom: 36px;
  max-width: 460px;
}

.sol-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 12px;
  background: #16a34a;
  color: white;
  font-weight: 700;
  font-size: 15px;
  text-decoration: none;
  align-self: flex-start;
  transition:
    background 150ms ease,
    transform 150ms ease,
    box-shadow 150ms ease;
}

.sol-cta:hover {
  background: #15803d;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(22, 163, 74, 0.3);
}

.cta-arrow {
  transition: transform 200ms ease;
}

.sol-cta:hover .cta-arrow {
  transform: translateX(4px);
}

.sol-image {
  flex: 1;
  position: relative;
}

.sol-image img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ─────────────────────────────────────────
   Responsive
───────────────────────────────────────── */
@media (max-width: 900px) {
  .s-hero,
  .s-bridge,
  .s-solution,
  .s-solution.reverse {
    flex-direction: column;
  }

  .s-hero-left {
    flex: none;
    width: 100%;
    padding: 80px 28px 32px;
  }

  .s-hero-left h1 {
    font-size: 42px;
  }

  .s-hero-right {
    flex: 1;
    min-height: 260px;
  }

  .s-familiar-content h2 {
    font-size: 38px;
  }

  .questions p {
    font-size: 17px;
  }

  .stat-row {
    grid-template-columns: 1fr;
    gap: 16px;
    max-width: 380px;
    margin: 0 auto;
  }

  .stat-num {
    font-size: 36px;
  }

  .s-bridge-left {
    flex: none;
    width: 100%;
    padding: 80px 28px 32px;
  }

  .s-bridge-left h2 {
    font-size: 36px;
  }

  .s-bridge-right {
    flex: 1;
    min-height: 260px;
  }

  .sol-text {
    flex: none;
    width: 100%;
    padding: 80px 28px 32px;
  }

  .sol-text h2 {
    font-size: 32px;
  }

  .sol-image {
    flex: 1;
    min-height: 260px;
  }
}
</style>
