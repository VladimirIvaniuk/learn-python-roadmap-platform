import { createI18n } from 'vue-i18n'
import { DEFAULT_UI_LANGUAGE, getStoredUiLanguage, UI_I18N, type UiLanguage } from './ui'

const initialLocale: UiLanguage =
  typeof window === 'undefined' ? DEFAULT_UI_LANGUAGE : getStoredUiLanguage()

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: DEFAULT_UI_LANGUAGE,
  messages: UI_I18N,
})
