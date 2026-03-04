<script setup lang="ts">
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'

defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <TransitionRoot :show="open" as="template">
    <Dialog class="ui-modal-root" @close="emit('close')">
      <TransitionChild
        as="template"
        enter="transition-opacity duration-150"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="transition-opacity duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="ui-modal-backdrop" />
      </TransitionChild>

      <div class="ui-modal-wrap">
        <TransitionChild
          as="template"
          enter="transition duration-150"
          enter-from="opacity-0 scale-95"
          enter-to="opacity-100 scale-100"
          leave="transition duration-150"
          leave-from="opacity-100 scale-100"
          leave-to="opacity-0 scale-95"
        >
          <DialogPanel class="ui-modal-panel">
            <h3 v-if="title" class="ui-modal-title">{{ title }}</h3>
            <slot />
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<style scoped>
.ui-modal-root { position: relative; z-index: 50; }
.ui-modal-backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); }
.ui-modal-wrap { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.ui-modal-panel {
  width: 100%;
  max-width: 36rem;
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  padding: 1rem;
}
.ui-modal-title { margin-bottom: 0.5rem; font-size: 1rem; font-weight: 600; color: var(--text-primary); }
</style>
