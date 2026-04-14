<template>
  <div class="search-box">
    <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <input
      v-model="inputValue"
      type="text"
      placeholder="Search for a brand or company..."
      @input="onInput"
      @keyup.enter="onEnter"
    />
    <button v-if="inputValue" class="clear-btn" @click="clear">✕</button>
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
  // Do NOT emit 'search' — only Search button / Enter key triggers a search
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
  border: 1px solid #dbe1e7;
  border-radius: 14px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #4ade80;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.15);
}

.clear-btn {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  font-size: 14px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.clear-btn:hover {
  color: #475569;
}
</style>
