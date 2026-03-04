<script setup lang="ts">
import { ref, watch, computed, onBeforeUnmount, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'
import LessonBody from '../components/LessonBody.vue'
import CodeEditor from '../components/CodeEditor.vue'
import HintModal from '../components/HintModal.vue'
import UiButton from '../components/ui/UiButton.vue'
import UiAlert from '../components/ui/UiAlert.vue'
import { useLessonsStore } from '../stores/lessons'
import { useProgressStore } from '../stores/progress'
import { useAuthStore } from '../stores/auth'
import { useTimer } from '../composables/useTimer'
import { useUiLanguage } from '../composables/useUiLanguage'

type DebugInfo = {
  error_type?: string
  title?: string
  summary?: string
  line?: number | null
  line_snippet?: string | null
  why?: string
  fix?: string[]
  example?: string | null
}

const route = useRoute()
const router = useRouter()
const lessons = useLessonsStore()
const progress = useProgressStore()
const auth = useAuthStore()
const timer = useTimer()

const code = ref('')
const output = ref('')
const outputError = ref(false)
const checkResult = ref<{
  passed: boolean
  message: string
  details: string[]
  weak_topics?: string[]
  smart_feedback?: { severity?: 'low' | 'medium' | 'high'; failed_steps?: string[]; next_actions?: string[]; weak_topics?: string[] }
} | null>(null)
const runDebug = ref<DebugInfo | null>(null)
const checkGamification = ref<{ xp: number; level: number; badges: string[] } | null>(null)
const attemptHistory = ref<Array<{
  module_id: string
  lesson_id: string
  passed: boolean
  error_type?: string
  weak_topics?: string[]
  feedback?: string
  created_at?: string | null
}>>([])
const feedbackMode = ref<'brief' | 'detailed'>((localStorage.getItem('learn_python_feedback_mode') as 'brief' | 'detailed') || 'brief')
const running = ref(false)
const hintOpen = ref(false)
const hintIndex = ref(0)
const leftPaneWidth = ref<number>(52)
const isResizingSplit = ref(false)
const outputCollapsed = ref(false)
const lessonLoadError = ref('')
const zenMode = ref(false)
const editorFullscreen = ref(false)
const readableMode = ref(false)
const highContrastMode = ref(false)
const sidebarCollapsed = ref(false)
const focusMode = ref(false)
const quickStartDismissed = ref(false)
const exampleLoadedNotice = ref(false)
let exampleLoadedTimer: ReturnType<typeof setTimeout> | null = null
const { messages } = useUiLanguage()
const text = computed(() => messages.value.home)
const terms = computed(() => messages.value.terms)

const theme = computed(() => localStorage.getItem('learn_python_theme') || 'dark')

// ── Lesson loading ───────────────────────────────────────────────────────────

watch(
  () => [route.params.moduleId as string, route.params.lessonId as string] as const,
  async ([moduleId, lessonId]) => {
    if (!moduleId || !lessonId) return
    localStorage.setItem('learn_python_last_lesson_path', `/lesson/${moduleId}/${lessonId}`)

    try {
      lessonLoadError.value = ''
      if (lessons.currentModule && lessons.currentLesson) {
        await timer.flush(lessons.currentModule, lessons.currentLesson)
      }
      await saveDraft()

      await lessons.loadLesson(moduleId, lessonId)
      hintIndex.value = 0
      checkResult.value = null
      checkGamification.value = null
      output.value = ''
      outputError.value = false
      runDebug.value = null

      code.value = await loadDraft(moduleId, lessonId)
      await loadAttemptHistory(moduleId, lessonId)
      timer.start()
    } catch {
      lessonLoadError.value = text.value.lessonLoadFailed
    }
  },
  { immediate: true }
)

async function retryLessonLoad() {
  const moduleId = route.params.moduleId as string
  const lessonId = route.params.lessonId as string
  if (!moduleId || !lessonId) return
  try {
    lessonLoadError.value = ''
    await lessons.loadLesson(moduleId, lessonId)
    code.value = await loadDraft(moduleId, lessonId)
  } catch {
    lessonLoadError.value = text.value.lessonLoadFailed
  }
}

// ── Draft helpers ────────────────────────────────────────────────────────────

const draftKey = (m: string, l: string) => `learn_python_draft_${m}/${l}`

async function saveDraft() {
  const m = lessons.currentModule
  const l = lessons.currentLesson
  if (!m || !l) return
  localStorage.setItem(draftKey(m, l), code.value)
  if (!auth.isLoggedIn) return
  try {
    await fetch('/api/code', {
      method: 'POST',
      headers: auth.authHeaders(),
      body: JSON.stringify({ module_id: m, lesson_id: l, code: code.value }),
    })
  } catch { /* non-critical */ }
}

function toggleFeedbackMode() {
  feedbackMode.value = feedbackMode.value === 'brief' ? 'detailed' : 'brief'
  localStorage.setItem('learn_python_feedback_mode', feedbackMode.value)
}

// ── Split resize / panel state ───────────────────────────────────────────────

function clamp(v: number, min: number, max: number) {
  return Math.min(max, Math.max(min, v))
}

function startSplitResize() {
  isResizingSplit.value = true
}

function onGlobalMouseMove(e: MouseEvent) {
  if (!isResizingSplit.value) return
  const el = document.querySelector('.main-split') as HTMLElement | null
  if (!el) return
  const rect = el.getBoundingClientRect()
  const next = ((e.clientX - rect.left) / rect.width) * 100
  leftPaneWidth.value = clamp(next, 30, 70)
}

function stopSplitResize() {
  isResizingSplit.value = false
}

function toggleOutputCollapsed() {
  outputCollapsed.value = !outputCollapsed.value
}

function toggleZenMode() {
  zenMode.value = !zenMode.value
}

function toggleEditorFullscreen() {
  editorFullscreen.value = !editorFullscreen.value
}

function toggleReadableMode() {
  readableMode.value = !readableMode.value
}

function toggleHighContrastMode() {
  highContrastMode.value = !highContrastMode.value
}

function toggleSidebarCollapsed() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function toggleFocusMode() {
  focusMode.value = !focusMode.value
}

function insertExample() {
  onLoadExample(lessons.currentContent?.example || '')
}

function onLoadExample(exampleCode: string) {
  if (!exampleCode) return
  code.value = exampleCode
  exampleLoadedNotice.value = true
  if (exampleLoadedTimer) clearTimeout(exampleLoadedTimer)
  exampleLoadedTimer = setTimeout(() => {
    exampleLoadedNotice.value = false
  }, 1600)
}

function onGlobalKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && editorFullscreen.value) {
    editorFullscreen.value = false
    return
  }
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.key.toLowerCase() === 'e') {
    e.preventDefault()
    toggleEditorFullscreen()
    return
  }
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    toggleReadableMode()
    return
  }
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.key.toLowerCase() === 'h') {
    e.preventDefault()
    toggleHighContrastMode()
    return
  }
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.key.toLowerCase() === 'b') {
    e.preventDefault()
    toggleSidebarCollapsed()
    return
  }
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.key.toLowerCase() === 'f') {
    e.preventDefault()
    toggleFocusMode()
  }
}

