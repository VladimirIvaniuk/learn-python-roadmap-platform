<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUiLanguage } from '../composables/useUiLanguage'

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
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <h1>🐍 Learn Python</h1>
        <p>{{ text.subtitle }}</p>
      </div>

      <div class="login-tabs">
        <button data-testid="login-tab-login" :class="{ active: isLogin }" @click="isLogin = true">{{ text.loginTab }}</button>
        <button data-testid="login-tab-register" :class="{ active: !isLogin }" @click="isLogin = false">{{ text.registerTab }}</button>
      </div>

      <form @submit.prevent="submit">
        <div class="form-group">
          <label>{{ text.email }}</label>
          <input v-model="email" data-testid="login-email" type="email" required autocomplete="email" placeholder="your@email.com" />
        </div>

        <div v-if="!isLogin" class="form-group">
          <label>{{ text.username }}</label>
          <input v-model="username" data-testid="login-username" type="text" required placeholder="pythonist" />
        </div>

        <div class="form-group">
          <label>{{ text.password }}</label>
          <input v-model="password" data-testid="login-password" type="password" required autocomplete="current-password" placeholder="••••••••" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" data-testid="login-submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? '…' : (isLogin ? text.loginButton : text.registerButton) }}
        </button>
      </form>

      <p class="login-note">{{ text.progressNote }}</p>
      <RouterLink :to="returnTarget" data-testid="login-guest-link" class="back-link">{{ text.guestMode }}</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}
.login-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.login-logo { text-align: center; margin-bottom: 1.5rem; }
.login-logo h1 { margin: 0; color: var(--accent); font-size: 1.5rem; }
.login-logo p { margin: 0.25rem 0 0; color: var(--text-secondary); font-size: 0.9rem; }

.login-tabs {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 1.5rem;
}
.login-tabs button {
  flex: 1; padding: 0.5rem;
  border: none; background: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer; font-size: 0.9rem;
  transition: all 0.2s;
}
.login-tabs button.active { background: var(--accent); color: #0d1117; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; margin-bottom: 0.4rem; color: var(--text-secondary); }
.form-group input {
  width: 100%; padding: 0.6rem 0.75rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem; box-sizing: border-box;
  outline: none; transition: border-color 0.2s;
}
.form-group input:focus { border-color: var(--accent); }

.error-msg { color: var(--error); font-size: 0.85rem; margin-bottom: 1rem; }
.login-note {
  margin: 0.85rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.35;
}
.btn-full { width: 100%; margin-top: 0.25rem; }
.back-link {
  display: block; text-align: center;
  margin-top: 1rem; color: var(--text-secondary);
  font-size: 0.82rem; text-decoration: none;
}
.back-link:hover { color: var(--accent); }
</style>
