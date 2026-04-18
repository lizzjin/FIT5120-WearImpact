<template>
  <div class="knowledge-page">
    <Navbar />

    <div class="page-container">
      <section
        class="knowledge-hero"
        v-motion
        :initial="{ opacity: 0, y: 24 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 600 } }"
      >
        <h1>Sustainable Fashion Knowledge Hub</h1>
        <p>
          Explore key sustainability topics related to clothing and learn how to
          make more responsible fashion choices.
        </p>
      </section>

      <section class="knowledge-section">
        <div
          class="section-heading"
          v-motion
          :initial="{ opacity: 0, y: 18 }"
          :enter="{ opacity: 1, y: 0, transition: { duration: 500, delay: 200 } }"
        >
          <h2>Explore Key Topics</h2>
          <p>
            Learn practical knowledge about sustainable fashion through simple
            and accessible topic-based content.
          </p>
        </div>

        <div class="content-layout">
          <div class="topics-panel">
            <h3>Topics</h3>

            <div class="topics-list">
              <button
                v-for="(topic, i) in knowledgeTopics"
                :key="topic.id"
                :class="['topic-button', { active: selectedTopic.id === topic.id }]"
                @click="selectTopic(topic)"
                v-motion
                :initial="{ opacity: 0, x: -16 }"
                :enter="{ opacity: 1, x: 0, transition: { duration: 400, delay: 100 + i * 80 } }"
              >
                <span class="topic-indicator" :class="{ active: selectedTopic.id === topic.id }"></span>
                {{ topic.title }}
              </button>
            </div>
          </div>

          <div class="topic-detail">
            <Transition name="content-fade" mode="out-in">
              <div :key="selectedTopic.id" class="topic-detail-inner">
                <h3>{{ selectedTopic.title }}</h3>
                <p>{{ selectedTopic.content }}</p>
              </div>
            </Transition>
          </div>
        </div>
      </section>

      <section
        class="knowledge-section alt-section"
        v-motion
        :initial="{ opacity: 0, y: 24 }"
        :visible-once="{ opacity: 1, y: 0, transition: { duration: 600 } }"
      >
        <div class="section-heading">
          <h2>Why This Matters</h2>
          <p>
            Small clothing choices can contribute to a more sustainable fashion future.
          </p>
        </div>

        <div class="info-block">
          <p>
            The knowledge hub is designed to help users better understand how fashion
            consumption affects the environment. By learning about waste reduction,
            recycling, second-hand shopping, and responsible clothing choices, users
            can take practical steps toward more sustainable everyday behaviour.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import { ref } from 'vue'
import { knowledgeTopics } from '../data/knowledgeTopics'

const selectedTopic = ref(knowledgeTopics[0])

function selectTopic(topic) {
  selectedTopic.value = topic
}
</script>

<style scoped>
.knowledge-page {
  background: var(--color-bg);
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

/* ── Hero ──────────────────────────────────────────────────────────────────── */
.knowledge-hero {
  background: linear-gradient(135deg, #edf5ef 0%, #dcfce7 100%);
  border-radius: 24px;
  padding: 48px 40px;
  margin-bottom: 28px;
  text-align: center;
}

.knowledge-hero h1 {
  font-size: 44px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.knowledge-hero p {
  font-size: 18px;
  color: var(--color-text-muted);
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto;
}

/* ── Section ──────────────────────────────────────────────────────────────── */
.knowledge-section {
  padding: 20px 0 36px;
}

.alt-section {
  background: #f3f4f6;
  padding: 48px 28px;
  border-radius: 24px;
}

.section-heading {
  text-align: center;
  margin-bottom: 28px;
}

.section-heading h2 {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 10px;
}

.section-heading p {
  font-size: 18px;
  color: var(--color-text-muted);
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Content layout ───────────────────────────────────────────────────────── */
.content-layout {
  display: grid;
  grid-template-columns: 0.85fr 1.4fr;
  gap: 24px;
}

/* ── Topics panel ─────────────────────────────────────────────────────────── */
.topics-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  padding: 24px;
  box-shadow: var(--shadow-card);
}

.topics-panel h3 {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 18px;
}

.topics-list {
  display: grid;
  gap: 10px;
}

.topic-button {
  width: 100%;
  text-align: left;
  padding: 16px 18px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 14px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  transition: all 250ms cubic-bezier(0.22, 1, 0.36, 1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.topic-indicator {
  width: 4px;
  height: 20px;
  border-radius: 4px;
  background: transparent;
  flex-shrink: 0;
  transition: background 250ms ease, height 250ms ease;
}

.topic-indicator.active {
  background: var(--color-primary);
  height: 24px;
}

.topic-button:hover {
  border-color: #bbf7d0;
  background: var(--color-primary-lighter);
  transform: translateX(4px);
}

.topic-button.active {
  background: var(--color-primary-lighter);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.08);
}

/* ── Topic detail ─────────────────────────────────────────────────────────── */
.topic-detail {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  padding: 32px;
  min-height: 360px;
  box-shadow: var(--shadow-card);
}

.topic-detail-inner h3 {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 16px;
}

.topic-detail-inner p {
  font-size: 17px;
  color: var(--color-text-muted);
  line-height: 1.8;
}

/* Content crossfade transition */
.content-fade-enter-active {
  transition: opacity 300ms ease, transform 300ms ease;
}
.content-fade-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}
.content-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.content-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Info block ───────────────────────────────────────────────────────────── */
.info-block {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  padding: 32px;
  box-shadow: var(--shadow-card);
  max-width: 1100px;
  margin: 0 auto;
}

.info-block p {
  font-size: 17px;
  color: var(--color-text-muted);
  line-height: 1.8;
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .knowledge-hero h1 {
    font-size: 32px;
  }

  .section-heading h2 {
    font-size: 28px;
  }

  .knowledge-hero p,
  .section-heading p,
  .topic-detail-inner p,
  .topic-button,
  .info-block p {
    font-size: 15px;
  }

  .topic-detail-inner h3 {
    font-size: 22px;
  }

  .topics-panel h3 {
    font-size: 20px;
  }

  .alt-section {
    padding: 32px 20px;
  }
}
</style>