async function loadDraft(moduleId: string, lessonId: string): Promise<string> {
  const local = localStorage.getItem(draftKey(moduleId, lessonId)) || ''
  if (!auth.isLoggedIn) return local
  try {
    const res = await fetch(`/api/code?module_id=${moduleId}&lesson_id=${lessonId}`, {
      headers: auth.authHeaders(),
    })
    const data = await res.json()
    return data.code || local
  } catch {
    return local
  }
}

// ── Run / Check / Format ─────────────────────────────────────────────────────

async function runCode() {
  if (running.value) return
  running.value = true
  outputError.value = false
  output.value = ''
  runDebug.value = null
  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: auth.authHeaders(),
      body: JSON.stringify({ code: code.value }),
    })
    const data = await res.json()
    runDebug.value = data.debug || null
    if (data.success) {
      output.value = data.output || messages.value.status.emptyOutput
      if (data.error) {
        outputError.value = true
        output.value += `\n${messages.value.status.stderrPrefix}` + data.error
      }
    } else {
      outputError.value = true
      output.value = data.error || messages.value.errors.execution
    }
  } catch (err: unknown) {
    outputError.value = true
    output.value = `${messages.value.errors.network}: ` + String(err)
  } finally {
    running.value = false
  }
}

async function checkCode() {
  if (running.value || !lessons.currentLesson) return
  running.value = true
  checkResult.value = null
  try {
    const res = await fetch('/api/check', {
      method: 'POST',
      headers: auth.authHeaders(),
      body: JSON.stringify({
        lesson_id: lessons.currentLesson,
        module_id: lessons.currentModule,
        code: code.value,
      }),
    })
    const data = await res.json()
    checkResult.value = data
    checkGamification.value = data.gamification || null
    if (lessons.currentModule && lessons.currentLesson && auth.isLoggedIn) {
      await loadAttemptHistory(lessons.currentModule, lessons.currentLesson)
    }
    if (data.passed && lessons.currentModule && lessons.currentLesson) {
      const spent = timer.elapsed.value
      timer.reset()
      await progress.markComplete(lessons.currentModule, lessons.currentLesson, spent)
      await lessons.loadSolution(lessons.currentModule, lessons.currentLesson)
    }
    await progress.loadAdaptiveSummary()
  } catch (err: unknown) {
    checkResult.value = { passed: false, message: messages.value.errors.network, details: [String(err)] }
  } finally {
    running.value = false
  }
}

