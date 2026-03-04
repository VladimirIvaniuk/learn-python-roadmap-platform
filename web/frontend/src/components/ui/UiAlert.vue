<script setup lang="ts">
const props = withDefaults(defineProps<{
  variant?: 'error' | 'info' | 'success'
}>(), {
  variant: 'info',
})

const classes = {
  error: 'ui-alert--error',
  info: 'ui-alert--info',
  success: 'ui-alert--success',
}
</script>

<template>
  <div :class="['ui-alert', classes[props.variant]]">
    <slot />
  </div>
</template>

<style scoped>
.ui-alert {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}
.ui-alert--info { color: var(--text-secondary); background: var(--bg-secondary); }
.ui-alert--error { color: var(--error); background: color-mix(in srgb, var(--error) 10%, transparent); border-color: color-mix(in srgb, var(--error) 65%, var(--border)); }
.ui-alert--success { color: var(--success); background: color-mix(in srgb, var(--success) 10%, transparent); border-color: color-mix(in srgb, var(--success) 65%, var(--border)); }
</style>
