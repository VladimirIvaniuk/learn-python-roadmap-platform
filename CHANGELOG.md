# Changelog

Усі помітні зміни в проєкті фіксуються в цьому файлі.

## [v0.1.1] - 2026-03-04

### Added

- У lesson workflow додано блок `What next`/`Що далі` з action-кнопками:
  - `Next lesson`,
  - `To plan`,
  - `To review`.
- Додано server-side пошук уроків з фільтрами:
  - endpoint `GET /api/lessons/search`,
  - фільтри за `level`, `difficulty`, `topic`, `max_time`, `q`.
- Додано endpoint історії спроб користувача:
  - `GET /api/attempts` для останніх перевірок по уроку.
- У lesson UI додано відображення `Recent attempts`.
- Розширено e2e smoke тести для нових сценаріїв:
  - next-step navigation,
  - login return path,
  - оновлені auth/navigation перевірки.

### Changed

- Покращено auth/guest UX:
  - login зберігає `returnTo`,
  - після авторизації користувач повертається до останнього контексту.
- Уніфіковано user-facing error/retry стани в `Home`, `Review`, `Plan`, `Stats`.
- Розширено i18n словники (UA/EN) під нові UX сценарії.

### Quality

- Пройдено frontend build (`vue-tsc + vite build`).
- Пройдено Playwright e2e suite (8/8).
- Перевірено Python syntax для backend (`py_compile`).

## [v0.1.0] - 2026-03-04

### Added

- Базова інфраструктура GitHub для командної роботи:
  - `CI` workflow (build + e2e smoke),
  - `CodeQL` security scanning,
  - `Dependabot`,
  - авто-triage labels.
- Захист гілки `main` з обов'язковими status checks.
- Шаблони для GitHub процесів:
  - `ISSUE_TEMPLATE` (bug/feature),
  - `pull_request_template.md`,
  - `CODEOWNERS`.
- Повна документація запуску і розгортання:
  - оновлений root `README.md`,
  - детальний `web/README.md` (dev/prod/systemd/nginx/DB),
  - `CONTRIBUTING.md`,
  - `SECURITY.md`,
  - `docs/ops/runbook.md`.
- Розширені e2e smoke тести (Playwright):
  - стабільність lesson tabs,
  - editor modes interactivity,
  - example-to-editor feedback,
  - login flow,
  - language toggle persistence,
  - guest navigation flow.

### Changed

- Покращено UX і стабільність інтерфейсу (локалізація, режими відображення, підказки, структурування панелей).
- Централізовано i18n (UA/EN) через `vue-i18n`.
- Посилено безпеку рендеру lesson контенту через `DOMPurify`.

### Security

- Ввімкнено автоматичне security-сканування через CodeQL.
- Документовано політику security disclosure в `SECURITY.md`.