async function loadAttemptHistory(moduleId: string, lessonId: string) {
  if (!auth.isLoggedIn) {
    attemptHistory.value = []
    return
  }
  try {
    const res = await fetch(`/api/attempts?module_id=${moduleId}&lesson_id=${lessonId}&limit=5`, {
      headers: auth.authHeaders(),
    })
    if (!res.ok) return
    const data = await res.json()
    attemptHistory.value = data.items || []
  } catch {
    // non-critical
  }
}

async function formatCode() {
  if (!code.value.trim()) return
  try {
    const res = await fetch('/api/format', {
      method: 'POST',
      headers: auth.authHeaders(),
      body: JSON.stringify({ code: code.value }),
    })
    const data = await res.json()
    if (data.success) {
      code.value = data.code
    } else {
      output.value = data.error || messages.value.errors.formatting
      outputError.value = true
    }
  } catch { /* silent */ }
}

// ── Hints ────────────────────────────────────────────────────────────────────

const currentHint = computed(() => {
  const hints = lessons.currentContent?.hints ?? []
  return hints[Math.min(hintIndex.value, hints.length - 1)] ?? ''
})

function showHint() {
  if (!currentHint.value) return
  hintOpen.value = true
  const max = (lessons.currentContent?.hints?.length ?? 1) - 1
  if (hintIndex.value < max) hintIndex.value++
}

// ── Lesson meta display ──────────────────────────────────────────────────────

const lessonTitle = computed(() => {
  if (!lessons.currentLesson) return text.value.selectLesson
  if (lessons.currentTitle) {
    return lessons.currentTitle.charAt(0).toUpperCase() + lessons.currentTitle.slice(1)
  }
  return lessons.currentLesson.replace(/^lesson_\d+_/, '').replace(/_/g, ' ')
})

const metaText = computed(() => {
  const meta = lessons.currentContent?.meta
  if (!meta) return ''
  const diff: Record<string, string> = {
    easy: text.value.difficultyEasy,
    medium: text.value.difficultyMedium,
    hard: text.value.difficultyHard,
  }
  return [diff[meta.difficulty], meta.time].filter(Boolean).join(' · ')
})

