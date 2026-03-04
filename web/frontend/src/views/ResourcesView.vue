<script setup lang="ts">
import { computed } from 'vue'
import { useUiLanguage } from '../composables/useUiLanguage'

const { messages } = useUiLanguage()
const sections = computed(() => messages.value.resources.sections)
</script>

<template>
  <div style="background: var(--bg-primary); height: 100vh; overflow-y: auto;">
    <div class="resources-page">
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <RouterLink to="/" class="btn btn-small">{{ messages.common.back }}</RouterLink>
        <h1>{{ messages.resources.title }}</h1>
      </div>
      <p class="subtitle">
        {{ messages.resources.subtitleStart }}
        {{ messages.resources.subtitleFlow }}
      </p>

      <div v-for="section in sections" :key="section.title" class="resource-section">
        <h2>{{ section.title }}</h2>
        <a
          v-for="r in section.resources"
          :key="r.url"
          :href="r.url"
          target="_blank"
          rel="noopener noreferrer"
          class="resource-card"
        >
          <span class="resource-icon">{{ r.icon }}</span>
          <div>
            <div class="resource-name">{{ r.name }}</div>
            <div class="resource-desc">{{ r.desc }}</div>
          </div>
        </a>
      </div>
    </div>
  </div>
</template>
