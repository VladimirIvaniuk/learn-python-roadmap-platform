<script setup lang="ts">
import { computed } from 'vue'
import { useUiLanguage } from '../composables/useUiLanguage'
import UiModal from './ui/UiModal.vue'
import UiButton from './ui/UiButton.vue'

defineProps<{ hint: string; open: boolean }>()
const emit = defineEmits<{ close: [] }>()
const { messages } = useUiLanguage()
const text = computed(() => messages.value.hintModal)
</script>

<template>
  <UiModal :open="open" :title="text.title" @close="emit('close')">
    <p class="mb-3 text-sm text-text-primary">{{ hint }}</p>
    <UiButton size="sm" @click="emit('close')">{{ text.close }}</UiButton>
  </UiModal>
</template>