const hasReviewQueue = computed(() => progress.reviewsDueCount > 0)
const localNextLessonId = computed(() => lessons.currentContent?.meta?.next || null)
const hasAdaptiveNext = computed(() => auth.isLoggedIn && !!progress.nextLesson)
const canGoToAnyNext = computed(() => {
  if (hasAdaptiveNext.value) return true
  return !!(lessons.currentModule && localNextLessonId.value)
})
const nextStepReason = computed(() => {
  if (hasAdaptiveNext.value && progress.nextLesson?.reason) return progress.nextLesson.reason
  if (localNextLessonId.value) return text.value.nextStepDefaultReason
  return ''
})

function goToNextStep() {
  if (hasAdaptiveNext.value && progress.nextLesson) {
    router.push(`/lesson/${progress.nextLesson.module_id}/${progress.nextLesson.lesson_id}`)
    return
  }
  if (lessons.currentModule && localNextLessonId.value) {
    router.push(`/lesson/${lessons.currentModule}/${localNextLessonId.value}`)
  }
}

function goToPlan() {
  router.push('/plan')
}

function goToReview() {
  router.push('/review')
}

const isCurrentCompleted = computed(() =>
  lessons.currentModule && lessons.currentLesson
    ? progress.isCompleted(lessons.currentModule, lessons.currentLesson)
    : false
)

// ── Cleanup ───────────────────────────────────────────────────────────────────

onBeforeUnmount(async () => {
  if (lessons.currentModule && lessons.currentLesson) {
    await timer.flush(lessons.currentModule, lessons.currentLesson)
    await saveDraft()
  }
})

onMounted(() => {
  const storedSplit = Number(localStorage.getItem('learn_python_split_left'))
  if (!Number.isNaN(storedSplit) && storedSplit > 0) {
    leftPaneWidth.value = clamp(storedSplit, 30, 70)
  }
  outputCollapsed.value = localStorage.getItem('learn_python_output_collapsed') === '1'
  zenMode.value = localStorage.getItem('learn_python_zen_mode') === '1'
  editorFullscreen.value = localStorage.getItem('learn_python_editor_fullscreen') === '1'
  readableMode.value = localStorage.getItem('learn_python_readable_mode') === '1'
  highContrastMode.value = localStorage.getItem('learn_python_high_contrast') === '1'
  sidebarCollapsed.value = localStorage.getItem('learn_python_sidebar_collapsed') === '1'
  focusMode.value = localStorage.getItem('learn_python_focus_mode') === '1'
  quickStartDismissed.value = localStorage.getItem('learn_python_quick_start_dismissed') === '1'
  window.addEventListener('mousemove', onGlobalMouseMove)
  window.addEventListener('mouseup', stopSplitResize)
  window.addEventListener('keydown', onGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onGlobalMouseMove)
  window.removeEventListener('mouseup', stopSplitResize)
  window.removeEventListener('keydown', onGlobalKeydown)
  if (exampleLoadedTimer) clearTimeout(exampleLoadedTimer)
})

watch(leftPaneWidth, (v) => {
  localStorage.setItem('learn_python_split_left', String(v))
})

watch(outputCollapsed, (v) => {
  localStorage.setItem('learn_python_output_collapsed', v ? '1' : '0')
})

watch(zenMode, (v) => {
  localStorage.setItem('learn_python_zen_mode', v ? '1' : '0')
})

watch(editorFullscreen, (v) => {
  localStorage.setItem('learn_python_editor_fullscreen', v ? '1' : '0')
})

watch(readableMode, (v) => {
  localStorage.setItem('learn_python_readable_mode', v ? '1' : '0')
})

watch(highContrastMode, (v) => {
  localStorage.setItem('learn_python_high_contrast', v ? '1' : '0')
})

