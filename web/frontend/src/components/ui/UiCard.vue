<template>
  <section class="ui-card">
    <slot />
  </section>
</template>

<style scoped>
.ui-card {
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  padding: 0.875rem;
}
</style>
