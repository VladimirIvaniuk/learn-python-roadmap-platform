# Operations Runbook

This runbook covers routine operations for `learn-python-roadmap-platform`.

## 1) Service health checks

API quick check:

```bash
curl -sSf http://127.0.0.1:8000/api/levels > /dev/null && echo "API OK"
```

Frontend availability (when served by backend build):

```bash
curl -sSf http://127.0.0.1:8000/ > /dev/null && echo "WEB OK"
```

## 2) Logs and process checks

If running via systemd:

```bash
sudo systemctl status learn-python
sudo journalctl -u learn-python -n 200 --no-pager
```

If running manually:

- check the terminal running `uvicorn`
- verify port usage with `lsof -i :8000`

## 3) Database operations (SQLite)

Database file:

- `web/learn_python.db`

List tables:

```bash
sqlite3 web/learn_python.db ".tables"
```

Quick user count:

```bash
sqlite3 web/learn_python.db "SELECT COUNT(*) FROM users;"
```

## 4) Backup procedure

Create backup:

```bash
mkdir -p web/backups
sqlite3 web/learn_python.db ".backup 'web/backups/learn_python-$(date +%F-%H%M).db'"
```

Verify backup exists:

```bash
ls -lh web/backups
```

## 5) Restore procedure

1. Stop service.
2. Restore file.
3. Start service.
4. Verify API health.

```bash
sudo systemctl stop learn-python
cp web/backups/<backup-file>.db web/learn_python.db
sudo systemctl start learn-python
curl -sSf http://127.0.0.1:8000/api/levels > /dev/null && echo "API OK"
```

## 6) Deployment update checklist

1. Pull latest code.
2. Install backend deps if changed.
3. Build frontend.
4. Restart service.
5. Run smoke checks.

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
cd web/frontend && npm ci && npm run build
cd ../..
sudo systemctl restart learn-python
curl -sSf http://127.0.0.1:8000/api/levels > /dev/null && echo "API OK"
```

## 7) Rollback steps

If latest deploy is unstable:

1. checkout previous known-good commit/tag
2. rebuild frontend
3. restart service
4. restore DB backup if data migration broke behavior

Prefer a tagged release process to make rollback deterministic.
