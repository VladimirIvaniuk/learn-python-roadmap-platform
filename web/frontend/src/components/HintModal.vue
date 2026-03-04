<script setup lang="ts">
import { computed } from 'vue'
import { useUiLanguage } from '../composables/useUiLanguage'

defineProps<{ hint: string; open: boolean }>()
const emit = defineEmits<{ close: [] }>()
const { messages } = useUiLanguage()
const text = computed(() => messages.value.hintModal)
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal" @click.self="emit('close')">
      <div class="modal-content">
        <h4>{{ text.title }}</h4>
        <p>{{ hint }}</p>
        <button class="btn" @click="emit('close')">{{ text.close }}</button>
      </div>
    </div>
  </Teleport>
</template>
