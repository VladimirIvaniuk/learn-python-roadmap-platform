# Contributing Guide

Thanks for contributing to `learn-python-roadmap-platform`.

## Development principles

- Keep changes small and focused (KISS).
- Avoid duplicated logic and docs (DRY).
- Follow existing architecture and style (consistency first).
- Prefer secure defaults and explicit validation.
- For frontend UI: prefer Tailwind utilities + Headless UI primitives over ad-hoc CSS.

## Setup

1. Clone and enter repository.
2. Create Python virtualenv and install backend deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

3. Install frontend deps:

```bash
cd web/frontend
npm ci
```

## Run locally

Backend:

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
python3 web/run.py
```

Frontend:

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python/web/frontend
npm run dev
```

## Tests

Frontend e2e smoke:

```bash
cd web/frontend
npm run test:e2e
```

Includes route-level smoke and visual snapshot attachments (`routes-smoke.spec.ts`).

Frontend build check:

```bash
cd web/frontend
npm run build
```

## Branch and PR flow

1. Create a branch from `main`:

```bash
git checkout -b <type>/<short-name>
```

2. Commit with clear message:

- `feat: ...`
- `fix: ...`
- `docs: ...`
- `chore: ...`

3. Open PR with:

- concise summary (why this change exists)
- test plan with commands
- screenshots for UI changes

## Review checklist

- No secrets in code, commits, logs, screenshots.
- No unrelated refactors bundled with feature/fix.
- New behavior has test coverage or manual verification notes.
- Docs updated when user-facing behavior changes.
