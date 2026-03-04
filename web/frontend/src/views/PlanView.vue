<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
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
type PlanAction = { planDate: string; taskKey: string; action: 'done' | 'skip' | 'snooze' }
const actionHistory = ref<PlanAction[]>([])
const HISTORY_STORAGE_KEY = 'learn_python_plan_undo_history'
const { messages } = useUiLanguage()
const text = computed(() => messages.value.plan)

function actionLabel(action: PlanAction['action']) {
  if (action === 'done') return text.value.actionDone
  if (action === 'skip') return text.value.actionSkip
  return text.value.actionSnooze
}

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  const ok = await progress.loadWeeklyPlan()
  if (!ok) error.value = text.value.loadFailed
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        actionHistory.value = parsed.slice(0, 5)
      }
    }
  } catch {
    actionHistory.value = []
  }
  loading.value = false
})

async function retryLoad() {
  loading.value = true
  error.value = ''
  const ok = await progress.loadWeeklyPlan()
  if (!ok) error.value = text.value.loadFailed
  loading.value = false
}

watch(
  actionHistory,
  (history) => {
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history.slice(0, 5)))
  },
  { deep: true }
)

function taskText(task: Record<string, unknown>) {
  const t = String(task.type || '')
  if (t === 'lesson') return `📘 ${task.title || task.lesson_id} (${task.why || text.value.nextStep})`
  if (t === 'review') return `🔁 ${text.value.reviewPrefix}: ${task.topic} (${task.lesson_id})`
  if (t === 'practice') return `🧩 ${text.value.practicePrefix}: ${task.topic}`
  return JSON.stringify(task)
}

function taskStatus(task: Record<string, unknown>) {
  const status = String(task.status || 'pending')
  if (status === 'done') return '✅'
  if (status === 'skip') return '⏭️'
  if (status === 'snooze') return '🕒'
  return '•'
}

async function doAction(dayDate: string, task: Record<string, unknown>, action: 'done' | 'skip' | 'snooze') {
  const taskKey = String(task.task_key || '')
  if (!taskKey) return
  busyKey.value = `${dayDate}/${taskKey}/${action}`
  error.value = ''
  const ok = await progress.planTaskAction(dayDate, taskKey, action)
  if (ok) {
    actionHistory.value.unshift({ planDate: dayDate, taskKey, action })
    actionHistory.value = actionHistory.value.slice(0, 5)
  } else {
    error.value = text.value.actionFailed
  }
  busyKey.value = ''
}

async function undoLastAction() {
  const lastAction = actionHistory.value[0]
  if (!lastAction) return
  const { planDate, taskKey } = lastAction
  busyKey.value = `${planDate}/${taskKey}/pending`
  error.value = ''
  const ok = await progress.planTaskAction(planDate, taskKey, 'pending')
  if (ok) actionHistory.value.shift()
  if (!ok) error.value = text.value.actionFailed
  busyKey.value = ''
}

function clearHistory() {
  actionHistory.value = []
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
      <UiAlert v-else-if="error && !progress.weeklyPlan" variant="error">
        <span>{{ error }} {{ messages.status.genericRetryHint }}</span>
        <UiButton size="sm" @click="retryLoad">{{ messages.common.retry }}</UiButton>
      </UiAlert>
      <template v-else-if="progress.weeklyPlan">
        <UiAlert v-if="error" class="mb-2" variant="error">
          <span>{{ error }}</span>
        </UiAlert>
        <div class="mb-3 text-sm text-text-secondary">
          {{ text.mode }} <strong>{{ messages.common.goalPresets[progress.weeklyPlan.preset as 'easy' | 'balanced' | 'intensive' | 'weekend'] || progress.weeklyPlan.preset }}</strong> · {{ text.generatedAt }}
          {{ new Date(progress.weeklyPlan.generated_at).toLocaleString('uk-UA') }}
        </div>
        <div class="mb-3">
          <UiButton size="sm" :disabled="!actionHistory.length || !!busyKey" @click="undoLastAction">{{ text.undo }}</UiButton>
          <UiButton
            class="ml-2"
            size="sm"
            :disabled="!actionHistory.length || !!busyKey"
            @click="clearHistory"
          >
            {{ text.clearHistory }}
          </UiButton>
          <span v-if="actionHistory.length" class="ml-2 text-xs text-text-secondary">
            {{ actionHistory.length }} {{ text.actionsInStack }}
          </span>
          <div v-if="actionHistory.length" class="mt-2 space-y-1 text-xs text-text-secondary">
            <div v-for="(a, idx) in actionHistory" :key="`${a.planDate}/${a.taskKey}/${idx}`">
              {{ idx + 1 }}. {{ actionLabel(a.action) }} · {{ a.taskKey }}
            </div>
          </div>
        </div>

        <UiCard v-for="day in progress.weeklyPlan.days" :key="day.day_index" class="mb-3">
          <div>
            <div class="text-sm font-semibold">
              {{ text.day }} {{ day.day_index }} · {{ new Date(day.date).toLocaleDateString('uk-UA') }}
            </div>
            <div class="text-xs text-text-secondary">
              {{ day.focus }} · ~{{ day.estimated_minutes }} {{ messages.common.minuteAbbr }}
              <span v-if="day.progress"> · {{ day.progress.done }}/{{ day.progress.total }} {{ text.completed }}</span>
            </div>
            <div class="mt-2 space-y-2">
              <div
                v-for="(task, i) in day.tasks"
                :key="i"
                class="flex flex-col gap-2 rounded-lg border border-border p-2 md:flex-row md:items-center md:justify-between"
              >
                <div class="flex-1">
                  <div class="text-sm">{{ taskStatus(task as Record<string, unknown>) }} {{ taskText(task as Record<string, unknown>) }}</div>
                  <div
                    v-if="(task as Record<string, unknown>).carryover"
                    class="text-xs text-text-secondary"
                  >
                    {{ text.rescheduledFrom }} {{ (task as Record<string, unknown>).rescheduled_from }}
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <UiButton
                    size="sm"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/done`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'done')"
                  >✅</UiButton>
                  <UiButton
                    size="sm"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/skip`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'skip')"
                  >⏭️</UiButton>
                  <UiButton
                    size="sm"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/snooze`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'snooze')"
                  >🕒</UiButton>
                </div>
              </div>
            </div>
          </div>
        </UiCard>
      </template>
      <div v-else class="text-sm text-text-secondary">{{ text.unavailable }}</div>
    </div>
  </div>
</template>
