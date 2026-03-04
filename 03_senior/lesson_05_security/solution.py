"""
Розв'язки — Security (Senior)
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import os
import re
import secrets
import time
import json
from dataclasses import dataclass, field
from typing import Any

# ── Завдання 1 — TokenService (JWT-like) ─────────────────────────────────────
class TokenService:
    ALGORITHM = "HS256"
    ACCESS_TTL  = 900       # 15 хвилин
    REFRESH_TTL = 604_800   # 7 днів

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()
        self._revoked: set[str] = set()

    def _sign(self, payload: dict) -> str:
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": self.ALGORITHM, "typ": "JWT"}).encode()
        ).rstrip(b"=").decode()

        body = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b"=").decode()

        sig = hmac.new(
            self._secret,
            f"{header}.{body}".encode(),
            hashlib.sha256,
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        return f"{header}.{body}.{sig_b64}"

    def create_access_token(self, user_id: str, role: str = "user") -> str:
        jti = secrets.token_hex(16)
        payload = {
            "sub": user_id,
            "role": role,
            "jti": jti,
            "type": "access",
            "iat": int(time.time()),
            "exp": int(time.time()) + self.ACCESS_TTL,
        }
        return self._sign(payload)

    def create_refresh_token(self, user_id: str) -> str:
        payload = {
            "sub": user_id,
            "jti": secrets.token_hex(16),
            "type": "refresh",
            "iat": int(time.time()),
            "exp": int(time.time()) + self.REFRESH_TTL,
        }
        return self._sign(payload)

    def verify(self, token: str) -> dict:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        header_b64, body_b64, sig_b64 = parts
        expected_sig = hmac.new(
            self._secret,
            f"{header_b64}.{body_b64}".encode(),
            hashlib.sha256,
        ).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b"=").decode()

        if not secrets.compare_digest(sig_b64, expected_b64):
            raise ValueError("Invalid signature")

        payload = json.loads(base64.urlsafe_b64decode(body_b64 + "=="))
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        if payload.get("jti") in self._revoked:
            raise ValueError("Token revoked")

        return payload

    def revoke(self, token: str) -> None:
        try:
            payload = self.verify(token)
            self._revoked.add(payload["jti"])
        except ValueError:
            pass  # вже інвалідний

svc = TokenService(secret=secrets.token_hex(32))
access = svc.create_access_token("user-42", role="admin")
refresh = svc.create_refresh_token("user-42")

print(f"Access token (трокати): {access[:40]}...")
payload = svc.verify(access)
print(f"Payload: sub={payload['sub']}, role={payload['role']}, type={payload['type']}")

svc.revoke(access)
try:
    svc.verify(access)
except ValueError as e:
    print(f"Revoked: {e}")

# ── Завдання 2 — PasswordPolicy ──────────────────────────────────────────────
COMMON_PASSWORDS = {"password", "12345678", "qwerty123", "password123"}

@dataclass
class PasswordPolicy:
    min_length: int = 12
    require_uppercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()-_=+[]{}|;':\",./<>?"

    def validate(self, password: str) -> list[str]:
        errors: list[str] = []
        if password.lower() in COMMON_PASSWORDS:
            errors.append("Пароль занадто поширений")
        if len(password) < self.min_length:
            errors.append(f"Мінімум {self.min_length} символів")
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Потрібна велика літера")
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("Потрібна цифра")
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append("Потрібен спецсимвол")
        return errors

    def is_valid(self, password: str) -> bool:
        return not self.validate(password)

policy = PasswordPolicy()
for pw in ["weak", "StrongPass1!", "password", "Secur3!Pass#2026"]:
    errors = policy.validate(pw)
    status = "✓" if not errors else f"✗ {errors}"
    print(f"  {pw!r:25} → {status}")

# ── Завдання 3 — SQL Injection demo ──────────────────────────────────────────
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'admin', 'admin')")
conn.execute("INSERT INTO users VALUES (2, 'bob', 'user')")
conn.commit()

# НЕБЕЗПЕЧНО:
def get_user_unsafe(username: str) -> list:
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()

# БЕЗПЕЧНО:
def get_user_safe(username: str) -> list:
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

evil = "' OR '1'='1"
print(f"\n[unsafe] {get_user_unsafe(evil)}")  # повертає всіх!
print(f"[safe]   {get_user_safe(evil)}")        # порожньо

# ── Завдання 4 — FileUploadValidator ─────────────────────────────────────────
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG":      "png",
    b"GIF8":         "gif",
    b"%PDF":         "pdf",
}
MAX_SIZE_MB = 5

@dataclass
class UploadResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    ext: str = ""

def validate_upload(filename: str, content: bytes) -> UploadResult:
    errors: list[str] = []

    # 1. Path traversal
    safe_name = os.path.basename(filename)
    if safe_name != filename:
        errors.append("Path traversal detected")
        return UploadResult(valid=False, errors=errors)

    # 2. Extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(f"Розширення {ext!r} не дозволено")

    # 3. Magic bytes
    detected = None
    for magic, file_type in MAGIC_BYTES.items():
        if content[:len(magic)] == magic:
            detected = file_type
            break
    if detected is None and not errors:
        errors.append("Не вдалося визначити тип файлу")

    # 4. Size
    size_mb = len(content) / 1_048_576
    if size_mb > MAX_SIZE_MB:
        errors.append(f"Файл {size_mb:.1f}MB перевищує ліміт {MAX_SIZE_MB}MB")

    return UploadResult(valid=not errors, errors=errors, ext=ext)

# Симуляція
fake_jpg = b"\xff\xd8\xff" + b"\x00" * 100
r = validate_upload("photo.jpg", fake_jpg)
print(f"\nphoto.jpg: valid={r.valid}, errors={r.errors}")

r2 = validate_upload("../etc/passwd", b"some content")
print(f"../etc/passwd: valid={r2.valid}, errors={r2.errors}")

r3 = validate_upload("script.php", b"<?php echo 1; ?>")
print(f"script.php: valid={r3.valid}, errors={r3.errors}")
