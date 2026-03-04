import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { i18n } from './i18n'
import './tailwind.css'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.use(router)
app.mount('#app')

const theme = localStorage.getItem('learn_python_theme') || 'dark'
document.documentElement.setAttribute('data-theme', theme)

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {})
}
