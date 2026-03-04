<script setup lang="ts">
const props = withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}>(), {
  variant: 'secondary',
  size: 'md',
  disabled: false,
  type: 'button',
})

const variantClasses = {
  primary: 'ui-btn--primary',
  secondary: 'ui-btn--secondary',
  ghost: 'ui-btn--ghost',
  danger: 'ui-btn--danger',
}

const sizeClasses = {
  sm: 'ui-btn--sm',
  md: 'ui-btn--md',
}
</script>

<template>
  <button
    :type="props.type"
    :disabled="props.disabled"
    :class="[
      'ui-btn',
      variantClasses[props.variant],
      sizeClasses[props.size],
    ]"
  >
    <slot />
  </button>
</template>

<style scoped>
.ui-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.4rem;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}
.ui-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.ui-btn--sm { height: 2rem; padding: 0 0.75rem; font-size: 0.75rem; }
.ui-btn--md { height: 2.25rem; padding: 0 0.875rem; font-size: 0.875rem; }
.ui-btn--primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.ui-btn--secondary { background: var(--bg-tertiary); color: var(--text-primary); border-color: var(--border); }
.ui-btn--ghost { background: transparent; color: var(--text-secondary); border-color: transparent; }
.ui-btn--ghost:hover { border-color: var(--border); color: var(--text-primary); }
.ui-btn--danger { background: var(--error); color: #fff; border-color: var(--error); }
</style>
