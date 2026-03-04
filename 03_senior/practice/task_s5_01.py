"""
Практика — Урок 5 (Безпека)
Дивись lesson_05_security/task.md

Завдання: safe_query — захист від SQL Injection
Завдання: validate_email — базова валідація
"""


def safe_query(user_id: str) -> tuple:
    """
    Повертає (sql, params) з параметризованим запитом.
    Якщо user_id не є числом — raise ValueError.

    Погано:  f"SELECT * FROM users WHERE id = {user_id}"
    Добре:   "SELECT * FROM users WHERE id = ?" з (int(user_id),)
    """
    # TODO: if not user_id.isdigit(): raise ValueError(...)
    # TODO: return ("SELECT * FROM users WHERE id = ?", (int(user_id),))
    if not str(user_id).isdigit():
        raise ValueError("Невалідний user_id")
    return ("SELECT * FROM users WHERE id = ?", (int(user_id),))


def hash_password(password: str) -> str:
    """
    Хешує пароль через sha256 (демо).
    У реальному проєкті: from passlib.hash import bcrypt; return bcrypt.hash(password)
    """
    import hashlib
    # TODO: повернути hashlib.sha256(password.encode()).hexdigest()
    return hashlib.sha256(password.encode()).hexdigest()


# Перевірка
if __name__ == "__main__":
    query, params = safe_query("42")
    print(f"Query: {query}, params: {params}")

    try:
        safe_query("1; DROP TABLE users")
    except ValueError as e:
        print(f"Заблоковано: {e}")

    hashed = hash_password("mysecret")
    print(f"Hash: {hashed[:20]}...")
