<template>
  <div class="knowledge-page">
    <Navbar />

    <div class="page-container">
      <section class="knowledge-hero">
        <h1>Sustainable Fashion Knowledge Hub</h1>
        <p>
          Explore key sustainability topics related to clothing and learn how to
          make more responsible fashion choices.
        </p>
      </section>

      <section class="knowledge-section">
        <div class="section-heading">
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
                v-for="topic in knowledgeTopics"
                :key="topic.id"
                :class="['topic-button', { active: selectedTopic.id === topic.id }]"
                @click="selectTopic(topic)"
              >
                {{ topic.title }}
              </button>
            </div>
          </div>

          <div class="topic-detail">
            <h3>{{ selectedTopic.title }}</h3>
            <p>{{ selectedTopic.content }}</p>
          </div>
        </div>
      </section>

      <section class="knowledge-section alt-section">
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
  background: #f8faf8;
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

.knowledge-hero {
  background: #edf5ef;
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 24px;
  text-align: center;
}

.knowledge-hero h1 {
  font-size: 48px;
  color: #0f172a;
  margin-bottom: 12px;
}

.knowledge-hero p {
  font-size: 18px;
  color: #475569;
  line-height: 1.6;
  max-width: 760px;
  margin: 0 auto;
}

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
  font-size: 48px;
  color: #0f172a;
  margin-bottom: 10px;
}

.section-heading p {
  font-size: 20px;
  color: #475569;
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.6;
}

.content-layout {
  display: grid;
  grid-template-columns: 0.85fr 1.4fr;
  gap: 24px;
}

.topics-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.topics-panel h3 {
  font-size: 28px;
  color: #0f172a;
  margin-bottom: 18px;
}

.topics-list {
  display: grid;
  gap: 14px;
}

.topic-button {
  width: 100%;
  text-align: left;
  padding: 18px 20px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 18px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  transition: all 0.2s ease;
}

.topic-button.active {
  background: #edf5ef;
  border-color: #16a34a;
}

.topic-detail {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 32px;
  min-height: 360px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.topic-detail h3 {
  font-size: 32px;
  color: #0f172a;
  margin-bottom: 16px;
}

.topic-detail p {
  font-size: 18px;
  color: #475569;
  line-height: 1.8;
}

.info-block {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
  max-width: 1100px;
  margin: 0 auto;
}

.info-block p {
  font-size: 18px;
  color: #475569;
  line-height: 1.8;
}

@media (max-width: 900px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .knowledge-hero h1,
  .section-heading h2 {
    font-size: 34px;
  }

  .knowledge-hero p,
  .section-heading p,
  .topic-detail p,
  .topic-button,
  .info-block p {
    font-size: 16px;
  }

  .topic-detail h3,
  .topics-panel h3 {
    font-size: 24px;
  }

  .alt-section {
    padding: 32px 20px;
  }
}
</style>