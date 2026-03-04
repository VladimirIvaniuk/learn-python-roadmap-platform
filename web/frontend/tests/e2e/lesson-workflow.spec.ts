import { expect, test } from '@playwright/test'

const LESSON_PATH = '/lesson/01_basics/lesson_04_functions'

async function mockApi(page: import('@playwright/test').Page) {
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url())
    const path = url.pathname
    const method = route.request().method()

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
    localStorage.clear()
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
