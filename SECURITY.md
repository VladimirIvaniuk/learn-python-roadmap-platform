# Security Policy

## Supported versions

This project currently supports security fixes on the latest `main` branch.

## Reporting a vulnerability

Please do not open public issues for security reports.

Send details to repository owner via private channel and include:

- vulnerability type and impact
- exact reproduction steps
- affected files/endpoints
- suggested mitigation (if known)

Target response timeline:

- initial acknowledgement: within 72 hours
- triage decision: within 7 days

## Security baseline in this repository

- JWT authentication with configurable `SECRET_KEY` from `.env`.
- Password hashing via `passlib` (`bcrypt`).
- Backend code execution sandbox protections and timeouts.
- UI HTML sanitization via `DOMPurify` for rendered markdown.
- Dependabot and CodeQL enabled in GitHub.

## Security recommendations for deployment

- Always set a strong custom `SECRET_KEY` in production.
- Restrict file permissions for `web/learn_python.db`.
- Run service behind reverse proxy with HTTPS.
- Keep dependencies updated and review Dependabot PRs promptly.
