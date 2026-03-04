<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import { useUiLanguage } from '../composables/useUiLanguage'

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
  <div style="background: var(--bg-primary); min-height: 100vh; overflow-y: auto;">
    <div class="resources-page">
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <RouterLink to="/" class="btn btn-small">{{ messages.common.back }}</RouterLink>
        <h1>{{ text.title }}</h1>
      </div>
      <p class="subtitle">{{ text.subtitle }}</p>

      <div v-if="loading" style="color: var(--text-secondary);">{{ messages.status.loading }}</div>
      <div v-else-if="error && !progress.weeklyPlan" class="inline-error-row">
        <span>{{ error }} {{ messages.status.genericRetryHint }}</span>
        <button class="btn btn-small" @click="retryLoad">{{ messages.common.retry }}</button>
      </div>
      <template v-else-if="progress.weeklyPlan">
        <div v-if="error" class="inline-error-row" style="margin-bottom:.55rem;">
          <span>{{ error }}</span>
        </div>
        <div style="margin-bottom: .8rem; color: var(--text-secondary); font-size: .85rem;">
          {{ text.mode }} <strong>{{ messages.common.goalPresets[progress.weeklyPlan.preset as 'easy' | 'balanced' | 'intensive' | 'weekend'] || progress.weeklyPlan.preset }}</strong> · {{ text.generatedAt }}
          {{ new Date(progress.weeklyPlan.generated_at).toLocaleString('uk-UA') }}
        </div>
        <div style="margin-bottom: .8rem;">
          <button class="btn btn-small" :disabled="!actionHistory.length || !!busyKey" @click="undoLastAction">{{ text.undo }}</button>
          <button
            class="btn btn-small"
            style="margin-left:.35rem;"
            :disabled="!actionHistory.length || !!busyKey"
            @click="clearHistory"
          >
            {{ text.clearHistory }}
          </button>
          <span v-if="actionHistory.length" style="margin-left:.45rem; color: var(--text-secondary); font-size:.8rem;">
            {{ actionHistory.length }} {{ text.actionsInStack }}
          </span>
          <div v-if="actionHistory.length" style="margin-top:.35rem; color: var(--text-secondary); font-size:.78rem;">
            <div v-for="(a, idx) in actionHistory" :key="`${a.planDate}/${a.taskKey}/${idx}`">
              {{ idx + 1 }}. {{ actionLabel(a.action) }} · {{ a.taskKey }}
            </div>
          </div>
        </div>

        <div v-for="day in progress.weeklyPlan.days" :key="day.day_index" class="review-card" style="align-items:flex-start;">
          <div style="flex:1;">
            <div class="resource-name">
              {{ text.day }} {{ day.day_index }} · {{ new Date(day.date).toLocaleDateString('uk-UA') }}
            </div>
            <div class="resource-desc">
              {{ day.focus }} · ~{{ day.estimated_minutes }} {{ messages.common.minuteAbbr }}
              <span v-if="day.progress"> · {{ day.progress.done }}/{{ day.progress.total }} {{ text.completed }}</span>
            </div>
            <div style="margin-top:.45rem;">
              <div
                v-for="(task, i) in day.tasks"
                :key="i"
                class="review-card"
                style="padding:.45rem .55rem; margin-bottom:.35rem;"
              >
                <div style="flex:1;">
                  <div style="font-size:.82rem;">{{ taskStatus(task as Record<string, unknown>) }} {{ taskText(task as Record<string, unknown>) }}</div>
                  <div
                    v-if="(task as Record<string, unknown>).carryover"
                    class="resource-desc"
                  >
                    {{ text.rescheduledFrom }} {{ (task as Record<string, unknown>).rescheduled_from }}
                  </div>
                </div>
                <div style="display:flex; gap:.25rem; flex-wrap: wrap;">
                  <button
                    class="btn btn-small"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/done`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'done')"
                  >✅</button>
                  <button
                    class="btn btn-small"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/skip`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'skip')"
                  >⏭️</button>
                  <button
                    class="btn btn-small"
                    :disabled="busyKey === `${day.date}/${String((task as Record<string, unknown>).task_key || '')}/snooze`"
                    @click="doAction(day.date, task as Record<string, unknown>, 'snooze')"
                  >🕒</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <div v-else style="color: var(--text-secondary);">{{ text.unavailable }}</div>
    </div>
  </div>
</template>
