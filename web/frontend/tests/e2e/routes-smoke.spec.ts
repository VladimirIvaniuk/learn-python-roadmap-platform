import { expect, test } from '@playwright/test'

const LESSON_PATH = '/lesson/01_basics/lesson_04_functions'

async function mockApi(page: import('@playwright/test').Page) {
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url())
    const path = url.pathname
    const method = route.request().method()
    const auth = route.request().headers()['authorization']

    if (path === '/api/auth/me') {
      if (auth?.startsWith('Bearer ')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user_id: 1, email: 'user@example.com', username: 'Test User' }),
        })
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Unauthorized' }),
        })
      }
      return
    }

    if (path === '/api/progress') {
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ completed: [], total: 12, by_level: { junior: { done: 0, total: 12 } } }),
        })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
      return
    }

    if (path === '/api/adaptive/summary') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          weak_topics: [{ topic: 'functions', count: 2 }],
          reviews_due_count: 2,
          reviews_due: [
            { module_id: '01_basics', lesson_id: 'lesson_04_functions', topic: 'functions', overdue: true, due_at: null },
          ],
          next_lesson: { module_id: '01_basics', lesson_id: 'lesson_05_strings', reason: 'Continue flow', score: 98 },
          next_lessons: [{ module_id: '01_basics', lesson_id: 'lesson_05_strings', title: 'Strings', reason: 'Continue flow', score: 98 }],
          gamification: { xp: 120, level: 2, badges: ['Starter'], goal_preset: 'balanced' },
          skill_map: { functions: { done: 1, total: 3, percent: 33 } },
          skill_lesson_matrix: {
            functions: [{ module_id: '01_basics', lesson_id: 'lesson_04_functions', title: 'Functions', done: true }],
          },
          quests: { daily: [{ id: 'd1', title: 'Solve one lesson', target: 1, progress: 0, done: false }], weekly: [] },
        }),
      })
      return
    }

    if (path === '/api/levels') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ junior: { modules: [{ id: '01_basics' }] }, middle: { modules: [] }, senior: { modules: [] } }),
      })
      return
    }

    if (path === '/api/lessons/01_basics') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          module: 'Основи Python',
          lessons: [
            { id: 'lesson_04_functions', title: 'Урок 4 — Функції' },
            { id: 'lesson_05_strings', title: 'Урок 5 — Рядки' },
          ],
        }),
      })
      return
    }

    if (path === '/api/lessons/01_basics/lesson_04_functions') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          theory: '# Теорія\n\nФункції допомагають уникати дублювання коду.',
          task: '## Завдання\n\nНапиши функцію `add(a, b)`.',
          example: 'def add(a, b):\n    return a + b',
          resources: [{ name: 'Python Docs', url: 'https://docs.python.org/3/' }],
          hints: ['Почни з `def add(a, b):`'],
          meta: { difficulty: 'easy', time: '20 хв', prev: null, next: 'lesson_05_strings' },
        }),
      })
      return
    }

    if (path === '/api/stats') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_completed: 4,
          total_lessons: 12,
          total_time_seconds: 5400,
          by_level: { junior: { done: 4, total: 12 } },
          daily_activity: {},
          lesson_times: [{ module_id: '01_basics', lesson_id: 'lesson_04_functions', time_spent: 240, completed_at: '2026-02-10T00:00:00Z' }],
        }),
      })
      return
    }

    if (path === '/api/review/queue') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { module_id: '01_basics', lesson_id: 'lesson_04_functions', topic: 'functions', overdue: true, due_at: null },
            { module_id: '01_basics', lesson_id: 'lesson_05_strings', topic: 'strings', overdue: false, due_at: '2026-03-06T10:00:00Z' },
          ],
        }),
      })
      return
    }

    if (path === '/api/review/complete' || path === '/api/review/session') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, processed: 1, successes: 1, bonus_xp: 5, xp: 125, level: 2 }) })
      return
    }

    if (path === '/api/plan/weekly') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          preset: 'balanced',
          generated_at: '2026-03-04T12:00:00Z',
          days: [
            {
              day_index: 1,
              date: '2026-03-04',
              focus: 'Functions',
              estimated_minutes: 45,
              progress: { done: 0, total: 2 },
              tasks: [{ task_key: 'lesson:01_basics:lesson_04_functions', type: 'lesson', title: 'Functions', lesson_id: 'lesson_04_functions', status: 'pending' }],
            },
          ],
        }),
      })
      return
    }

    if (path === '/api/plan/task-action') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      return
    }

    if (path === '/api/code' || path === '/api/notes') {
      if (method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: '', content: '' }) })
      } else {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      }
      return
    }

    if (path === '/api/lessons/search') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) })
      return
    }

    if (path === '/api/attempts') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) })
      return
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
  await page.addInitScript(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
})

test('guest routes smoke + visual snapshots', async ({ page }) => {
  await page.goto('/login')
  await expect(page.locator('button[type="submit"]').first()).toBeVisible()
  await test.info().attach('route-login', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })

  await page.goto('/resources')
  await expect(page.getByRole('heading').first()).toBeVisible()
  await test.info().attach('route-resources', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })
})

test('workspace/auth routes smoke + visual snapshots', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, email: 'user@example.com', username: 'Test User' }))
  })

  await page.goto('/')
  await expect(page.getByTestId('run-button')).toBeVisible()
  await test.info().attach('route-home', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })

  await page.goto(LESSON_PATH)
  await expect(page.getByTestId('lesson-tab-theory')).toBeVisible()
  await test.info().attach('route-lesson', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })

  await page.goto('/stats')
  await expect(page.getByText(/статистика|stats|learning/i)).toBeVisible()
  await test.info().attach('route-stats', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })

  await page.goto('/review')
  await expect(page.getByRole('heading').first()).toBeVisible()
  await test.info().attach('route-review', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })

  await page.goto('/plan')
  await expect(page.getByRole('heading').first()).toBeVisible()
  await test.info().attach('route-plan', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  })
})
