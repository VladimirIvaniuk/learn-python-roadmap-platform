<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUiLanguage } from '../composables/useUiLanguage'

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

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await fetch('/api/stats', { headers: auth.authHeaders() })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    stats.value = await res.json()
    const adaptiveRes = await fetch('/api/adaptive/summary', { headers: auth.authHeaders() })
    if (adaptiveRes.ok) adaptive.value = await adaptiveRes.json()
  } catch (e: unknown) {
    error.value = messages.value.errors.statsLoadPrefix + String(e)
  } finally {
    loading.value = false
  }
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
  <div style="background: var(--bg-primary); min-height: 100vh; overflow-y: auto;">
    <div class="stats-page">
      <div class="stats-header">
        <RouterLink to="/" class="btn btn-small">{{ messages.common.back }}</RouterLink>
        <h1 style="font-size: 1.4rem;">{{ text.learningStats }}</h1>
      </div>

      <div v-if="loading" style="color: var(--text-secondary); text-align: center; padding: 3rem;">
        {{ messages.status.loading }}
      </div>
      <div v-else-if="error" style="color: var(--error); padding: 1rem;">{{ error }}</div>

      <template v-else-if="stats">
        <!-- Summary cards -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_completed }}</div>
            <div class="stat-label">{{ text.completedLessons }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ totalPercent }}%</div>
            <div class="stat-label">{{ text.overallProgress }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ totalTimeFormatted }}</div>
            <div class="stat-label">{{ text.totalTime }}</div>
          </div>
          <div v-if="adaptive" class="stat-card">
            <div class="stat-value">{{ messages.common.levelPrefix }}{{ adaptive.gamification.level }}</div>
            <div class="stat-label">{{ ui.level }} · {{ adaptive.gamification.xp }} XP</div>
          </div>
        </div>

        <!-- Progress by level -->
        <div class="stats-section">
          <h3>{{ text.progressByLevels }}</h3>
          <div
            v-for="(data, level) in stats.by_level"
            :key="level"
            class="progress-bar-row"
          >
            <span class="progress-bar-label">{{ levelLabel(level) }}</span>
            <div class="progress-bar-track">
              <div
                class="progress-bar-fill"
                :style="{ width: data.total ? (data.done / data.total * 100) + '%' : '0%' }"
              ></div>
            </div>
            <span class="progress-bar-text">{{ data.done }}/{{ data.total }}</span>
          </div>
        </div>

        <!-- Activity calendar -->
        <div class="stats-section">
          <h3>{{ text.activity52Weeks }}</h3>
          <div class="calendar">
            <div v-for="(week, wi) in calendarWeeks" :key="wi" class="calendar-week">
              <div
                v-for="day in week"
                :key="day.date"
                class="calendar-cell"
                :data-count="cellLevel(day.count)"
                :title="`${day.date}: ${day.count} ${text.value.lessonCountSuffix}`"
              ></div>
            </div>
          </div>
        </div>

        <div v-if="adaptive" class="stats-section">
          <h3>{{ text.weakTopics }}</h3>
          <div v-if="!adaptive.weak_topics?.length" style="color: var(--text-secondary); font-size: .85rem;">{{ text.noWeakTopics }}</div>
          <div v-else class="badges-wrap">
            <span v-for="t in adaptive.weak_topics" :key="t.topic" class="badge-chip">
              {{ t.topic }} · {{ t.count }}
            </span>
          </div>
        </div>

        <div v-if="adaptive?.quests" class="stats-section">
          <h3>{{ text.quests }}</h3>
          <div class="stats-cards" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin-bottom: 0;">
            <div class="stat-card" style="text-align:left;">
              <div style="font-size: .82rem; color: var(--text-secondary); margin-bottom: .5rem;">{{ ui.daily }}</div>
              <div v-for="q in adaptive.quests.daily" :key="q.id" class="quest-row">
                <span>{{ q.done ? '✅' : '🎯' }} {{ q.title }}</span>
                <strong>{{ q.progress }}/{{ q.target }}</strong>
              </div>
            </div>
            <div class="stat-card" style="text-align:left;">
              <div style="font-size: .82rem; color: var(--text-secondary); margin-bottom: .5rem;">{{ ui.weekly }}</div>
              <div v-for="q in adaptive.quests.weekly" :key="q.id" class="quest-row">
                <span>{{ q.done ? '✅' : '🎯' }} {{ q.title }}</span>
                <strong>{{ q.progress }}/{{ q.target }}</strong>
              </div>
            </div>
          </div>
        </div>

        <div v-if="adaptive?.next_lessons?.length" class="stats-section">
          <h3>{{ text.adaptiveRecommendationsTop3 }}</h3>
          <div class="badges-wrap">
            <RouterLink
              v-for="item in adaptive.next_lessons"
              :key="`${item.module_id}/${item.lesson_id}`"
              :to="`/lesson/${item.module_id}/${item.lesson_id}`"
              class="badge-chip"
              :title="`${ui.score}: ${item.score ?? 0} · ${item.reason ?? ''}`"
            >
              {{ item.title || item.lesson_id }} · {{ item.score ?? 0 }}
            </RouterLink>
          </div>
        </div>

        <div v-if="adaptive" class="stats-section">
          <h3>{{ text.skillsMap }}</h3>
          <div
            v-for="(node, name) in adaptive.skill_map"
            :key="name"
            class="progress-bar-row"
          >
            <span class="progress-bar-label">{{ name }}</span>
            <div class="progress-bar-track">
              <div class="progress-bar-fill" :style="{ width: node.percent + '%' }"></div>
            </div>
            <span class="progress-bar-text">{{ node.done }}/{{ node.total }}</span>
          </div>
        </div>

        <div v-if="adaptive?.skill_lesson_matrix" class="stats-section">
          <h3>{{ text.skillsMatrixByLesson }}</h3>
          <div v-for="(rows, skill) in adaptive.skill_lesson_matrix" :key="skill" style="margin-bottom: .8rem;">
            <div style="font-size: .82rem; color: var(--text-secondary); margin-bottom: .35rem;">{{ skill }}</div>
            <div class="badges-wrap">
              <RouterLink
                v-for="item in rows"
                :key="`${item.module_id}/${item.lesson_id}`"
                :to="`/lesson/${item.module_id}/${item.lesson_id}`"
                class="badge-chip"
                :style="{ borderColor: item.done ? 'var(--success)' : 'var(--border)' }"
              >
                {{ item.done ? '✓' : '○' }} {{ item.title }}
              </RouterLink>
            </div>
          </div>
        </div>

        <div v-if="adaptive" class="stats-section">
          <h3>{{ text.badges }}</h3>
          <div class="badges-wrap">
            <span v-for="b in adaptive.gamification.badges" :key="b" class="badge-chip">{{ b }}</span>
            <span v-if="!adaptive.gamification.badges.length" style="color: var(--text-secondary); font-size: .85rem;">{{ text.noBadges }}</span>
          </div>
        </div>

        <!-- Completed lessons table -->
        <div class="stats-section">
          <h3>{{ text.completedLessonsSection }}</h3>
          <div v-if="!stats.lesson_times.length" style="color: var(--text-secondary); font-size: 0.85rem;">
            {{ text.noCompletedLessons }}
          </div>
          <table v-else class="completed-table">
            <thead>
              <tr>
                <th>{{ text.colModule }}</th>
                <th>{{ text.colLesson }}</th>
                <th>{{ text.colTime }}</th>
                <th>{{ text.colDate }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in stats.lesson_times" :key="i">
                <td>{{ item.module_id }}</td>
                <td>{{ item.lesson_id }}</td>
                <td>{{ item.time_spent ? formatTime(item.time_spent) : '—' }}</td>
                <td>{{ formatDate(item.completed_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>
