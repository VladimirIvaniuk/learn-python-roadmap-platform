<script setup lang="ts">
const model = defineModel<string | number>({ required: true })

const props = withDefaults(defineProps<{
  type?: string
  placeholder?: string
  min?: number
  step?: number
}>(), {
  type: 'text',
  placeholder: '',
})
</script>

<template>
  <input
    v-model="model"
    :type="props.type"
    :placeholder="props.placeholder"
    :min="props.min"
    :step="props.step"
    class="ui-input"
  />
</template>

<style scoped>
.ui-input {
  height: 2.25rem;
  width: 100%;
  border-radius: 0.4rem;
  border: 1px solid var(--border);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: 0 0.75rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s ease;
}
.ui-input:focus { border-color: var(--accent); }
</style>
