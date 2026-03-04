<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import { useUiLanguage } from '../composables/useUiLanguage'

const auth = useAuthStore()
const progress = useProgressStore()
const router = useRouter()
const loading = ref(true)
const busyKey = ref('')
const sessionMode = ref(false)
const sessionIndex = ref(0)
const sessionResults = ref<Array<{ module_id: string; lesson_id: string; topic: string; success: boolean }>>([])
const sessionSummary = ref<{ processed: number; successes: number; bonus_xp: number; xp: number; level: number } | null>(null)
const { messages } = useUiLanguage()
const text = computed(() => messages.value.review)
const terms = computed(() => messages.value.terms)

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  await progress.loadReviewQueue()
  loading.value = false
})

const overdueItems = computed(() => progress.reviewsDue.filter(i => i.overdue))
const futureItems = computed(() => progress.reviewsDue.filter(i => !i.overdue))
const sessionItems = computed(() => overdueItems.value.slice(0, 5))
const currentSessionItem = computed(() => sessionItems.value[sessionIndex.value] || null)

async function mark(item: { module_id: string; lesson_id: string; topic: string }, success: boolean) {
  const key = `${item.module_id}/${item.lesson_id}/${item.topic}`
  busyKey.value = key
  await progress.completeReview(item.module_id, item.lesson_id, item.topic, success)
  busyKey.value = ''
}

function startSession() {
  sessionMode.value = true
  sessionIndex.value = 0
  sessionResults.value = []
  sessionSummary.value = null
}

function stopSession() {
  sessionMode.value = false
  sessionIndex.value = 0
  sessionResults.value = []
}

async function answerSession(success: boolean) {
  const item = currentSessionItem.value
  if (!item) return
  sessionResults.value.push({
    module_id: item.module_id,
    lesson_id: item.lesson_id,
    topic: item.topic,
    success,
  })
  if (sessionIndex.value >= sessionItems.value.length - 1) {
    const summary = await progress.completeReviewSession(sessionResults.value)
    if (summary) {
      sessionSummary.value = summary
    }
    sessionMode.value = false
    sessionIndex.value = 0
    sessionResults.value = []
    return
  }
  sessionIndex.value += 1
}

function openLesson(item: { module_id: string; lesson_id: string }) {
  router.push(`/lesson/${item.module_id}/${item.lesson_id}`)
}
</script>

<template>
  <div style="background: var(--bg-primary); min-height: 100vh; overflow-y: auto;">
    <div class="resources-page">
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <RouterLink to="/" class="btn btn-small">{{ messages.common.back }}</RouterLink>
        <h1>{{ text.title }}</h1>
      </div>
      <p class="subtitle">{{ text.subtitle }}</p>

      <div v-if="loading" style="color: var(--text-secondary);">{{ messages.status.loading }}</div>

      <template v-else>
        <div class="stats-section">
          <h3>{{ text.sprintTitle }}</h3>
          <div v-if="sessionMode && currentSessionItem" class="review-card">
            <div>
              <div class="resource-name">{{ currentSessionItem.topic }}</div>
              <div class="resource-desc">
                {{ text.card }} {{ sessionIndex + 1 }}/{{ sessionItems.length }} ·
                {{ currentSessionItem.module_id }} / {{ currentSessionItem.lesson_id }}
              </div>
            </div>
            <div style="display: flex; gap: .4rem; flex-wrap: wrap;">
              <button class="btn btn-small" @click="openLesson(currentSessionItem)">{{ text.openLesson }}</button>
              <button class="btn btn-small" @click="answerSession(true)">{{ text.know }}</button>
              <button class="btn btn-small" @click="answerSession(false)">{{ text.repeat }}</button>
              <button class="btn btn-small" @click="stopSession">{{ text.stop }}</button>
            </div>
          </div>
          <div v-else>
            <button class="btn btn-small" :disabled="sessionItems.length < 1" @click="startSession">
              {{ text.startSprint }}
            </button>
            <span style="margin-left: .5rem; color: var(--text-secondary); font-size: .82rem;">
              {{ text.sprintInfo }}
            </span>
          </div>
          <div v-if="sessionSummary" style="margin-top: .5rem; color: var(--text-secondary); font-size: .82rem;">
            {{ text.session }}: {{ sessionSummary.successes }}/{{ sessionSummary.processed }} · {{ text.bonusXp }}: +{{ sessionSummary.bonus_xp }} ·
            XP: {{ sessionSummary.xp }} · {{ terms.level }} {{ sessionSummary.level }}
          </div>
        </div>

        <div class="stats-section">
          <h3>{{ text.overdue }} ({{ overdueItems.length }})</h3>
          <div v-if="!overdueItems.length" style="color: var(--text-secondary); font-size: .85rem;">
            {{ text.overdueEmpty }}
          </div>
          <div v-for="item in overdueItems" :key="`${item.module_id}/${item.lesson_id}/${item.topic}`" class="review-card">
            <div>
              <div class="resource-name">{{ item.topic }}</div>
              <div class="resource-desc">{{ item.module_id }} / {{ item.lesson_id }}</div>
            </div>
            <div style="display: flex; gap: .4rem; flex-wrap: wrap;">
              <button class="btn btn-small" @click="openLesson(item)">{{ text.openLesson }}</button>
              <button
                class="btn btn-small"
                :disabled="busyKey === `${item.module_id}/${item.lesson_id}/${item.topic}`"
                @click="mark(item, true)"
              >
                {{ text.know }}
              </button>
              <button
                class="btn btn-small"
                :disabled="busyKey === `${item.module_id}/${item.lesson_id}/${item.topic}`"
                @click="mark(item, false)"
              >
                {{ text.repeat }}
              </button>
            </div>
          </div>
        </div>

        <div class="stats-section">
          <h3>{{ text.plannedLater }} ({{ futureItems.length }})</h3>
          <div v-if="!futureItems.length" style="color: var(--text-secondary); font-size: .85rem;">
            {{ text.plannedEmpty }}
          </div>
          <div v-for="item in futureItems" :key="`${item.module_id}/${item.lesson_id}/${item.topic}`" class="review-card muted">
            <div>
              <div class="resource-name">{{ item.topic }}</div>
              <div class="resource-desc">{{ item.module_id }} / {{ item.lesson_id }}</div>
            </div>
            <div class="resource-desc">{{ text.plannedAt }} {{ item.due_at ? new Date(item.due_at).toLocaleString('uk-UA') : '—' }}</div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
