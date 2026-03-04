"""
Senior 5 — Приклади: безпека

pip install bcrypt PyJWT
"""
import hashlib
import hmac
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any


# ── Хешування паролів ─────────────────────────────────────────────────────────
print("=== Хешування паролів ===")

# ❌ MD5 — НЕ для паролів
md5_hash = hashlib.md5(b"password123").hexdigest()
print(f"MD5 (UNSAFE): {md5_hash}")
print("  Причина: дуже швидкий → брутфорс ~10 млрд хешів/сек на GPU!")

# ✅ bcrypt — повільний за дизайном
try:
    import bcrypt
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)   # 2^12 = 4096 ітерацій, ~0.3с
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    hashed = hash_password("my_secure_pass_1")
    print(f"\nbcrypt hash: {hashed[:30]}...")
    print(f"verify correct: {verify_password('my_secure_pass_1', hashed)}")
    print(f"verify wrong:   {verify_password('wrong_password', hashed)}")

except ImportError:
    print("  pip install bcrypt (для реального проєкту)")

# Власна реалізація з PBKDF2 (вбудований у Python)
def hash_password_pbkdf2(password: str) -> str:
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"pbkdf2:{salt}:{key.hex()}"

def verify_password_pbkdf2(plain: str, stored: str) -> bool:
    _, salt, key_hex = stored.split(":")
    key = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(key.hex(), key_hex)   # constant-time comparison!

hashed_pbkdf2 = hash_password_pbkdf2("my_secure_pass_1")
print(f"\nPBKDF2: {verify_password_pbkdf2('my_secure_pass_1', hashed_pbkdf2)} (correct)")
print(f"PBKDF2: {verify_password_pbkdf2('wrong', hashed_pbkdf2)} (wrong)")


# ── JWT (без зовнішніх бібліотек для демо) ────────────────────────────────────
print("\n=== JWT Демо ===")
import base64, json

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)

def create_jwt(payload: dict[str, Any], secret: str) -> str:
    header = b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64url_encode(json.dumps(payload).encode())
    sig_input = f"{header}.{body}".encode()
    sig = hmac.new(secret.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{body}.{b64url_encode(sig)}"

def verify_jwt(token: str, secret: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")
    header, payload_b64, sig_b64 = parts
    expected_sig = hmac.new(
        secret.encode(), f"{header}.{payload_b64}".encode(), hashlib.sha256
    ).digest()
    if not hmac.compare_digest(b64url_decode(sig_b64), expected_sig):
        raise ValueError("Invalid signature!")
    payload = json.loads(b64url_decode(payload_b64))
    if payload.get("exp") and time.time() > payload["exp"]:
        raise ValueError("Token expired!")
    return payload

SECRET = "my-secret-key"
now = int(time.time())
token = create_jwt({"sub": "42", "iat": now, "exp": now + 3600, "role": "admin"}, SECRET)
print(f"Token: {token[:50]}...")

payload = verify_jwt(token, SECRET)
print(f"Payload: {payload}")

# Демонстрація: payload видно без ключа!
raw_payload = json.loads(b64url_decode(token.split(".")[1]))
print(f"Payload без ключа: {raw_payload}")
print("  → НІКОЛИ не клади секрети в JWT payload!")


# ── SQL Injection Demo ────────────────────────────────────────────────────────
print("\n=== SQL Injection ===")

import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'alice', 'SECRET_DATA')")
conn.execute("INSERT INTO users VALUES (2, 'bob', 'OTHER_SECRET')")
conn.commit()

def unsafe_get_user(username: str) -> list:
    query = f"SELECT id, username FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()

def safe_get_user(username: str) -> list:
    return conn.execute(
        "SELECT id, username FROM users WHERE username = ?",
        (username,)
    ).fetchall()

print(f"Safe query: {safe_get_user('alice')}")
print(f"Injection attempt on safe: {safe_get_user(\"' OR '1'='1\")}")
print(f"Injection attempt UNSAFE: {unsafe_get_user(\"' OR '1'='1\")}")
print("  → ВРАЗЛИВО! Повертає всіх користувачів")


# ── Input Validation ──────────────────────────────────────────────────────────
print("\n=== Input Validation ===")

def safe_filename(filename: str) -> str:
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError(f"Path traversal attempt: {filename!r}")
    cleaned = re.sub(r"[^\w\-. ]", "", filename)
    if not cleaned:
        raise ValueError("Empty filename after sanitization")
    return cleaned

for name in ["report.pdf", "../../etc/passwd", "file<script>.txt", "normal_file_2026.csv"]:
    try:
        safe = safe_filename(name)
        print(f"  ✅ '{name}' → '{safe}'")
    except ValueError as e:
        print(f"  ❌ Blocked: {e}")


# ── Secrets Management ────────────────────────────────────────────────────────
print("\n=== Secrets ===")
# secrets модуль — криптографічно безпечний генератор
token = secrets.token_urlsafe(32)
api_key = secrets.token_hex(16)
print(f"  Token: {token}")
print(f"  API key: {api_key}")
print("  → Зберігай тільки в .env або secrets manager!")
