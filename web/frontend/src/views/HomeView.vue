<script setup lang="ts">
import { ref, watch, computed, onBeforeUnmount, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'
import LessonBody from '../components/LessonBody.vue'
import CodeEditor from '../components/CodeEditor.vue'
import HintModal from '../components/HintModal.vue'
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
const feedbackMode = ref<'brief' | 'detailed'>((localStorage.getItem('learn_python_feedback_mode') as 'brief' | 'detailed') || 'brief')
const running = ref(false)
const hintOpen = ref(false)
const hintIndex = ref(0)
const leftPaneWidth = ref<number>(52)
const isResizingSplit = ref(false)
const outputCollapsed = ref(false)
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
    timer.start()
  },
  { immediate: true }
)

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
    class="app"
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

    <main class="content">
      <!-- Header -->
      <div class="lesson-header">
        <div>
          <h2>{{ lessonTitle }}</h2>
          <div v-if="metaText" class="lesson-meta">{{ metaText }}</div>
        </div>
        <div class="header-right">
          <button class="btn btn-small" @click="toggleSidebarCollapsed">
            {{ sidebarCollapsed ? text.showMenu : text.hideMenu }}
          </button>
          <span v-if="isCurrentCompleted" style="color: var(--success);">{{ text.completed }}</span>
          <span v-if="lessons.currentLesson" class="timer">⏱ {{ timer.display }}</span>
          <span v-if="progress.streak" class="streak">🔥 {{ progress.streak }}</span>
          <span>{{ progress.completed.length }}/{{ progress.total }}</span>
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
                <button
                  class="btn btn-small"
                  data-testid="hint-button"
                  :disabled="!lessons.currentContent?.hints?.length"
                  @click="showHint"
                >{{ text.hint }}</button>
                <details class="modes-menu">
                  <summary class="btn btn-small" data-testid="modes-menu-trigger">{{ text.modes }}</summary>
                  <div class="modes-popover">
                    <button class="btn btn-small" data-testid="mode-readable" :class="{ 'btn-secondary': readableMode }" @click="toggleReadableMode">
                      {{ readableMode ? text.readableOn : text.readable }}
                    </button>
                    <button class="btn btn-small" data-testid="mode-contrast" :class="{ 'btn-secondary': highContrastMode }" @click="toggleHighContrastMode">
                      {{ highContrastMode ? text.contrastOn : text.contrast }}
                    </button>
                    <button class="btn btn-small" data-testid="mode-fullscreen" :class="{ 'btn-secondary': editorFullscreen }" @click="toggleEditorFullscreen">
                      {{ editorFullscreen ? text.fullscreenExit : text.fullscreen }}
                    </button>
                    <button class="btn btn-small" data-testid="mode-zen" :class="{ 'btn-secondary': zenMode }" @click="toggleZenMode">
                      {{ zenMode ? text.zenOn : text.zen }}
                    </button>
                    <button class="btn btn-small" data-testid="mode-focus" :class="{ 'btn-secondary': focusMode }" @click="toggleFocusMode">
                      {{ focusMode ? text.focusOn : text.focus }}
                    </button>
                  </div>
                </details>
                <button class="btn btn-small" :disabled="running" @click="formatCode">{{ text.format }}</button>
              </div>
              <div class="editor-actions-primary">
                <button class="btn btn-secondary" data-testid="run-button" :disabled="running" @click="runCode">
                  {{ running ? text.running : text.run }}
                </button>
                <button class="btn btn-primary" data-testid="check-button" :disabled="running" @click="checkCode">
                  {{ running ? text.checking : text.check }}
                </button>
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
              <button class="btn btn-small" :disabled="!lessons.currentContent?.example" @click="insertExample">
                {{ text.quickStartLoadExample }}
              </button>
              <button class="btn btn-small" @click="quickStartDismissed = true">
                {{ text.quickStartDismiss }}
              </button>
            </div>
          </div>

          <div v-show="!outputCollapsed" class="output-section">
            <div class="output-header">
              <span>{{ text.result }}</span>
              <button class="btn btn-small" @click="toggleOutputCollapsed">{{ text.collapse }}</button>
            </div>
            <pre :class="['output', { error: outputError }]">{{ output }}</pre>
          </div>
          <div v-show="outputCollapsed" class="output-section output-collapsed">
            <div class="output-header">
              <span>{{ text.resultHidden }}</span>
              <button class="btn btn-small" @click="toggleOutputCollapsed">{{ text.show }}</button>
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
                    <button class="btn btn-small" @click="toggleFeedbackMode">
                      {{ feedbackMode === 'brief' ? text.detailed : text.brief }}
                    </button>
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
                  <button class="btn btn-small" @click="toggleFeedbackMode">
                    {{ feedbackMode === 'brief' ? text.detailed : text.brief }}
                  </button>
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
