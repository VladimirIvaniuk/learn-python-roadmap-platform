<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import { useLessonsStore, type ModuleData } from '../stores/lessons'
import { GOAL_PRESET_ORDER, type GoalPreset } from '../i18n/ui'
import { useUiLanguage } from '../composables/useUiLanguage'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import UiButton from './ui/UiButton.vue'
import UiInput from './ui/UiInput.vue'
import UiSelect from './ui/UiSelect.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const progress = useProgressStore()
const lessons = useLessonsStore()

const currentLevel = ref('junior')
const modulesData = ref<ModuleData[]>([])
const openModuleId = ref<string | null>(null)
const searchQuery = ref('')
const searchDifficulty = ref('all')
const searchTopic = ref('')
const searchMaxMinutes = ref<number>(0)
const searchLoading = ref(false)
const searchError = ref('')
const searchResults = ref<Array<{
  module_id: string
  lesson_id: string
  title: string
  difficulty: string
  time_text: string
  topics: string[]
}>>([])
const loading = ref(false)
const compactMode = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const LEVELS = [
  { id: 'junior', label: 'Junior' },
  { id: 'middle', label: 'Middle' },
  { id: 'senior', label: 'Senior' },
]

async function loadModules() {
  loading.value = true
  try {
    if (!lessons.levelsData) await lessons.loadLevels()
    const mods: Array<{ id: string }> =
      lessons.levelsData?.[currentLevel.value]?.modules ?? []
    modulesData.value = await Promise.all(mods.map(m => lessons.loadModuleData(m.id)))
  } finally {
    loading.value = false
  }
}

const filteredModules = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return modulesData.value
  return modulesData.value
    .map(mod => ({ ...mod, lessons: mod.lessons.filter(l => l.title.toLowerCase().includes(q)) }))
    .filter(mod => mod.lessons.length > 0)
})
const hasSearchFilters = computed(() =>
  !!searchQuery.value.trim() ||
  searchDifficulty.value !== 'all' ||
  !!searchTopic.value.trim() ||
  searchMaxMinutes.value > 0
)
const difficultyOptions = computed(() => ([
  { value: 'all', label: messages.value.sidebar.searchAllDifficulties },
  { value: 'easy', label: messages.value.home.difficultyEasy },
  { value: 'medium', label: messages.value.home.difficultyMedium },
  { value: 'hard', label: messages.value.home.difficultyHard },
]))

const hasAdaptive = computed(() => auth.isLoggedIn && !!progress.nextLesson)
const adaptiveTop = computed(() => progress.nextLessons.slice(0, 3))
const goalPreset = computed({
  get: () => (progress.gamification.goal_preset as GoalPreset) || 'balanced',
  set: async (v) => {
    await progress.setGoalPreset(v)
  },
})
const { messages, language, toggleLanguage } = useUiLanguage()
const loginTarget = computed(() => {
  const current = route.fullPath || '/'
  return { path: '/login', query: { returnTo: current } }
})
const goalPresetOptions = computed(() =>
  GOAL_PRESET_ORDER.map((value) => ({ value, label: messages.value.common.goalPresets[value] }))
)

function goToAdaptiveNext() {
  const next = progress.nextLesson
  if (!next) return
  goToLesson(next.module_id, next.lesson_id)
}

function toggleModule(id: string) {
  openModuleId.value = openModuleId.value === id ? null : id
}

function goToLesson(moduleId: string, lessonId: string) {
  router.push(`/lesson/${moduleId}/${lessonId}`)
}

function isActive(moduleId: string, lessonId: string) {
  return route.params.moduleId === moduleId && route.params.lessonId === lessonId
}

function toggleTheme() {
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', next)
  localStorage.setItem('learn_python_theme', next)
}

function exportProgress() {
  const blob = new Blob(
    [JSON.stringify({ completed: progress.completed, streak: progress.streak, date: new Date().toISOString() }, null, 2)],
    { type: 'application/json' }
  )
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob),
    download: 'learn_python_progress.json',
  })
  a.click()
  URL.revokeObjectURL(a.href)
}

function toggleCompactMode() {
  compactMode.value = !compactMode.value
}

