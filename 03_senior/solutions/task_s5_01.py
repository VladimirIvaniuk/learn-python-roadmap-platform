"""
Рішення — Урок 5 (Безпека)

Дивись після того, як спробував сам!
"""


def safe_query(user_id: str) -> str:
    if not user_id.isdigit():
        raise ValueError("user_id має містити тільки цифри")
    return f"SELECT * FROM users WHERE id = {user_id}"


print(safe_query("123"))
try:
    safe_query("1; DROP TABLE users")
except ValueError as e:
    print("Перехоплено:", e)
