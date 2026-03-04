import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export interface LessonMeta {
  difficulty: string
  time: string
  prev: string | null
  next: string | null
}

export interface LessonContent {
  theory: string
  task: string
  example: string
  resources: Array<{ name: string; url: string }>
  hints: string[]
  meta: LessonMeta
}

export interface LessonItem {
  id: string
  title: string
}

export interface ModuleData {
  id: string
  name: string
  lessons: LessonItem[]
}

export const useLessonsStore = defineStore('lessons', () => {
  const auth = useAuthStore()

  const levelsData = ref<Record<string, { modules: Array<{ id: string }> }> | null>(null)
  const currentContent = ref<LessonContent | null>(null)
  const currentModule = ref<string | null>(null)
  const currentLesson = ref<string | null>(null)
  const currentTitle = ref('')
  const solution = ref<string | null>(null)

  async function loadLevels() {
    const res = await fetch('/api/levels')
    levelsData.value = await res.json()
  }

  async function loadModuleData(moduleId: string): Promise<ModuleData> {
    const res = await fetch(`/api/lessons/${moduleId}`)
    const data = await res.json()
    return { id: moduleId, name: data.module, lessons: data.lessons }
  }

  async function loadLesson(moduleId: string, lessonId: string) {
    currentModule.value = moduleId
    currentLesson.value = lessonId
    solution.value = null
    currentContent.value = null

    const res = await fetch(`/api/lessons/${moduleId}/${lessonId}`)
    currentContent.value = await res.json()
    currentTitle.value = currentContent.value?.meta
      ? lessonId.replace(/^lesson_\d+_/, '').replace(/_/g, ' ')
      : lessonId
  }

  async function loadSolution(moduleId: string, lessonId: string) {
    try {
      const res = await fetch(`/api/lessons/${moduleId}/${lessonId}/solution`, {
        headers: auth.authHeaders(),
      })
      const data = await res.json()
      solution.value = data.solution ?? null
    } catch {
      solution.value = null
    }
  }

  async function getNote(moduleId: string, lessonId: string): Promise<string> {
    if (!auth.isLoggedIn) return ''
    try {
      const res = await fetch(
        `/api/notes?module_id=${moduleId}&lesson_id=${lessonId}`,
        { headers: auth.authHeaders() }
      )
      const data = await res.json()
      return data.content || ''
    } catch {
      return ''
    }
  }

  async function saveNote(moduleId: string, lessonId: string, content: string) {
    if (!auth.isLoggedIn) return
    await fetch('/api/notes', {
      method: 'POST',
      headers: auth.authHeaders(),
      body: JSON.stringify({ module_id: moduleId, lesson_id: lessonId, content }),
    })
  }

  return {
    levelsData,
    currentContent,
    currentModule,
    currentLesson,
    currentTitle,
    solution,
    loadLevels,
    loadModuleData,
    loadLesson,
    loadSolution,
    getNote,
    saveNote,
  }
})