async function runServerSearch() {
  if (!hasSearchFilters.value) {
    searchResults.value = []
    searchError.value = ''
    return
  }
  searchLoading.value = true
  searchError.value = ''
  try {
    searchResults.value = await lessons.searchLessons({
      q: searchQuery.value,
      level: currentLevel.value,
      difficulty: searchDifficulty.value,
      topic: searchTopic.value,
      maxTime: searchMaxMinutes.value > 0 ? searchMaxMinutes.value : undefined,
    })
  } catch {
    searchError.value = messages.value.sidebar.searchFailed
  } finally {
    searchLoading.value = false
  }
}

watch(
  [searchQuery, searchDifficulty, searchTopic, searchMaxMinutes, currentLevel],
  () => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      runServerSearch()
    }, 250)
  }
)

function handleLogout() {
  auth.logout()
  router.push('/')
}

// Auto-open the module of the active lesson
watch(
  () => route.params.moduleId as string,
  id => { if (id) openModuleId.value = id },
  { immediate: true }
)

watch(currentLevel, loadModules)
onMounted(() => {
  compactMode.value = localStorage.getItem('learn_python_sidebar_compact') === '1'
  loadModules()
})

watch(compactMode, (enabled) => {
  localStorage.setItem('learn_python_sidebar_compact', enabled ? '1' : '0')
})

onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})
</script>

