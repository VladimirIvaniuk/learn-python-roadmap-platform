<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUiLanguage } from '../composables/useUiLanguage'
import UiButton from '../components/ui/UiButton.vue'
import UiInput from '../components/ui/UiInput.vue'
import UiAlert from '../components/ui/UiAlert.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isLogin = ref(true)
const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const { messages } = useUiLanguage()
const text = computed(() => messages.value.login)
const returnTarget = computed(() => {
  const fromQuery = typeof route.query.returnTo === 'string' ? route.query.returnTo : ''
  if (fromQuery.startsWith('/')) return fromQuery
  return localStorage.getItem('learn_python_last_lesson_path') || '/'
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const endpoint = isLogin.value ? '/api/auth/login' : '/api/auth/register'
    const body = isLogin.value
      ? { email: email.value, password: password.value }
      : { email: email.value, username: username.value, password: password.value }

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      error.value = data.detail || (isLogin.value ? messages.value.errors.invalidCredentials : messages.value.errors.registrationFailed)
      return
    }

    const data = await res.json()
    auth.setAuth(data.token, data.user)
    router.push(returnTarget.value)
  } catch {
    error.value = messages.value.errors.networkWithRetry
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="lp-page flex min-h-screen items-center justify-center p-4">
    <div class="w-full max-w-md rounded-2xl border border-border bg-bg-secondary p-6 shadow-xl">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-accent">🐍 Learn Python</h1>
        <p class="mt-1 text-sm text-text-secondary">{{ text.subtitle }}</p>
      </div>

      <div class="mb-6 grid grid-cols-2 rounded-lg bg-bg-tertiary p-1">
        <button
          data-testid="login-tab-login"
          class="rounded-md px-3 py-2 text-sm transition"
          :class="isLogin ? 'bg-accent text-white' : 'text-text-secondary hover:text-text-primary'"
          @click="isLogin = true"
        >
          {{ text.loginTab }}
        </button>
        <button
          data-testid="login-tab-register"
          class="rounded-md px-3 py-2 text-sm transition"
          :class="!isLogin ? 'bg-accent text-white' : 'text-text-secondary hover:text-text-primary'"
          @click="isLogin = false"
        >
          {{ text.registerTab }}
        </button>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1">
          <label class="text-xs text-text-secondary">{{ text.email }}</label>
          <UiInput v-model="email" data-testid="login-email" type="email" required autocomplete="email" placeholder="your@email.com" />
        </div>

        <div v-if="!isLogin" class="space-y-1">
          <label class="text-xs text-text-secondary">{{ text.username }}</label>
          <UiInput v-model="username" data-testid="login-username" type="text" required autocomplete="username" placeholder="pythonist" />
        </div>

        <div class="space-y-1">
          <label class="text-xs text-text-secondary">{{ text.password }}</label>
          <UiInput v-model="password" data-testid="login-password" type="password" required autocomplete="current-password" placeholder="••••••••" />
        </div>

        <UiAlert v-if="error" variant="error">
          <span>{{ error }}</span>
        </UiAlert>

        <UiButton type="submit" variant="primary" size="md" class="w-full" data-testid="login-submit" :disabled="loading">
          {{ loading ? '…' : (isLogin ? text.loginButton : text.registerButton) }}
        </UiButton>
      </form>

      <p class="mt-4 text-xs leading-5 text-text-secondary">{{ text.progressNote }}</p>
      <RouterLink
        :to="returnTarget"
        data-testid="login-guest-link"
        class="mt-4 block text-center text-xs text-text-secondary transition hover:text-accent"
      >
        {{ text.guestMode }}
      </RouterLink>
    </div>
  </div>
</template>
