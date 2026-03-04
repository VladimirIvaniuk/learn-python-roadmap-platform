import { computed, ref } from 'vue'
import {
  DEFAULT_UI_LANGUAGE,
  getStoredUiLanguage,
  setStoredUiLanguage,
  type UiLanguage,
  UI_I18N,
} from '../i18n/ui'
import { i18n } from '../i18n'

const currentLanguage = ref<UiLanguage>(DEFAULT_UI_LANGUAGE)
let initialized = false

function ensureInitialized() {
  if (initialized) return
  currentLanguage.value = getStoredUiLanguage()
  i18n.global.locale.value = currentLanguage.value
  initialized = true
}

export function useUiLanguage() {
  ensureInitialized()

  const messages = computed(() => i18n.global.getLocaleMessage(currentLanguage.value) as typeof UI_I18N.uk)

  function setLanguage(lang: UiLanguage) {
    currentLanguage.value = lang
    i18n.global.locale.value = lang
    setStoredUiLanguage(lang)
  }

  function toggleLanguage() {
    setLanguage(currentLanguage.value === 'uk' ? 'en' : 'uk')
  }

  return {
    language: currentLanguage,
    messages,
    setLanguage,
    toggleLanguage,
  }
}
