<template>
  <div class="search-bar">
    <div class="input-wrapper">
      <input
        v-model="inputValue"
        type="text"
        placeholder="Enter your suburb or city"
        @keyup.enter="handleSearch"
      />
      <button
        v-if="inputValue"
        class="clear-btn"
        @click="clearInput"
        type="button"
      >
        ×
      </button>
    </div>

    <button class="search-btn" @click="handleSearch">Search</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['search'])
const inputValue = ref('')

function handleSearch() {
  emit('search', inputValue.value)
}

function clearInput() {
  inputValue.value = ''
  emit('search', '')
}
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: 14px;
  margin: 24px 0;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 44px 14px 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 16px;
  outline: none;
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  font-size: 22px;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
}

.search-btn {
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 22px;
  font-weight: 600;
  cursor: pointer;
}
</style>