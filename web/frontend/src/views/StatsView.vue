<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUiLanguage } from '../composables/useUiLanguage'
import UiButton from '../components/ui/UiButton.vue'
import UiCard from '../components/ui/UiCard.vue'
import UiAlert from '../components/ui/UiAlert.vue'

interface StatsData {
  total_completed: number
  total_lessons: number
  total_time_seconds: number
  by_level: Record<string, { done: number; total: number }>
  daily_activity: Record<string, number>
  lesson_times: Array<{ module_id: string; lesson_id: string; time_spent: number; completed_at: string }>
}

interface AdaptiveSummary {
  weak_topics: Array<{ topic: string; count: number }>
  reviews_due_count: number
  gamification: { xp: number; level: number; badges: string[] }
  skill_map: Record<string, { done: number; total: number; percent: number }>
  skill_lesson_matrix: Record<string, Array<{ module_id: string; lesson_id: string; title: string; done: boolean }>>
  quests?: {
    daily: Array<{ id: string; title: string; target: number; progress: number; done: boolean }>
    weekly: Array<{ id: string; title: string; target: number; progress: number; done: boolean }>
  }
  next_lessons?: Array<{ module_id: string; lesson_id: string; title?: string; reason?: string; score?: number }>
}

const router = useRouter()
const auth = useAuthStore()
const stats = ref<StatsData | null>(null)
const adaptive = ref<AdaptiveSummary | null>(null)
const loading = ref(true)
const error = ref('')
const { messages } = useUiLanguage()
const ui = computed(() => messages.value.terms)
const text = computed(() => messages.value.stats)

async function loadStatsData() {
  loading.value = true
  error.value = ''
  stats.value = null
  adaptive.value = null
  try {
    const res = await fetch('/api/stats', { headers: auth.authHeaders() })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    stats.value = await res.json()
    const adaptiveRes = await fetch('/api/adaptive/summary', { headers: auth.authHeaders() })
    if (adaptiveRes.ok) adaptive.value = await adaptiveRes.json()
  } catch {
    error.value = text.value.loadFailed
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  await loadStatsData()
})

const totalPercent = computed(() => {
  if (!stats.value) return 0
  return stats.value.total_lessons
    ? Math.round((stats.value.total_completed / stats.value.total_lessons) * 100)
    : 0
})

const totalTimeFormatted = computed(() => {
  if (!stats.value) return text.value.zeroMinutes
  const h = Math.floor(stats.value.total_time_seconds / 3600)
  const m = Math.floor((stats.value.total_time_seconds % 3600) / 60)
  if (h > 0) return `${h} ${text.value.hourUnit} ${m} ${text.value.minuteUnit}`
  return `${m} ${text.value.minuteUnit}`
})

// Build a 52-week calendar (GitHub-style)
const calendarWeeks = computed(() => {
  if (!stats.value) return []
  const weeks: Array<Array<{ date: string; count: number }>> = []
  const today = new Date()
  const start = new Date(today)
  start.setDate(today.getDate() - 363) // ~52 weeks back

  let current = new Date(start)
  let week: Array<{ date: string; count: number }> = []

  // Pad to Sunday
  while (current.getDay() !== 0) {
    current.setDate(current.getDate() - 1)
  }

  while (current <= today) {
    const dateStr = current.toISOString().split('T')[0]
    week.push({ date: dateStr, count: stats.value.daily_activity[dateStr] || 0 })
    if (week.length === 7) {
      weeks.push(week)
      week = []
    }
    current.setDate(current.getDate() + 1)
  }
  if (week.length) weeks.push(week)
  return weeks
})

function cellLevel(count: number): string {
  if (count === 0) return '0'
  if (count === 1) return '1'
  if (count <= 2) return '2'
  if (count <= 4) return '3'
  return '4'
}

function formatTime(secs: number): string {
  if (secs < 60) return `${secs}${text.value.secondUnit}`
  const m = Math.floor(secs / 60)
  const s = secs % 60
  return s ? `${m}${text.value.minuteUnit} ${s}${text.value.secondUnit}` : `${m}${text.value.minuteUnit}`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short', year: 'numeric' })
}

function levelLabel(level: string): string {
  const labels: Record<string, string> = {
    junior: 'Junior',
    middle: 'Middle',
    senior: 'Senior',
  }
  return labels[level] || level
}
</script>

