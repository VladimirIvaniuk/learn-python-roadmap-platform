import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useProgressStore = defineStore('progress', () => {
  const auth = useAuthStore()

  const completed = ref<string[]>([])
  const total = ref(0)
  const byLevel = ref<Record<string, { done: number; total: number }>>({})
  const weakTopics = ref<Array<{ topic: string; count: number }>>([])
  const reviewsDueCount = ref(0)
  const reviewsDue = ref<Array<{
    module_id: string
    lesson_id: string
    topic: string
    due_at: string | null
    overdue?: boolean
    interval_days?: number
    repetitions?: number
    last_result?: number
  }>>([])
  const nextLesson = ref<{ module_id: string; lesson_id: string; reason: string } | null>(null)
  const nextLessons = ref<Array<{ module_id: string; lesson_id: string; reason: string; title?: string; score?: number }>>([])
  const gamification = ref<{ xp: number; level: number; badges: string[]; goal_preset?: string }>({ xp: 0, level: 1, badges: [], goal_preset: 'balanced' })
  const skillMap = ref<Record<string, { done: number; total: number; percent: number }>>({})
  const skillLessonMatrix = ref<Record<string, Array<{ module_id: string; lesson_id: string; title: string; done: boolean }>>>({})
  const quests = ref<{ daily: Array<{ id: string; title: string; target: number; progress: number; done: boolean }>; weekly: Array<{ id: string; title: string; target: number; progress: number; done: boolean }> }>({ daily: [], weekly: [] })
  const weeklyPlan = ref<{
    preset: string
    generated_at: string
    days: Array<{
      day_index: number
      date: string
      focus: string
      estimated_minutes: number
      tasks: Array<Record<string, unknown>>
      progress?: { done: number; total: number }
    }>
  } | null>(null)

  const streak = ref(parseInt(localStorage.getItem('learn_python_streak') || '0'))
  const lastActivityDate = ref(localStorage.getItem('learn_python_last_date') || '')

  async function load() {
    try {
      const res = await fetch('/api/progress', { headers: auth.authHeaders() })
      const data = await res.json()
      if (auth.isLoggedIn) {
        completed.value = data.completed || []
      } else {
        completed.value = JSON.parse(
          localStorage.getItem('learn_python_completed') || '[]'
        )
      }
      total.value = data.total || 0
      byLevel.value = data.by_level || {}
      if (auth.isLoggedIn) await loadAdaptiveSummary()
    } catch {
      completed.value = JSON.parse(
        localStorage.getItem('learn_python_completed') || '[]'
      )
    }
  }

  async function loadAdaptiveSummary() {
    if (!auth.isLoggedIn) return
    try {
      const res = await fetch('/api/adaptive/summary', { headers: auth.authHeaders() })
      if (!res.ok) return
      const data = await res.json()
      weakTopics.value = data.weak_topics || []
      reviewsDueCount.value = data.reviews_due_count || 0
      reviewsDue.value = data.reviews_due || []
      nextLesson.value = data.next_lesson || null
      nextLessons.value = data.next_lessons || (data.next_lesson ? [data.next_lesson] : [])
      gamification.value = data.gamification || { xp: 0, level: 1, badges: [], goal_preset: 'balanced' }
      skillMap.value = data.skill_map || {}
      skillLessonMatrix.value = data.skill_lesson_matrix || {}
      quests.value = data.quests || { daily: [], weekly: [] }
    } catch {
      // non-critical
    }
  }

  async function loadReviewQueue() {
    if (!auth.isLoggedIn) return
    try {
      const res = await fetch('/api/review/queue', { headers: auth.authHeaders() })
      if (!res.ok) return
      const data = await res.json()
      reviewsDue.value = data.items || []
      reviewsDueCount.value = reviewsDue.value.filter(i => i.overdue).length
    } catch {
      // non-critical
    }
  }

  async function completeReview(moduleId: string, lessonId: string, topic: string, success: boolean) {
    if (!auth.isLoggedIn) return false
    try {
      const res = await fetch('/api/review/complete', {
        method: 'POST',
        headers: auth.authHeaders(),
        body: JSON.stringify({
          module_id: moduleId,
          lesson_id: lessonId,
          topic,
          success,
        }),
      })
      if (!res.ok) return false
      await loadReviewQueue()
      await loadAdaptiveSummary()
      await loadWeeklyPlan()
      return true
    } catch {
      return false
    }
  }

  async function loadWeeklyPlan() {
    if (!auth.isLoggedIn) return
    try {
      const res = await fetch('/api/plan/weekly', { headers: auth.authHeaders() })
      if (!res.ok) return
      weeklyPlan.value = await res.json()
    } catch {
      // non-critical
    }
  }

  async function planTaskAction(planDate: string, taskKey: string, action: 'done' | 'skip' | 'snooze' | 'pending') {
    if (!auth.isLoggedIn) return false
    try {
      const res = await fetch('/api/plan/task-action', {
        method: 'POST',
        headers: auth.authHeaders(),
        body: JSON.stringify({
          plan_date: planDate,
          task_key: taskKey,
          action,
        }),
      })
      if (!res.ok) return false
      await loadWeeklyPlan()
      await loadAdaptiveSummary()
      return true
    } catch {
      return false
    }
  }

  async function completeReviewSession(items: Array<{ module_id: string; lesson_id: string; topic: string; success: boolean }>) {
    if (!auth.isLoggedIn) return null
    try {
      const res = await fetch('/api/review/session', {
        method: 'POST',
        headers: auth.authHeaders(),
        body: JSON.stringify({ items }),
      })
      if (!res.ok) return null
      const data = await res.json()
      await loadReviewQueue()
      await loadAdaptiveSummary()
      return data
    } catch {
      return null
    }
  }

  async function setGoalPreset(preset: 'easy' | 'balanced' | 'intensive' | 'weekend') {
    if (!auth.isLoggedIn) return false
    try {
      const res = await fetch('/api/goals/preset', {
        method: 'POST',
        headers: auth.authHeaders(),
        body: JSON.stringify({ preset }),
      })
      if (!res.ok) return false
      gamification.value = { ...gamification.value, goal_preset: preset }
      await loadAdaptiveSummary()
      return true
    } catch {
      return false
    }
  }

  async function markComplete(moduleId: string, lessonId: string, timeSpent = 0) {
    const key = `${moduleId}/${lessonId}`
    if (completed.value.includes(key)) return

    completed.value.push(key)
    updateStreak()

    if (auth.isLoggedIn) {
      try {
        await fetch('/api/progress', {
          method: 'POST',
          headers: auth.authHeaders(),
          body: JSON.stringify({
            module_id: moduleId,
            lesson_id: lessonId,
            time_spent: timeSpent,
          }),
        })
      } catch {
        localStorage.setItem(
          'learn_python_completed',
          JSON.stringify(completed.value)
        )
      }
      await loadAdaptiveSummary()
    } else {
      localStorage.setItem(
        'learn_python_completed',
        JSON.stringify(completed.value)
      )
    }
  }

  function updateStreak() {
    const today = new Date().toDateString()
    if (lastActivityDate.value === today) return

    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    streak.value =
      lastActivityDate.value === yesterday.toDateString() ? streak.value + 1 : 1

    lastActivityDate.value = today
    localStorage.setItem('learn_python_streak', String(streak.value))
    localStorage.setItem('learn_python_last_date', today)
  }

  function isCompleted(moduleId: string, lessonId: string) {
    return completed.value.includes(`${moduleId}/${lessonId}`)
  }

  return {
    completed,
    total,
    byLevel,
    streak,
    weakTopics,
    reviewsDueCount,
    reviewsDue,
    nextLesson,
    nextLessons,
    gamification,
    skillMap,
    skillLessonMatrix,
    quests,
    weeklyPlan,
    load,
    loadAdaptiveSummary,
    loadWeeklyPlan,
    planTaskAction,
    loadReviewQueue,
    completeReview,
    completeReviewSession,
    setGoalPreset,
    markComplete,
    isCompleted,
  }
})
