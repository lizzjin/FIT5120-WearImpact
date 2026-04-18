<template>
  <div class="home-page" ref="pageRef">
    <Navbar />

    <!-- §1 Hero — split: warm cream left / editorial image right -->
    <section class="snap-section s-hero">
      <div class="s-hero-left section-animate">
        <p class="eyebrow">FOR SUSTAINABLE FASHION IN AUSTRALIA</p>
        <h1
          v-motion
          :initial="{ opacity: 0, y: 40 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 700, delay: 100 } }"
        >
          Look good.<br />Feel good.<br />Choose better.
        </h1>
        <p
          class="hero-sub"
          v-motion
          :initial="{ opacity: 0, y: 24 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 600, delay: 300 } }"
        >
          Fast fashion gives instant joy.<br />
          But its impact lasts far longer than trends.
        </p>
        <p
          class="hero-stat"
          v-motion
          :initial="{ opacity: 0, x: -20 }"
          :visible-once="{ opacity: 1, x: 0, transition: { duration: 600, delay: 500 } }"
        >
          Every year, Australians throw away <strong>220,000 tonnes</strong> of clothing.
          Most of it was bought with good intentions.
        </p>
        <span
          class="scroll-hint"
          v-motion
          :initial="{ opacity: 0 }"
          :visible-once="{ opacity: 1, transition: { duration: 500, delay: 800 } }"
        >
          Scroll to explore <span class="bounce">&#8595;</span>
        </span>
      </div>
      <div class="s-hero-right">
        <img
          src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80"
          alt="Minimal fashion store"
        />
      </div>
    </section>

    <!-- §2 Sound Familiar? — full-bleed dark overlay -->
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
          <p
            v-for="(q, i) in familiarQuestions"
            :key="i"
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 200 + i * 180 } }"
          >
            {{ q }}
          </p>
        </div>
        <p
          class="familiar-stat"
          v-motion
          :initial="{ opacity: 0, y: 16 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 600, delay: 800 } }"
        >
          You're not alone &mdash;
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
          <div
            v-for="(stat, i) in impactStats"
            :key="stat.number"
            class="stat-card"
            v-motion
            :initial="{ opacity: 0, y: 30, scale: 0.95 }"
            :visible-once="{ opacity: 1, y: 0, scale: 1, transition: { duration: 500, delay: 150 + i * 180 } }"
          >
            <p class="stat-num">{{ stat.number }}</p>
            <p class="stat-lbl">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- §4 Bridge — transition from problem to solution -->
    <section class="snap-section s-bridge">
      <div class="s-bridge-left section-animate">
        <h2
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 600, delay: 100 } }"
        >
          Sustainable choices<br />shouldn't feel hard.
        </h2>
        <p
          class="bridge-sub"
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 300 } }"
        >
          You don't need to stop loving fashion.
        </p>
        <p
          class="bridge-em"
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 450 } }"
        >
          You just need better information.
        </p>
        <p
          class="bridge-hint"
          v-motion
          :initial="{ opacity: 0 }"
          :visible-once="{ opacity: 1, transition: { duration: 500, delay: 650 } }"
        >
          Here's how WearImpact helps &#8595;
        </p>
      </div>
      <div class="s-bridge-right">
        <img
          src="https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1200&q=80"
          alt="Sustainable fashion choices"
        />
      </div>
    </section>

    <!-- §5–7 Solution sections -->
    <section
      v-for="(sol, i) in solutions"
      :key="sol.id"
      class="snap-section s-solution"
      :class="{ reverse: i % 2 === 1 }"
    >
      <div class="sol-text section-animate">
        <p
          class="sol-problem"
          v-motion
          :initial="{ opacity: 0, y: 16 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 100 } }"
        >
          {{ sol.problem }}
        </p>
        <h2
          v-motion
          :initial="{ opacity: 0, y: 24 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 600, delay: 250 } }"
        >
          {{ sol.title }}
        </h2>
        <p
          class="sol-desc"
          v-motion
          :initial="{ opacity: 0, y: 18 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 400 } }"
        >
          {{ sol.description }}
        </p>
        <router-link
          :to="sol.link"
          class="sol-cta"
          v-motion
          :initial="{ opacity: 0, y: 12 }"
          :visible-once="{ opacity: 1, y: 0, transition: { duration: 500, delay: 550 } }"
        >
          {{ sol.cta }}
          <ArrowRight :size="17" :stroke-width="2.5" class="cta-arrow" />
        </router-link>
      </div>
      <div class="sol-image">
        <img :src="sol.image" :alt="sol.title" />
      </div>
    </section>

    <!-- Footer -->
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
let isAnimating = false
let rafId = null
let scrollLocked = false
let accumulatedDelta = 0
const LOCK_DURATION = 700
const DELTA_THRESHOLD = 30
let observer = null