watch(sidebarCollapsed, (v) => {
  localStorage.setItem('learn_python_sidebar_collapsed', v ? '1' : '0')
})

watch(focusMode, (v) => {
  localStorage.setItem('learn_python_focus_mode', v ? '1' : '0')
})

watch(quickStartDismissed, (v) => {
  localStorage.setItem('learn_python_quick_start_dismissed', v ? '1' : '0')
})

window.addEventListener('beforeunload', () => {
  const m = lessons.currentModule
  const l = lessons.currentLesson
  if (m && l && timer.elapsed.value >= 5 && auth.isLoggedIn) {
    navigator.sendBeacon('/api/time', JSON.stringify({ module_id: m, lesson_id: l, seconds: timer.elapsed.value }))
  }
})
</script>

<template>
  <div
    class="app lp-page"
    :class="{
      'zen-mode': zenMode,
      'editor-fullscreen': editorFullscreen,
      'readable-mode': readableMode,
      'high-contrast-mode': highContrastMode,
      'sidebar-collapsed': sidebarCollapsed,
      'focus-mode': focusMode,
    }"
  >
    <AppSidebar />

    <main class="content bg-bg-primary">
      <!-- Header -->
      <div class="lesson-header rounded-xl border border-border bg-bg-secondary">
        <div>
          <h2>{{ lessonTitle }}</h2>
          <div v-if="metaText" class="lesson-meta">{{ metaText }}</div>
        </div>
        <div class="header-right">
          <UiButton size="sm" @click="toggleSidebarCollapsed">
            {{ sidebarCollapsed ? text.showMenu : text.hideMenu }}
          </UiButton>
          <span v-if="isCurrentCompleted" style="color: var(--success);">{{ text.completed }}</span>
          <span v-if="lessons.currentLesson" class="timer">⏱ {{ timer.display }}</span>
          <span v-if="progress.streak" class="streak">🔥 {{ progress.streak }}</span>
          <span>{{ progress.completed.length }}/{{ progress.total }}</span>
        </div>
      </div>
      <UiAlert v-if="lessonLoadError" class="mx-3 mt-2" variant="error">
        <span>{{ lessonLoadError }} {{ messages.status.genericRetryHint }}</span>
        <UiButton size="sm" data-testid="retry-load-lesson" @click="retryLessonLoad">{{ messages.common.retry }}</UiButton>
      </UiAlert>

      <div v-if="lessons.currentLesson" class="next-step-bar rounded-lg border border-border bg-bg-secondary">
        <div class="next-step-info">
          <strong>{{ text.nextStepTitle }}</strong>
          <small v-if="nextStepReason">{{ text.nextStepReason }}: {{ nextStepReason }}</small>
        </div>
        <div class="next-step-actions">
          <UiButton
            variant="primary"
            size="sm"
            data-testid="next-step-primary"
            :disabled="!canGoToAnyNext"
            @click="goToNextStep"
          >
            {{ text.nextLesson }}
          </UiButton>
          <UiButton
            size="sm"
            data-testid="next-step-plan"
            :disabled="!auth.isLoggedIn"
            @click="goToPlan"
          >
            {{ text.toPlan }}
          </UiButton>
          <UiButton
            size="sm"
            data-testid="next-step-review"
            :disabled="!auth.isLoggedIn || !hasReviewQueue"
            @click="goToReview"
          >
            {{ text.toReview }}
          </UiButton>
        </div>
      </div>

      <!-- Split: lesson content + editor -->
      <div
        class="main-split"
        :style="{ gridTemplateColumns: `${leftPaneWidth}% 8px minmax(0, 1fr)` }"
      >
        <LessonBody @load-example="onLoadExample" />
        <div
          class="splitter"
          :class="{ active: isResizingSplit }"
          role="separator"
          :aria-label="text.resizePanelsAria"
          @mousedown.prevent="startSplitResize"
        ></div>

        <!-- Editor column -->
        <div class="editor-section">
          <div class="editor-header">
            <span>
              {{ text.editor }}
              <small
                class="shortcut-hint"
                :title="text.shortcutsTitle"
              >{{ text.shortcuts }}</small>
              <small v-if="exampleLoadedNotice" data-testid="example-loaded-home" class="inline-success">{{ text.exampleLoaded }}</small>
            </span>
            <div class="editor-actions">
              <div class="editor-actions-secondary">
                <UiButton
                  class="toolbar-btn"
                  size="sm"
                  data-testid="hint-button"
                  :disabled="!lessons.currentContent?.hints?.length"
                  @click="showHint"
                >{{ text.hint }}</UiButton>
                <details class="modes-menu">
                  <summary data-testid="modes-menu-trigger" class="toolbar-summary">{{ text.modes }}</summary>
                  <div class="modes-popover">
                    <UiButton size="sm" data-testid="mode-readable" :variant="readableMode ? 'primary' : 'secondary'" @click="toggleReadableMode">
                      {{ readableMode ? text.readableOn : text.readable }}
                    </UiButton>
                    <UiButton size="sm" data-testid="mode-contrast" :variant="highContrastMode ? 'primary' : 'secondary'" @click="toggleHighContrastMode">
                      {{ highContrastMode ? text.contrastOn : text.contrast }}
                    </UiButton>
                    <UiButton size="sm" data-testid="mode-fullscreen" :variant="editorFullscreen ? 'primary' : 'secondary'" @click="toggleEditorFullscreen">
                      {{ editorFullscreen ? text.fullscreenExit : text.fullscreen }}
                    </UiButton>
                    <UiButton size="sm" data-testid="mode-zen" :variant="zenMode ? 'primary' : 'secondary'" @click="toggleZenMode">
                      {{ zenMode ? text.zenOn : text.zen }}
                    </UiButton>
                    <UiButton size="sm" data-testid="mode-focus" :variant="focusMode ? 'primary' : 'secondary'" @click="toggleFocusMode">
                      {{ focusMode ? text.focusOn : text.focus }}
                    </UiButton>
                  </div>
                </details>
                <UiButton class="toolbar-btn" size="sm" :disabled="running" @click="formatCode">{{ text.format }}</UiButton>
              </div>
              <div class="editor-actions-primary">
                <UiButton class="run-cta" size="sm" data-testid="run-button" :disabled="running" @click="runCode">
                  {{ running ? text.running : text.run }}
                </UiButton>
                <UiButton class="check-cta" size="sm" variant="primary" data-testid="check-button" :disabled="running" @click="checkCode">
                  {{ running ? text.checking : text.check }}
                </UiButton>
              </div>
            </div>
          </div>

          <CodeEditor
            v-model="code"
            :theme="theme"
            :on-run="runCode"
            :on-check="checkCode"
          />

          <div
            v-if="!quickStartDismissed && !code.trim() && !running"
            class="quick-start-card"
          >
            <div class="quick-start-title">{{ text.quickStartTitle }}</div>
            <p class="quick-start-body">{{ text.quickStartBody }}</p>
            <div class="quick-start-actions">
              <UiButton size="sm" :disabled="!lessons.currentContent?.example" @click="insertExample">
                {{ text.quickStartLoadExample }}
              </UiButton>
              <UiButton size="sm" @click="quickStartDismissed = true">
                {{ text.quickStartDismiss }}
              </UiButton>
            </div>
          </div>

          <div v-show="!outputCollapsed" class="output-section">
            <div class="output-header">
              <span>{{ text.result }}</span>
              <UiButton size="sm" @click="toggleOutputCollapsed">{{ text.collapse }}</UiButton>
            </div>
            <pre :class="['output', { error: outputError }]">{{ output }}</pre>
          </div>
          <div v-show="outputCollapsed" class="output-section output-collapsed">
            <div class="output-header">
              <span>{{ text.resultHidden }}</span>
              <UiButton size="sm" @click="toggleOutputCollapsed">{{ text.show }}</UiButton>
            </div>
          </div>

          <div v-if="runDebug">
            <details v-if="focusMode" class="panel-accordion-item" open>
              <summary>{{ text.debug }}</summary>
              <div class="debug-panel">
                <p><strong>{{ runDebug.title || text.runtimeError }}</strong></p>
                <p v-if="runDebug.summary">{{ runDebug.summary }}</p>
                <p v-if="runDebug.line">{{ text.line }} <code>{{ runDebug.line }}</code></p>
                <p v-if="runDebug.line_snippet">{{ text.code }} <code>{{ runDebug.line_snippet }}</code></p>
                <p v-if="runDebug.why">{{ runDebug.why }}</p>
                <ul v-if="runDebug.fix?.length">
                  <li v-for="(fix, idx) in runDebug.fix" :key="idx">{{ fix }}</li>
                </ul>
                <pre v-if="runDebug.example" class="debug-example">{{ runDebug.example }}</pre>
              </div>
            </details>
            <div v-else class="debug-panel">
              <h4>{{ text.debugHuman }}</h4>
              <p><strong>{{ runDebug.title || text.runtimeError }}</strong></p>
              <p v-if="runDebug.summary">{{ runDebug.summary }}</p>
              <p v-if="runDebug.line">{{ text.line }} <code>{{ runDebug.line }}</code></p>
              <p v-if="runDebug.line_snippet">{{ text.code }} <code>{{ runDebug.line_snippet }}</code></p>
              <p v-if="runDebug.why">{{ runDebug.why }}</p>
              <ul v-if="runDebug.fix?.length">
                <li v-for="(fix, idx) in runDebug.fix" :key="idx">{{ fix }}</li>
              </ul>
              <pre v-if="runDebug.example" class="debug-example">{{ runDebug.example }}</pre>
            </div>
          </div>

          <div v-if="checkResult">
            <details
              v-if="focusMode"
              class="panel-accordion-item"
              :open="!checkResult.passed"
            >
              <summary>{{ checkResult.passed ? text.checkResultPassed : text.checkResultFailed }}</summary>
              <div class="check-result" :class="checkResult.passed ? 'passed' : 'failed'">
                <strong>{{ checkResult.message }}</strong>
                <ul v-if="checkResult.details?.length">
                  <li v-for="(d, i) in checkResult.details" :key="i">{{ d }}</li>
                </ul>
                <div v-if="checkResult.weak_topics?.length" style="margin-top: .35rem; font-size: .78rem;">
                  {{ text.weakTopics }} {{ checkResult.weak_topics.join(', ') }}
                </div>
                <div
                  v-if="checkResult.smart_feedback?.next_actions?.length"
                  class="smart-feedback"
                  :class="`severity-${checkResult.smart_feedback?.severity || 'medium'}`"
                >
                  <div style="display:flex;justify-content:space-between;align-items:center;gap:.5rem;">
                    <strong>{{ text.nextActions }}</strong>
                    <UiButton size="sm" @click="toggleFeedbackMode">
                      {{ feedbackMode === 'brief' ? text.detailed : text.brief }}
                    </UiButton>
                  </div>
                  <ul style="padding-left: 1rem; margin-top: .2rem;">
                    <li
                      v-for="(a, i) in (feedbackMode === 'brief'
                        ? checkResult.smart_feedback.next_actions.slice(0, 2)
                        : checkResult.smart_feedback.next_actions)"
                      :key="i"
                    >
                      {{ a }}
                    </li>
                  </ul>
                  <details v-if="feedbackMode === 'detailed' && checkResult.smart_feedback.failed_steps?.length">
                    <summary>{{ text.failedStepsDetails }}</summary>
                    <ul style="padding-left:1rem; margin-top:.2rem;">
                      <li v-for="(s, i) in checkResult.smart_feedback.failed_steps" :key="i">{{ s }}</li>
                    </ul>
                  </details>
                </div>
                <div v-if="checkGamification" style="margin-top: .35rem; font-size: .78rem;">
                  XP: {{ checkGamification.xp }} · {{ terms.level }}: {{ checkGamification.level }}
                </div>
              </div>
            </details>
            <div
              v-else
              class="check-result"
              :class="checkResult.passed ? 'passed' : 'failed'"
            >
              <strong>{{ checkResult.message }}</strong>
              <ul v-if="checkResult.details?.length">
                <li v-for="(d, i) in checkResult.details" :key="i">{{ d }}</li>
              </ul>
              <div v-if="checkResult.weak_topics?.length" style="margin-top: .35rem; font-size: .78rem;">
                {{ text.weakTopics }} {{ checkResult.weak_topics.join(', ') }}
              </div>
              <div
                v-if="checkResult.smart_feedback?.next_actions?.length"
                class="smart-feedback"
                :class="`severity-${checkResult.smart_feedback?.severity || 'medium'}`"
              >
                <div style="display:flex;justify-content:space-between;align-items:center;gap:.5rem;">
                  <strong>{{ text.nextActions }}</strong>
                  <UiButton size="sm" @click="toggleFeedbackMode">
                    {{ feedbackMode === 'brief' ? text.detailed : text.brief }}
                  </UiButton>
                </div>
                <ul style="padding-left: 1rem; margin-top: .2rem;">
                  <li
                    v-for="(a, i) in (feedbackMode === 'brief'
                      ? checkResult.smart_feedback.next_actions.slice(0, 2)
                      : checkResult.smart_feedback.next_actions)"
                    :key="i"
                  >
                    {{ a }}
                  </li>
                </ul>
                <details v-if="feedbackMode === 'detailed' && checkResult.smart_feedback.failed_steps?.length">
                  <summary>{{ text.failedStepsDetails }}</summary>
                  <ul style="padding-left:1rem; margin-top:.2rem;">
                    <li v-for="(s, i) in checkResult.smart_feedback.failed_steps" :key="i">{{ s }}</li>
                  </ul>
                </details>
              </div>
              <div v-if="checkGamification" style="margin-top: .35rem; font-size: .78rem;">
                XP: {{ checkGamification.xp }} · {{ terms.level }}: {{ checkGamification.level }}
              </div>
            </div>
          </div>

          <div v-if="attemptHistory.length" class="attempt-history">
            <details>
              <summary>{{ text.recentAttempts }} ({{ attemptHistory.length }})</summary>
              <div class="attempt-history-list">
                <div v-for="(item, idx) in attemptHistory" :key="`${item.created_at || idx}`" class="attempt-history-item">
                  <strong>{{ item.passed ? text.attemptPassed : text.attemptFailed }}</strong>
                  <span v-if="item.error_type"> · {{ item.error_type }}</span>
                  <span v-if="item.created_at"> · {{ new Date(item.created_at).toLocaleString('uk-UA') }}</span>
                  <div v-if="item.weak_topics?.length" class="resource-desc">{{ text.weakTopics }} {{ item.weak_topics.join(', ') }}</div>
                  <div v-if="item.feedback" class="resource-desc">{{ item.feedback }}</div>
                </div>
              </div>
            </details>
          </div>

          <div v-if="lessons.solution">
            <details v-if="focusMode" class="panel-accordion-item">
              <summary>📘 {{ text.canonicalSolution }}</summary>
              <div class="solution-panel">
                <pre>{{ lessons.solution }}</pre>
              </div>
            </details>
            <div v-else class="solution-panel">
              <h4>{{ text.canonicalSolution }}</h4>
              <pre>{{ lessons.solution }}</pre>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <HintModal :hint="currentHint" :open="hintOpen" @close="hintOpen = false" />
</template>
