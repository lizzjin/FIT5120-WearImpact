<template>
  <div class="search-box" role="search">
    <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <input
      v-model="inputValue"
      type="text"
      placeholder="Search for a brand or company..."
      aria-label="Search clothing brands"
      @input="onInput"
      @keyup.enter="onEnter"
    />
    <button v-if="inputValue" class="clear-btn" @click="clear" aria-label="Clear search">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M18 6 6 18M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'search'])

const inputValue = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  inputValue.value = val
})

function onInput() {
  emit('update:modelValue', inputValue.value)
}

function onEnter() {
  emit('search', inputValue.value)
}

function clear() {
  inputValue.value = ''
  emit('update:modelValue', '')
}
</script>

<style scoped>
.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.search-box input {
  width: 100%;
  padding: 16px 44px;
  border: 1.5px solid #dbe1e7;
  border-radius: 14px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-box input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.12);
}

.clear-btn {
  position: absolute;
  right: 14px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  transition: background 150ms ease, color 150ms ease;
}

.clear-btn:hover {
  background: #e2e8f0;
  color: #475569;
}
</style>