<template>
  <aside class="sidebar" :class="{ compact: compactMode }">
    <div class="logo">
      <h1>🐍 Learn Python</h1>
      <p>{{ messages.login.subtitle }}</p>
    </div>

    <div class="auth-header">
      <span class="user-name" data-testid="sidebar-user-name">{{ auth.user?.username || auth.user?.email || messages.sidebar.guest }}</span>
      <RouterLink v-if="!auth.isLoggedIn" :to="loginTarget" data-testid="sidebar-login-link">
        <UiButton size="sm">{{ messages.sidebar.login }}</UiButton>
      </RouterLink>
      <UiButton v-else size="sm" data-testid="sidebar-logout-button" @click="handleLogout">{{ messages.sidebar.logout }}</UiButton>
    </div>

    <div class="quick-links">
      <RouterLink to="/resources" class="resources-link">{{ messages.sidebar.resources }}</RouterLink>
      <RouterLink to="/stats" class="resources-link">{{ messages.sidebar.stats }}</RouterLink>
      <RouterLink to="/review" class="resources-link">{{ messages.sidebar.reviews }} <span v-if="progress.reviewsDueCount">({{ progress.reviewsDueCount }})</span></RouterLink>
      <RouterLink to="/plan" class="resources-link">{{ messages.sidebar.weeklyPlan }}</RouterLink>
    </div>

    <div class="top-actions">
      <UiInput v-model="searchQuery" :placeholder="messages.sidebar.searchLessons" />
      <div class="sidebar-actions-grid">
        <UiButton size="sm" :title="messages.sidebar.toggleTheme" @click="toggleTheme">🌓</UiButton>
        <UiButton size="sm" :title="messages.sidebar.exportProgress" @click="exportProgress">📥</UiButton>
        <UiButton size="sm" data-testid="language-toggle" :title="messages.common.languageToggleTitle" @click="toggleLanguage">
          {{ language === 'uk' ? 'UA' : 'EN' }}
        </UiButton>
        <UiButton
          size="sm"
          :title="compactMode ? messages.sidebar.compactDisable : messages.sidebar.compactEnable"
          @click="toggleCompactMode"
        >
          {{ compactMode ? '↔' : '⇔' }}
        </UiButton>
      </div>
    </div>

    <div class="search-filters">
      <UiInput v-model="searchTopic" :placeholder="messages.sidebar.searchTopic" />
      <div class="filter-row">
        <UiSelect v-model="searchDifficulty" :options="difficultyOptions" />
        <UiInput v-model="searchMaxMinutes" type="number" min="0" step="5" :placeholder="messages.sidebar.searchMaxMinutes" />
      </div>
      <div v-if="searchLoading" class="search-meta">{{ messages.status.loading }}</div>
      <div v-else-if="searchError" class="search-meta" style="color: var(--error);">{{ searchError }}</div>
    </div>

    <div class="level-tabs">
      <button
        v-for="lvl in LEVELS"
        :key="lvl.id"
        class="level-tab"
        :class="{ active: currentLevel === lvl.id }"
        @click="currentLevel = lvl.id"
      >{{ lvl.label }}</button>
    </div>

    <nav class="modules">
      <div v-if="loading" style="padding: 1rem; color: var(--text-secondary); font-size: 0.82rem;">
        {{ messages.sidebar.loading }}
      </div>

      <template v-if="hasSearchFilters">
        <div v-if="!searchResults.length && !searchLoading" class="search-meta">{{ messages.sidebar.searchNoResults }}</div>
        <a
          v-for="item in searchResults"
          :key="`${item.module_id}/${item.lesson_id}`"
          href="#"
          class="lesson-item"
          :class="{ active: isActive(item.module_id, item.lesson_id), completed: progress.isCompleted(item.module_id, item.lesson_id) }"
          @click.prevent="goToLesson(item.module_id, item.lesson_id)"
        >
          <span class="lesson-check"></span>
          {{ item.title }}
        </a>
      </template>

      <template v-else v-for="mod in filteredModules" :key="mod.id">
        <button
          class="module-btn"
          :class="{ active: openModuleId === mod.id }"
          @click="toggleModule(mod.id)"
        >{{ mod.name }}</button>

        <div class="lesson-list" :class="{ open: openModuleId === mod.id }">
          <a
            v-for="lesson in mod.lessons"
            :key="lesson.id"
            href="#"
            class="lesson-item"
            :class="{
              active: isActive(mod.id, lesson.id),
              completed: progress.isCompleted(mod.id, lesson.id),
            }"
            @click.prevent="goToLesson(mod.id, lesson.id)"
          >
            <span class="lesson-check"></span>
            {{ lesson.title }}
          </a>
        </div>
      </template>
    </nav>

    <div v-if="auth.isLoggedIn" class="adaptive-card">
      <div class="adaptive-title">🧭 {{ messages.terms.adaptiveRoute }}</div>
      <div class="adaptive-row">XP: <strong>{{ progress.gamification.xp }}</strong> · {{ messages.terms.level }} {{ progress.gamification.level }}</div>
      <div class="adaptive-row">{{ messages.sidebar.reviewsNow }} <strong>{{ progress.reviewsDueCount }}</strong></div>
      <div style="margin-top: 0.4rem; margin-bottom: 0.4rem;">
        <label class="adaptive-row">{{ messages.sidebar.goal }}</label>
        <UiSelect v-model="goalPreset" :options="goalPresetOptions" />
      </div>
      <UiButton
        size="sm"
        style="margin-top: .4rem; width: 100%;"
        :disabled="!hasAdaptive"
        @click="goToAdaptiveNext"
      >
        {{ hasAdaptive ? messages.sidebar.continue : messages.sidebar.noRecommendations }}
      </UiButton>

      <Disclosure v-if="adaptiveTop.length" as="div" style="margin-top: .5rem;">
        <DisclosureButton class="adaptive-block-title">{{ messages.sidebar.recommendationsPanel }}</DisclosureButton>
        <DisclosurePanel style="margin-top: .3rem;">
          <button
            v-for="item in adaptiveTop"
            :key="`${item.module_id}/${item.lesson_id}`"
            class="adaptive-rec-card"
            :title="`${messages.terms.score}: ${item.score ?? 0} · ${item.reason}`"
            @click="goToLesson(item.module_id, item.lesson_id)"
          >
            <div class="adaptive-rec-title">{{ item.title || item.lesson_id }}</div>
            <div class="adaptive-rec-reason">{{ item.reason }} · {{ messages.terms.score }} {{ item.score ?? 0 }}</div>
          </button>
        </DisclosurePanel>
      </Disclosure>

      <Disclosure v-if="progress.quests.daily.length" as="div" style="margin-top: .5rem;">
        <DisclosureButton class="adaptive-block-title">{{ messages.sidebar.questsPanel }}</DisclosureButton>
        <DisclosurePanel style="margin-top: .3rem;">
          <div v-for="q in progress.quests.daily" :key="q.id" class="quest-row">
            <span>{{ q.done ? '✅' : '🎯' }} {{ q.title }}</span>
            <span>{{ q.progress }}/{{ q.target }}</span>
          </div>
        </DisclosurePanel>
      </Disclosure>
    </div>
  </aside>
</template>
