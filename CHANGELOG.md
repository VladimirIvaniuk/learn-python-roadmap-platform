# Changelog

Усі помітні зміни в проєкті фіксуються в цьому файлі.

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