const familiarQuestions = [
  '"Bought something because it was on sale?"',
  '"Worn an outfit once, then forgot about it?"',
  '"Have clothes in your wardrobe you never touch?"',
]

const impactStats = [
  {
    number: '220,000 t',
    label: 'of clothing sent to landfill every year in Australia'
  },
  {
    number: '14.5M t',
    label: 'of CO\u2082 from fashion-related carbon emissions'
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

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
}

function scrollToSection(index) {
  const page = pageRef.value
  const sections = getSections()
  if (index < 0 || index >= sections.length || !page) return

  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }

  currentIndex = index
  isAnimating = true

  const startTop = page.scrollTop
  const targetTop = sections[index].offsetTop
  const distance = targetTop - startTop
  const duration = 600
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

function onWheel(e) {
  e.preventDefault()
  if (scrollLocked) return

  accumulatedDelta += e.deltaY
  if (Math.abs(accumulatedDelta) < DELTA_THRESHOLD) return

  const direction = accumulatedDelta > 0 ? 1 : -1
  accumulatedDelta = 0
  scrollLocked = true

  scrollToSection(currentIndex + direction)

  setTimeout(() => {
    accumulatedDelta = 0
    scrollLocked = false
  }, LOCK_DURATION)
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
/* ── Scroll container ── */
.home-page {
  height: 100vh;
  overflow-y: scroll;
  scroll-behavior: auto;
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
}

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
  color: var(--color-primary);
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
  background: var(--color-warm-cream);
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
  color: var(--color-text);
  margin-bottom: 24px;
}

.hero-sub {
  font-size: 18px;
  color: var(--color-text-muted);
  line-height: 1.7;
  margin-bottom: 20px;
}

.hero-stat {
  font-size: 14px;
  color: var(--color-text-subtle);
  line-height: 1.65;
  border-left: 3px solid var(--color-primary);
  padding-left: 16px;
  margin-bottom: 36px;
  max-width: 420px;
}

.hero-stat strong {
  color: var(--color-text);
  font-weight: 700;
}

.scroll-hint {
  font-size: 13px;
  color: var(--color-text-faint);
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
  overflow: hidden;
}

.s-hero-right img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
  transition: transform 8s ease;
}

.s-hero-right:hover img {
  transform: scale(1.03);
}

/* ─────────────────────────────────────────
   §2  Sound Familiar?
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
  border-radius: var(--radius-card);
  padding: 40px 32px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: border-color 300ms ease, background 300ms ease, transform 300ms ease;
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
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
  background: var(--color-warm-alt);
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
  color: var(--color-text);
  margin-bottom: 28px;
}

.bridge-sub {
  font-size: 19px;
  color: var(--color-text-muted);
  line-height: 1.65;
  margin-bottom: 6px;
}

.bridge-em {
  font-size: 19px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.65;
  margin-bottom: 36px;
}

.bridge-hint {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 0.01em;
}

.s-bridge-right {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.s-bridge-right img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
  transition: transform 8s ease;
}

.s-bridge-right:hover img {
  transform: scale(1.03);
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
  background: var(--color-primary-lighter);
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
  color: var(--color-text-faint);
  margin-bottom: 16px;
}

.sol-text h2 {
  font-size: 46px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--color-text);
  margin-bottom: 20px;
}

.sol-desc {
  font-size: 17px;
  color: var(--color-text-muted);
  line-height: 1.75;
  margin-bottom: 36px;
  max-width: 460px;
}

.sol-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: var(--radius-btn);
  background: var(--color-primary);
  color: white;
  font-weight: 700;
  font-size: 15px;
  text-decoration: none;
  align-self: flex-start;
  transition:
    background var(--transition-base),
    transform var(--transition-base),
    box-shadow var(--transition-base);
}

.sol-cta:hover {
  background: var(--color-primary-dark);
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
  overflow: hidden;
}

.sol-image img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 6s ease;
}

.s-solution:hover .sol-image img {
  transform: scale(1.04);
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
