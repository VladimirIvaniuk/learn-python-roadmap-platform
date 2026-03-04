<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, keymap, lineNumbers, drawSelection, highlightActiveLine, placeholder } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { defaultKeymap, historyKeymap, history, indentWithTab } from '@codemirror/commands'
import { syntaxHighlighting, defaultHighlightStyle, bracketMatching } from '@codemirror/language'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { useUiLanguage } from '../composables/useUiLanguage'

const props = defineProps<{
  modelValue: string
  theme?: string
  onRun: () => void
  onCheck: () => void
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const containerEl = ref<HTMLElement>()
let view: EditorView | null = null
let ignoreNext = false
const { messages, language } = useUiLanguage()

function buildExtensions() {
  return [
    history(),
    lineNumbers(),
    drawSelection(),
    highlightActiveLine(),
    bracketMatching(),
    syntaxHighlighting(defaultHighlightStyle),
    python(),
    placeholder(messages.value.home.editorPlaceholder),
    ...(props.theme !== 'light' ? [oneDark] : []),
    EditorView.theme({
      '&': { fontSize: '14px', height: '100%' },
      '.cm-scroller': { fontFamily: "'Monaco', 'Menlo', 'Fira Code', monospace", overflow: 'auto' },
    }),
    keymap.of([
      ...defaultKeymap,
      ...historyKeymap,
      indentWithTab,
      { key: 'Ctrl-Enter', mac: 'Cmd-Enter', run: () => { props.onRun(); return true } },
      { key: 'Ctrl-Shift-Enter', mac: 'Cmd-Shift-Enter', run: () => { props.onCheck(); return true } },
    ]),
    EditorView.updateListener.of(update => {
      if (update.docChanged && !ignoreNext) {
        emit('update:modelValue', update.state.doc.toString())
      }
    }),
  ]
}

onMounted(() => {
  if (!containerEl.value) return
  view = new EditorView({
    state: EditorState.create({ doc: props.modelValue, extensions: buildExtensions() }),
    parent: containerEl.value,
  })
})

onUnmounted(() => {
  view?.destroy()
  view = null
})

watch(() => props.modelValue, val => {
  if (!view) return
  const current = view.state.doc.toString()
  if (current !== val) {
    ignoreNext = true
    view.dispatch({ changes: { from: 0, to: current.length, insert: val } })
    ignoreNext = false
  }
})

watch(() => props.theme, () => {
  if (!view) return
  const doc = view.state.doc.toString()
  view.setState(EditorState.create({ doc, extensions: buildExtensions() }))
})

watch(() => language.value, () => {
  if (!view) return
  const doc = view.state.doc.toString()
  view.setState(EditorState.create({ doc, extensions: buildExtensions() }))
})
</script>

<template>
  <div ref="containerEl" class="cm-editor-wrap"></div>
</template>
