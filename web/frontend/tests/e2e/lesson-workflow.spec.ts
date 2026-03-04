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
          body: JSON.stringify({ user_id: 1, email: 'user@example.com' }),
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

    if (path === '/api/auth/login' || path === '/api/auth/register') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          token: 'test-token',
          user: { id: 1, email: 'user@example.com', username: 'Test User' },
        }),
      })
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
          weak_topics: [],
          reviews_due_count: 0,
          reviews_due: [],
          next_lesson: null,
          next_lessons: [],
          gamification: { xp: 0, level: 1, badges: [], goal_preset: 'balanced' },
          skill_map: {},
          skill_lesson_matrix: {},
          quests: { daily: [], weekly: [] },
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
          example: 'def add(a, b):\n    return a + b\n\nprint(add(2, 3))',
          resources: [{ name: 'Python Docs', url: 'https://docs.python.org/3/' }],
          hints: ['Почни з `def add(a, b):`'],
          meta: { difficulty: 'easy', time: '20 хв', prev: null, next: 'lesson_05_strings' },
        }),
      })
      return
    }

    if (path === '/api/code') {
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ code: '' }),
        })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      return
    }

    if (path === '/api/notes') {
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ content: '' }),
        })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      return
    }

    if (path === '/api/run') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, output: '5', error: '' }),
      })
      return
    }

    if (path === '/api/check') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          passed: false,
          message: 'Поки не пройдено',
          details: ['Перевір функцію add'],
          smart_feedback: { severity: 'medium', next_actions: ['Додай return', 'Перевір виклик функції'] },
        }),
      })
      return
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
  await page.addInitScript(() => {
    if (!sessionStorage.getItem('__e2e_storage_cleared__')) {
      localStorage.clear()
      sessionStorage.setItem('__e2e_storage_cleared__', '1')
    }
  })
})

test('tabs stay aligned with visible panel', async ({ page }) => {
  await page.goto(LESSON_PATH)

  const cases = [
    { tab: 'theory', panel: 'theory' },
    { tab: 'task', panel: 'task' },
    { tab: 'example', panel: 'example' },
    { tab: 'notes', panel: 'notes' },
  ] as const

  for (const c of cases) {
    await page.getByTestId(`lesson-tab-${c.tab}`).click()
    await expect(page.getByTestId(`lesson-panel-${c.panel}`)).toBeVisible()
    for (const other of cases.filter(x => x.panel !== c.panel)) {
      await expect(page.getByTestId(`lesson-panel-${other.panel}`)).toHaveCount(0)
    }
  }
})

test('modes toggles are clickable', async ({ page }) => {
  await page.goto(LESSON_PATH)

  await page.getByTestId('modes-menu-trigger').click()
  await page.getByTestId('mode-readable').click()
  await page.getByTestId('mode-contrast').click()
  await page.getByTestId('mode-zen').click()
  await page.getByTestId('mode-focus').click()
  await page.getByTestId('mode-fullscreen').click()
  await page.keyboard.press('Escape')

  await expect(page.getByTestId('run-button')).toBeVisible()
})

test('example loads into editor with visible feedback', async ({ page }) => {
  await page.goto(LESSON_PATH)

  await page.getByTestId('lesson-tab-example').click()
  await page.getByTestId('example-to-editor').click()

  await expect(
    page.locator('[data-testid="example-loaded-home"], [data-testid="example-loaded-lesson"]').first()
  ).toBeVisible()
})

test('next-step primary action opens next lesson', async ({ page }) => {
  await page.goto(LESSON_PATH)

  await expect(page.getByTestId('next-step-primary')).toBeVisible()
  await page.getByTestId('next-step-primary').click()
  await expect(page).toHaveURL(/\/lesson\/01_basics\/lesson_05_strings$/)
})

test('user can sign in from login page', async ({ page }) => {
  await page.goto('/login')

  await page.locator('input[type="email"]:visible').first().fill('user@example.com')
  await page.locator('input[type="password"]:visible').first().fill('secret123')
  await page.locator('button:visible').filter({ hasText: /Увійти|Sign in/i }).first().click()

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByTestId('sidebar-user-name')).toContainText('Test User')
  await expect
    .poll(async () => page.evaluate(() => localStorage.getItem('token')))
    .toBe('test-token')
})

test('login from lesson keeps return path', async ({ page }) => {
  await page.goto(LESSON_PATH)
  await page.getByTestId('sidebar-login-link').click()
  await expect(page).toHaveURL(/\/login\?returnTo=/)

  await page.locator('input[type="email"]:visible').first().fill('user@example.com')
  await page.locator('input[type="password"]:visible').first().fill('secret123')
  await page.locator('button:visible').filter({ hasText: /Увійти|Sign in/i }).first().click()

  await expect(page).toHaveURL(/\/lesson\/01_basics\/lesson_04_functions$/)
})

test('language toggle updates UI and persists after reload', async ({ page }) => {
  await page.goto(LESSON_PATH)

  await expect(page.getByTestId('run-button')).toContainText('Запустити')
  await page.getByTestId('language-toggle').click()
  await expect(page.getByTestId('run-button')).toContainText('Run')

  await page.reload()
  await expect(page.getByTestId('run-button')).toContainText('Run')
  await expect
    .poll(async () => page.evaluate(() => localStorage.getItem('learn_python_ui_lang')))
    .toBe('en')
})

test('guest-mode link returns user to learning workspace', async ({ page }) => {
  await page.goto('/login')
  await page.getByRole('link', { name: /Без авторизації|Continue as guest|На головну/i }).click()
  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByTestId('run-button')).toBeVisible()
})
