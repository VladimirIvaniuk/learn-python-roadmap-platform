<script setup lang="ts">
import { computed } from 'vue'
import { useUiLanguage } from '../composables/useUiLanguage'
import UiButton from '../components/ui/UiButton.vue'
import UiCard from '../components/ui/UiCard.vue'

const { messages } = useUiLanguage()
const sections = computed(() => messages.value.resources.sections)
</script>

<template>
  <div class="lp-page overflow-y-auto">
    <div class="mx-auto w-full max-w-5xl px-4 py-5">
      <div class="mb-3 flex items-center gap-3">
        <RouterLink to="/">
          <UiButton size="sm">{{ messages.common.back }}</UiButton>
        </RouterLink>
        <h1 class="text-2xl font-semibold">{{ messages.resources.title }}</h1>
      </div>
      <p class="mb-5 text-sm text-text-secondary">
        {{ messages.resources.subtitleStart }}
        {{ messages.resources.subtitleFlow }}
      </p>

      <div class="space-y-6">
        <section v-for="section in sections" :key="section.title" class="space-y-2">
          <h2 class="text-lg font-semibold">{{ section.title }}</h2>
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <a
              v-for="r in section.resources"
              :key="r.url"
              :href="r.url"
              target="_blank"
              rel="noopener noreferrer"
              class="block transition hover:-translate-y-0.5"
            >
              <UiCard>
                <div class="flex items-start gap-2">
                  <span class="text-lg">{{ r.icon }}</span>
                  <div>
                    <div class="text-sm font-semibold text-text-primary">{{ r.name }}</div>
                    <div class="text-xs text-text-secondary">{{ r.desc }}</div>
                  </div>
                </div>
              </UiCard>
            </a>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
