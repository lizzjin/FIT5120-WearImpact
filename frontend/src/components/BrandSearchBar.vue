<template>
  <div class="search-box">
    <input
      v-model="inputValue"
      type="text"
      placeholder="Search for a brand..."
      @input="emitSearch"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

const inputValue = ref(props.modelValue)

watch(
  () => props.modelValue,
  (newValue) => {
    inputValue.value = newValue
  }
)

function emitSearch() {
  emit('update:modelValue', inputValue.value)
  emit('search', inputValue.value)
}
</script>

<style scoped>
.search-box input {
  width: 100%;
  padding: 16px 18px;
  border: 1px solid #dbe1e7;
  border-radius: 14px;
  font-size: 17px;
  outline: none;
}
</style>