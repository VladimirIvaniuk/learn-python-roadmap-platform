<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import { useUiLanguage } from '../composables/useUiLanguage'
import UiButton from '../components/ui/UiButton.vue'
import UiCard from '../components/ui/UiCard.vue'
import UiAlert from '../components/ui/UiAlert.vue'

const auth = useAuthStore()
const progress = useProgressStore()
const router = useRouter()
const loading = ref(true)
const busyKey = ref('')
const error = ref('')
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
  const ok = await progress.loadReviewQueue()
  if (!ok) error.value = text.value.loadFailed
  loading.value = false
})

async function retryLoad() {
  loading.value = true
  error.value = ''
  const ok = await progress.loadReviewQueue()
  if (!ok) error.value = text.value.loadFailed
  loading.value = false
}

const overdueItems = computed(() => progress.reviewsDue.filter(i => i.overdue))
const futureItems = computed(() => progress.reviewsDue.filter(i => !i.overdue))
const sessionItems = computed(() => overdueItems.value.slice(0, 5))
const currentSessionItem = computed(() => sessionItems.value[sessionIndex.value] || null)

async function mark(item: { module_id: string; lesson_id: string; topic: string }, success: boolean) {
  const key = `${item.module_id}/${item.lesson_id}/${item.topic}`
  busyKey.value = key
  error.value = ''
  const ok = await progress.completeReview(item.module_id, item.lesson_id, item.topic, success)
  if (!ok) error.value = text.value.actionFailed
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
    } else {
      error.value = text.value.actionFailed
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
  <div class="lp-page overflow-y-auto">
    <div class="mx-auto w-full max-w-5xl px-4 py-5">
      <div class="mb-3 flex items-center gap-3">
        <RouterLink to="/">
          <UiButton size="sm">{{ messages.common.back }}</UiButton>
        </RouterLink>
        <h1 class="text-2xl font-semibold">{{ text.title }}</h1>
      </div>
      <p class="mb-5 text-sm text-text-secondary">{{ text.subtitle }}</p>

      <div v-if="loading" class="py-10 text-sm text-text-secondary">{{ messages.status.loading }}</div>
      <UiAlert v-else-if="error" variant="error">
        <span>{{ error }} {{ messages.status.genericRetryHint }}</span>
        <UiButton size="sm" @click="retryLoad">{{ messages.common.retry }}</UiButton>
      </UiAlert>

      <template v-else>
        <UiCard class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.sprintTitle }}</h3>
          <div v-if="sessionMode && currentSessionItem" class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div class="text-sm font-semibold">{{ currentSessionItem.topic }}</div>
              <div class="text-xs text-text-secondary">
                {{ text.card }} {{ sessionIndex + 1 }}/{{ sessionItems.length }} ·
                {{ currentSessionItem.module_id }} / {{ currentSessionItem.lesson_id }}
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <UiButton size="sm" @click="openLesson(currentSessionItem)">{{ text.openLesson }}</UiButton>
              <UiButton size="sm" @click="answerSession(true)">{{ text.know }}</UiButton>
              <UiButton size="sm" @click="answerSession(false)">{{ text.repeat }}</UiButton>
              <UiButton size="sm" variant="ghost" @click="stopSession">{{ text.stop }}</UiButton>
            </div>
          </div>
          <div v-else class="flex items-center gap-2">
            <UiButton size="sm" :disabled="sessionItems.length < 1" @click="startSession">
              {{ text.startSprint }}
            </UiButton>
            <span class="text-xs text-text-secondary">
              {{ text.sprintInfo }}
            </span>
          </div>
          <div v-if="sessionSummary" class="mt-2 text-xs text-text-secondary">
            {{ text.session }}: {{ sessionSummary.successes }}/{{ sessionSummary.processed }} · {{ text.bonusXp }}: +{{ sessionSummary.bonus_xp }} ·
            XP: {{ sessionSummary.xp }} · {{ terms.level }} {{ sessionSummary.level }}
          </div>
        </UiCard>

        <UiCard class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.overdue }} ({{ overdueItems.length }})</h3>
          <div v-if="!overdueItems.length" class="text-sm text-text-secondary">
            {{ text.overdueEmpty }}
          </div>
          <div v-for="item in overdueItems" :key="`${item.module_id}/${item.lesson_id}/${item.topic}`" class="mb-2 flex flex-col gap-2 rounded-lg border border-border p-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div class="text-sm font-semibold">{{ item.topic }}</div>
              <div class="text-xs text-text-secondary">{{ item.module_id }} / {{ item.lesson_id }}</div>
            </div>
            <div class="flex flex-wrap gap-2">
              <UiButton size="sm" @click="openLesson(item)">{{ text.openLesson }}</UiButton>
              <UiButton
                size="sm"
                :disabled="busyKey === `${item.module_id}/${item.lesson_id}/${item.topic}`"
                @click="mark(item, true)"
              >
                {{ text.know }}
              </UiButton>
              <UiButton
                size="sm"
                :disabled="busyKey === `${item.module_id}/${item.lesson_id}/${item.topic}`"
                @click="mark(item, false)"
              >
                {{ text.repeat }}
              </UiButton>
            </div>
          </div>
        </UiCard>

        <UiCard>
          <h3 class="mb-3 text-base font-semibold">{{ text.plannedLater }} ({{ futureItems.length }})</h3>
          <div v-if="!futureItems.length" class="text-sm text-text-secondary">
            {{ text.plannedEmpty }}
          </div>
          <div v-for="item in futureItems" :key="`${item.module_id}/${item.lesson_id}/${item.topic}`" class="mb-2 flex flex-col gap-1 rounded-lg border border-border/70 bg-bg-tertiary/60 p-3">
            <div>
              <div class="text-sm font-semibold">{{ item.topic }}</div>
              <div class="text-xs text-text-secondary">{{ item.module_id }} / {{ item.lesson_id }}</div>
            </div>
            <div class="text-xs text-text-secondary">{{ text.plannedAt }} {{ item.due_at ? new Date(item.due_at).toLocaleString('uk-UA') : '—' }}</div>
          </div>
        </UiCard>
      </template>
    </div>
  </div>
</template>
