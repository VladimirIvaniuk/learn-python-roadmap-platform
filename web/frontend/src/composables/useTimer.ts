import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'

export function useTimer() {
  const auth = useAuthStore()
  const elapsed = ref(0)
  const display = ref('00:00')

  let interval: ReturnType<typeof setInterval> | null = null

  function start() {
    stop()
    const startTime = Date.now() - elapsed.value * 1000
    interval = setInterval(() => {
      elapsed.value = Math.floor((Date.now() - startTime) / 1000)
      const m = String(Math.floor(elapsed.value / 60)).padStart(2, '0')
      const s = String(elapsed.value % 60).padStart(2, '0')
      display.value = `${m}:${s}`
    }, 1000)
  }

  function stop() {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  function reset() {
    stop()
    elapsed.value = 0
    display.value = '00:00'
  }

  async function flush(moduleId: string, lessonId: string) {
    const secs = elapsed.value
    if (secs < 5 || !auth.isLoggedIn) return
    try {
      await fetch('/api/time', {
        method: 'POST',
        headers: auth.authHeaders(),
        body: JSON.stringify({ module_id: moduleId, lesson_id: lessonId, seconds: secs }),
      })
    } catch {
      // silent — non-critical
    }
  }

  onUnmounted(stop)

  return { elapsed, display, start, stop, reset, flush }
}