<template>
  <div class="lp-page overflow-y-auto">
    <div class="mx-auto w-full max-w-6xl px-4 py-5">
      <div class="mb-4 flex items-center gap-3">
        <RouterLink to="/">
          <UiButton size="sm">{{ messages.common.back }}</UiButton>
        </RouterLink>
        <h1 class="text-2xl font-semibold">{{ text.learningStats }}</h1>
      </div>

      <div v-if="loading" class="py-10 text-center text-sm text-text-secondary">
        {{ messages.status.loading }}
      </div>
      <UiAlert v-else-if="error" class="mb-4" variant="error">
        <span>{{ error }} {{ messages.status.genericRetryHint }}</span>
        <UiButton size="sm" @click="loadStatsData">{{ messages.common.retry }}</UiButton>
      </UiAlert>

      <template v-else-if="stats">
        <div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <UiCard><div class="text-xl font-semibold">{{ stats.total_completed }}</div><div class="text-xs text-text-secondary">{{ text.completedLessons }}</div></UiCard>
          <UiCard><div class="text-xl font-semibold">{{ totalPercent }}%</div><div class="text-xs text-text-secondary">{{ text.overallProgress }}</div></UiCard>
          <UiCard><div class="text-xl font-semibold">{{ totalTimeFormatted }}</div><div class="text-xs text-text-secondary">{{ text.totalTime }}</div></UiCard>
          <UiCard v-if="adaptive"><div class="text-xl font-semibold">{{ messages.common.levelPrefix }}{{ adaptive.gamification.level }}</div><div class="text-xs text-text-secondary">{{ ui.level }} · {{ adaptive.gamification.xp }} XP</div></UiCard>
        </div>

        <UiCard class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.progressByLevels }}</h3>
          <div
            v-for="(data, level) in stats.by_level"
            :key="level"
            class="mb-2 grid grid-cols-[90px_minmax(0,1fr)_56px] items-center gap-2"
          >
            <span class="text-xs text-text-secondary">{{ levelLabel(level) }}</span>
            <div class="h-2 rounded bg-bg-tertiary">
              <div
                class="h-2 rounded bg-accent"
                :style="{ width: data.total ? (data.done / data.total * 100) + '%' : '0%' }"
              ></div>
            </div>
            <span class="text-xs text-text-secondary">{{ data.done }}/{{ data.total }}</span>
          </div>
        </UiCard>

        <UiCard class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.activity52Weeks }}</h3>
          <div class="flex gap-1 overflow-auto">
            <div v-for="(week, wi) in calendarWeeks" :key="wi" class="grid grid-rows-7 gap-1">
              <div
                v-for="day in week"
                :key="day.date"
                class="h-3 w-3 rounded-sm border border-border/70"
                :data-count="cellLevel(day.count)"
                :style="{ backgroundColor: day.count === 0 ? 'var(--bg-tertiary)' : day.count <= 2 ? 'color-mix(in srgb, var(--accent) 45%, transparent)' : 'var(--accent)' }"
                :title="`${day.date}: ${day.count} ${text.value.lessonCountSuffix}`"
              ></div>
            </div>
          </div>
        </UiCard>

        <UiCard v-if="adaptive" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.weakTopics }}</h3>
          <div v-if="!adaptive.weak_topics?.length" class="text-sm text-text-secondary">{{ text.noWeakTopics }}</div>
          <div v-else class="flex flex-wrap gap-2">
            <span v-for="t in adaptive.weak_topics" :key="t.topic" class="rounded-full border border-border bg-bg-tertiary px-2 py-1 text-xs">
              {{ t.topic }} · {{ t.count }}
            </span>
          </div>
        </UiCard>

        <UiCard v-if="adaptive?.quests" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.quests }}</h3>
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div class="rounded-lg border border-border p-3">
              <div class="mb-2 text-xs text-text-secondary">{{ ui.daily }}</div>
              <div v-for="q in adaptive.quests.daily" :key="q.id" class="quest-row">
                <span>{{ q.done ? '✅' : '🎯' }} {{ q.title }}</span>
                <strong>{{ q.progress }}/{{ q.target }}</strong>
              </div>
            </div>
            <div class="rounded-lg border border-border p-3">
              <div class="mb-2 text-xs text-text-secondary">{{ ui.weekly }}</div>
              <div v-for="q in adaptive.quests.weekly" :key="q.id" class="quest-row">
                <span>{{ q.done ? '✅' : '🎯' }} {{ q.title }}</span>
                <strong>{{ q.progress }}/{{ q.target }}</strong>
              </div>
            </div>
          </div>
        </UiCard>

        <UiCard v-if="adaptive?.next_lessons?.length" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.adaptiveRecommendationsTop3 }}</h3>
          <div class="flex flex-wrap gap-2">
            <RouterLink
              v-for="item in adaptive.next_lessons"
              :key="`${item.module_id}/${item.lesson_id}`"
              :to="`/lesson/${item.module_id}/${item.lesson_id}`"
              class="rounded-full border border-border bg-bg-tertiary px-2 py-1 text-xs hover:border-accent"
              :title="`${ui.score}: ${item.score ?? 0} · ${item.reason ?? ''}`"
            >
              {{ item.title || item.lesson_id }} · {{ item.score ?? 0 }}
            </RouterLink>
          </div>
        </UiCard>

        <UiCard v-if="adaptive" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.skillsMap }}</h3>
          <div
            v-for="(node, name) in adaptive.skill_map"
            :key="name"
            class="mb-2 grid grid-cols-[120px_minmax(0,1fr)_56px] items-center gap-2"
          >
            <span class="text-xs text-text-secondary">{{ name }}</span>
            <div class="h-2 rounded bg-bg-tertiary">
              <div class="h-2 rounded bg-accent" :style="{ width: node.percent + '%' }"></div>
            </div>
            <span class="text-xs text-text-secondary">{{ node.done }}/{{ node.total }}</span>
          </div>
        </UiCard>

        <UiCard v-if="adaptive?.skill_lesson_matrix" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.skillsMatrixByLesson }}</h3>
          <div v-for="(rows, skill) in adaptive.skill_lesson_matrix" :key="skill" class="mb-3">
            <div class="mb-1 text-xs text-text-secondary">{{ skill }}</div>
            <div class="flex flex-wrap gap-2">
              <RouterLink
                v-for="item in rows"
                :key="`${item.module_id}/${item.lesson_id}`"
                :to="`/lesson/${item.module_id}/${item.lesson_id}`"
                class="rounded-full border bg-bg-tertiary px-2 py-1 text-xs"
                :style="{ borderColor: item.done ? 'var(--success)' : 'var(--border)' }"
              >
                {{ item.done ? '✓' : '○' }} {{ item.title }}
              </RouterLink>
            </div>
          </div>
        </UiCard>

        <UiCard v-if="adaptive" class="mb-4">
          <h3 class="mb-3 text-base font-semibold">{{ text.badges }}</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="b in adaptive.gamification.badges" :key="b" class="rounded-full border border-border bg-bg-tertiary px-2 py-1 text-xs">{{ b }}</span>
            <span v-if="!adaptive.gamification.badges.length" class="text-sm text-text-secondary">{{ text.noBadges }}</span>
          </div>
        </UiCard>

        <UiCard>
          <h3 class="mb-3 text-base font-semibold">{{ text.completedLessonsSection }}</h3>
          <div v-if="!stats.lesson_times.length" class="text-sm text-text-secondary">
            {{ text.noCompletedLessons }}
          </div>
          <table v-else class="w-full border-collapse overflow-hidden rounded-lg border border-border text-sm">
            <thead>
              <tr class="bg-bg-tertiary text-left text-xs text-text-secondary">
                <th class="px-2 py-2">{{ text.colModule }}</th>
                <th class="px-2 py-2">{{ text.colLesson }}</th>
                <th class="px-2 py-2">{{ text.colTime }}</th>
                <th class="px-2 py-2">{{ text.colDate }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in stats.lesson_times" :key="i" class="border-t border-border">
                <td class="px-2 py-2">{{ item.module_id }}</td>
                <td class="px-2 py-2">{{ item.lesson_id }}</td>
                <td class="px-2 py-2">{{ item.time_spent ? formatTime(item.time_spent) : '—' }}</td>
                <td class="px-2 py-2">{{ formatDate(item.completed_at) }}</td>
              </tr>
            </tbody>
          </table>
        </UiCard>
      </template>
    </div>
  </div>
</template>
