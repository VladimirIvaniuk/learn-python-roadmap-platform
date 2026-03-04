<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useLessonsStore } from '../stores/lessons'
import { useUiLanguage } from '../composables/useUiLanguage'

const emit = defineEmits<{ loadExample: [code: string] }>()

const lessons = useLessonsStore()
const { messages } = useUiLanguage()
const text = computed(() => messages.value.lessonBody)
const activeTab = ref('theory')
const noteContent = ref('')
const noteSaved = ref(false)
const exampleLoaded = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null
let exampleLoadedTimer: ReturnType<typeof setTimeout> | null = null

const TABS = computed(() => [
  { id: 'theory', label: text.value.tabTheory },
  { id: 'task', label: text.value.tabTask },
  { id: 'example', label: text.value.tabExample },
  { id: 'notes', label: text.value.tabNotes },
])
const TAB_IDS = ['theory', 'task', 'example', 'notes']

const theoryHtml = computed(() => {
  const content = lessons.currentContent
  if (!content) return ''
  let html = marked.parse(content.theory) as string
  if (content.resources?.length) {
    html +=
      `<div class="lesson-resources"><h4>${text.value.extraResourcesTitle}</h4><ul>` +
      content.resources
        .map(r => `<li><a href="${r.url}" target="_blank" rel="noopener noreferrer">${r.name}</a></li>`)
        .join('') +
      '</ul></div>'
  }
  return DOMPurify.sanitize(html)
})

const taskHtml = computed(() =>
  lessons.currentContent?.task
    ? DOMPurify.sanitize(marked.parse(lessons.currentContent.task) as string)
    : ''
)

watch(
  () => [lessons.currentModule, lessons.currentLesson],
  async ([mod, les]) => {
    activeTab.value = 'theory'
    noteContent.value = ''
    if (mod && les) {
      noteContent.value = await lessons.getNote(mod as string, les as string)
    }
  },
  { immediate: true }
)

function scheduleNoteSave() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(async () => {
    if (!lessons.currentModule || !lessons.currentLesson) return
    await lessons.saveNote(lessons.currentModule, lessons.currentLesson, noteContent.value)
    noteSaved.value = true
    setTimeout(() => { noteSaved.value = false }, 2000)
  }, 800)
}

function loadExample() {
  const ex = lessons.currentContent?.example
  if (!ex) return
  emit('loadExample', ex)
  exampleLoaded.value = true
  if (exampleLoadedTimer) clearTimeout(exampleLoadedTimer)
  exampleLoadedTimer = setTimeout(() => {
    exampleLoaded.value = false
  }, 1600)
}

function switchToTabByIndex(i: number) {
  const id = TAB_IDS[i]
  if (!id) return
  activeTab.value = id
}

function cycleTab(step: 1 | -1) {
  const currentIdx = TAB_IDS.indexOf(activeTab.value)
  const next = (currentIdx + step + TAB_IDS.length) % TAB_IDS.length
  switchToTabByIndex(next)
}

function onTabHotkeys(e: KeyboardEvent) {
  if (!e.altKey) return
  if (e.ctrlKey || e.metaKey) return

  if (e.key >= '1' && e.key <= '4') {
    e.preventDefault()
    switchToTabByIndex(Number(e.key) - 1)
    return
  }

  if (e.key === 'ArrowRight') {
    e.preventDefault()
    cycleTab(1)
    return
  }

  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    cycleTab(-1)
  }
}

onMounted(() => {
  window.addEventListener('keydown', onTabHotkeys)
})

onUnmounted(() => {
  if (saveTimer) clearTimeout(saveTimer)
  if (exampleLoadedTimer) clearTimeout(exampleLoadedTimer)
  window.removeEventListener('keydown', onTabHotkeys)
})
</script>

<template>
  <div class="lesson-body">
    <div class="tabs" :title="text.tabsTitle">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        :data-testid="`lesson-tab-${tab.id}`"
        class="tab"
        :class="{ active: activeTab === tab.id }"
        role="tab"
        :aria-selected="activeTab === tab.id"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </div>

    <div v-if="activeTab === 'theory'" class="tab-content" data-testid="lesson-panel-theory">
      <div class="tab-section-label">{{ text.tabTheory }}</div>
      <div v-if="lessons.currentContent" class="markdown-body" v-html="theoryHtml"></div>
      <div v-else class="no-lesson-msg">
        {{ text.noLessonSelected }}
      </div>
    </div>

    <div v-else-if="activeTab === 'task'" class="tab-content" data-testid="lesson-panel-task">
      <div class="tab-section-label">{{ text.tabTask }}</div>
      <div class="markdown-body" v-html="taskHtml"></div>
    </div>

    <div v-else-if="activeTab === 'example'" class="tab-content" data-testid="lesson-panel-example">
      <div class="tab-section-label">{{ text.tabExample }}</div>
      <div class="example-actions">
        <button class="btn btn-small" data-testid="example-to-editor" @click="loadExample" :title="text.loadExampleToEditor">
          {{ text.toEditor }}
        </button>
        <span v-if="exampleLoaded" data-testid="example-loaded-lesson" class="inline-success">{{ text.exampleLoaded }}</span>
      </div>
      <pre><code>{{ lessons.currentContent?.example || '' }}</code></pre>
    </div>

    <div v-else class="tab-content notes-tab-content" data-testid="lesson-panel-notes">
      <div class="tab-section-label">{{ text.tabNotes }}</div>
      <div class="notes-header">
        <span class="notes-hint">{{ text.notesAutosave }}</span>
        <span v-if="noteSaved" class="save-indicator">{{ text.saved }}</span>
      </div>
      <textarea
        v-model="noteContent"
        class="note-textarea"
        :placeholder="text.notesPlaceholder"
        @input="scheduleNoteSave"
      ></textarea>
    </div>
  </div>
</template>
