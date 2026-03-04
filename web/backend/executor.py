"""
Безпечне виконання Python-коду та перевірка завдань.

Обмеження: timeout 5 сек, ізольована директорія, ліміт розміру коду.
"""
import re
import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Tuple, Optional, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TIMEOUT = 5
MAX_CODE_SIZE = 32_768  # 32 KB
EOF_INPUT_HINT = (
    "Схоже, код використовує input(), але ранер запущено без інтерактивного вводу (EOFError). "
    "Для перевірки на платформі підстав фіксовані тестові значення замість input(), "
    "або запускай цей фрагмент локально в терміналі."
)

_ERROR_EXPLANATIONS: dict[str, dict[str, Any]] = {
    "SyntaxError": {
        "title": "Синтаксична помилка",
        "why": "Python не зміг розібрати код. Часто причина: пропущені дужки, двокрапка або лапки.",
        "fix": [
            "Перевір рядок з помилкою та один рядок вище.",
            "Переконайся, що після if/for/while/def/class є двокрапка ':'.",
            "Перевір, чи всі дужки (), [] та лапки закриті.",
        ],
        "example": "if x > 5  # ❌\n    print(x)\n# має бути: if x > 5:",
    },
    "IndentationError": {
        "title": "Помилка відступів",
        "why": "Python чутливий до відступів. Найчастіше змішані таби/пробіли або зламаний блок.",
        "fix": [
            "Використовуй тільки пробіли (4 пробіли на рівень).",
            "Перевір відступи всередині if/for/while/def.",
            "Уникай змішування Tab і Space.",
        ],
        "example": "if True:\nprint('hi')  # ❌\n# має бути з відступом",
    },
    "NameError": {
        "title": "Невідома змінна",
        "why": "Використано ім'я, яке не було оголошено або є опечатка в назві.",
        "fix": [
            "Перевір написання імені змінної (регістр важливий).",
            "Переконайся, що змінна створена до використання.",
            "Не використовуй лапки для імен змінних і не забувай лапки для тексту.",
        ],
        "example": "print(user_name)  # ❌ якщо оголошено username",
    },
    "TypeError": {
        "title": "Несумісні типи",
        "why": "Операція виконана між значеннями несумісних типів.",
        "fix": [
            "Перевір типи через print(type(x)).",
            "Конвертуй значення у потрібний тип: int(), float(), str().",
            "Пам'ятай: input() повертає рядок (str).",
        ],
        "example": "print('Вік: ' + 25)  # ❌\nprint('Вік: ' + str(25))  # ✅",
    },
    "ValueError": {
        "title": "Некоректне значення",
        "why": "Тип підходить, але саме значення некоректне для операції.",
        "fix": [
            "Перевір вхідні дані перед конвертацією.",
            "Використай try/except для обробки невалідного вводу.",
            "Для чисел з input() перевіряй .isdigit() або обробляй виняток.",
        ],
        "example": "int('abc')  # ❌ ValueError",
    },
    "IndexError": {
        "title": "Індекс поза межами",
        "why": "Спроба доступу до елемента списку/кортежу за неіснуючим індексом.",
        "fix": [
            "Перевір довжину колекції через len().",
            "Використовуй індекси від 0 до len(seq)-1.",
            "Перед доступом перевіряй, що список не порожній.",
        ],
        "example": "items = []\nprint(items[0])  # ❌",
    },
    "KeyError": {
        "title": "Ключ не знайдено",
        "why": "У словнику немає ключа, до якого ти звернувся через d[key].",
        "fix": [
            "Використовуй d.get(key) замість d[key], якщо ключ може бути відсутній.",
            "Перевір наявність: if key in d:",
            "Перевір правильність написання ключа.",
        ],
        "example": "d = {'a': 1}\nprint(d['b'])  # ❌",
    },
    "AttributeError": {
        "title": "Немає такого атрибуту/методу",
        "why": "Ти викликаєш метод або атрибут, якого немає у цього об'єкта.",
        "fix": [
            "Перевір тип об'єкта через type(obj).",
            "Перевір назву методу (можлива опечатка).",
            "Переконайся, що цей метод доступний саме для цього типу.",
        ],
        "example": "5.append(1)  # ❌ у int немає append()",
    },
    "ZeroDivisionError": {
        "title": "Ділення на нуль",
        "why": "У знаменнику опинився 0.",
        "fix": [
            "Перед діленням перевіряй if divisor == 0.",
            "Додай try/except ZeroDivisionError для безпечної обробки.",
            "Покажи користувачу дружнє повідомлення замість падіння програми.",
        ],
        "example": "a / 0  # ❌",
    },
    "ModuleNotFoundError": {
        "title": "Модуль не знайдено",
        "why": "Спроба імпортувати пакет, якого немає у середовищі виконання.",
        "fix": [
            "Перевір правильність назви модуля у import.",
            "Переконайся, що модуль встановлений у поточному середовищі.",
            "Для платформи використовуй тільки дозволені/доступні модулі.",
        ],
        "example": "import some_unknown_package  # ❌",
    },
    "EOFError": {
        "title": "Немає вводу для input()",
        "why": "Код очікує введення, але раннер не має інтерактивного stdin.",
        "fix": [
            "Для платформи заміни input() на фіксовані тестові значення.",
            "Для реального вводу запускай код локально у терміналі.",
        ],
        "example": "name = 'Іван'  # platform-варіант замість input()",
    },
}

# Заборонені патерни — перевіряємо через regex щоб ускладнити обхід
_FORBIDDEN_PATTERNS = [
    r"os\.system",
    r"os\.popen",
    r"os\.execv",
    r"subprocess",
    r"__import__\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
    r"open\s*\(",          # заборона запису/читання файлів
    r"importlib",
    r"builtins",
    r"compile\s*\(",
    r"globals\s*\(",
    r"locals\s*\(",
    r"getattr\s*\(",
    r"setattr\s*\(",
    r"__class__",
    r"__bases__",
    r"__subclasses__",
    r"socket\.",
    r"urllib",
    r"requests\.",
    r"http\.client",
]
_FORBIDDEN_RE = re.compile("|".join(_FORBIDDEN_PATTERNS))

# Тести: custom — handler, stdin — для input()
TASK_TESTS = {
    "lesson_01_hello": {"type": "custom", "handler": "check_lesson_01_hello"},
    "lesson_02_types": {"type": "custom", "handler": "check_lesson_02_types", "stdin": "Тест\n25\n"},
    "lesson_03_flow": {"type": "custom", "handler": "check_lesson_03_flow"},
    "lesson_04_functions": {"type": "custom", "handler": "check_lesson_04_functions"},
    "lesson_01_lists": {"type": "custom", "handler": "check_lesson_01_lists"},
    "lesson_02_dicts_sets": {"type": "custom", "handler": "check_lesson_02_dicts_sets"},
    "lesson_03_comprehensions": {"type": "custom", "handler": "check_lesson_03_comprehensions"},
    "lesson_01_classes": {"type": "custom", "handler": "check_lesson_01_classes"},
    "lesson_02_inheritance": {"type": "custom", "handler": "check_lesson_02_inheritance"},
    "lesson_01_files": {"type": "custom", "handler": "check_lesson_01_files"},
    "lesson_02_exceptions": {"type": "custom", "handler": "check_lesson_02_exceptions", "stdin": "0\n"},
    "lesson_01_oop_advanced": {"type": "custom", "handler": "check_lesson_01_oop_advanced"},
    "lesson_02_async": {"type": "custom", "handler": "check_lesson_02_async"},
    "lesson_03_fastapi": {"type": "run"},
    "lesson_04_databases": {"type": "run"},
    "lesson_05_testing": {"type": "run"},
    "lesson_06_devops": {"type": "run"},
    "lesson_01_architecture": {"type": "custom", "handler": "check_lesson_01_architecture"},
    "lesson_02_design_patterns": {"type": "custom", "handler": "check_lesson_02_design_patterns"},
    "lesson_03_system_design": {"type": "custom", "handler": "check_lesson_03_system_design"},
    "lesson_04_code_quality": {"type": "run"},
    "lesson_05_security": {"type": "custom", "handler": "check_lesson_05_security"},
    "lesson_06_soft_skills": {"type": "run"},
}


def _check(details: List[str], ok: bool, msg: str, fail_msg: str) -> Optional[str]:
    """Повертає fail_msg якщо не пройдено, інакше None."""
    details.append(f"{'✓' if ok else '✗'} {msg}")
    return fail_msg if not ok else None


def _extract_error_type(stderr: str) -> str:
    match = re.search(r"([A-Za-z_]+Error):", stderr)
    if match:
        return match.group(1)
    if "SyntaxError" in stderr:
        return "SyntaxError"
    if "IndentationError" in stderr:
        return "IndentationError"
    return "RuntimeError"


def _extract_error_line(stderr: str) -> Optional[int]:
    match = re.search(r'File ".*?", line (\d+)', stderr)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def explain_error(stderr: str, code: Optional[str] = None) -> dict[str, Any]:
    """Перетворює traceback у дружнє пояснення для користувача."""
    error_type = _extract_error_type(stderr)
    line = _extract_error_line(stderr)
    profile = _ERROR_EXPLANATIONS.get(
        error_type,
        {
            "title": "Помилка виконання",
            "why": "Код завершився з помилкою під час виконання.",
            "fix": [
                "Перевір traceback нижче і рядок, де впала програма.",
                "Виведи проміжні значення через print() для дебагу.",
            ],
            "example": None,
        },
    )

    summary = stderr.splitlines()[-1] if stderr.strip() else "Невідома помилка"
    line_snippet = None
    if code and line and 1 <= line <= len(code.splitlines()):
        src = code.splitlines()
        line_snippet = src[line - 1].strip()

    return {
        "error_type": error_type,
        "title": profile["title"],
        "summary": summary,
        "line": line,
        "line_snippet": line_snippet,
        "why": profile["why"],
        "fix": profile["fix"],
        "example": profile["example"],
    }


# === Junior: Basics ===
def check_lesson_01_hello(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    lines = [ln.strip() for ln in output.strip().split("\n") if ln.strip()]
    fail = _check(details, "Я вивчаю Python" in output, "Завд.1: 'Я вивчаю Python'", "Завдання 1: виведи 'Я вивчаю Python'")
    if fail:
        return (False, fail, details)
    fail = _check(details, "Це мій перший урок" in output, "Завд.1: 'Це мій перший урок'", "Завдання 1: виведи 'Це мій перший урок'")
    if fail:
        return (False, fail, details)
    fail = _check(details, any(re.search(r"\d+", ln) for ln in lines[:3]), "Завд.1: вік", "Завдання 1: виведи вік числом")
    if fail:
        return (False, fail, details)
    fail = _check(details, "city" in code, "Завд.2: змінна city", "Завдання 2: створи змінну city")
    if fail:
        return (False, fail, details)
    fail = _check(details, len(lines) >= 4, "Завд.2: вивід міста", "Завдання 2: виведи місто")
    if fail:
        return (False, fail, details)
    fail = _check(details, "a" in code and "b" in code, "Завд.3: змінні a, b", "Завдання 3: створи a та b")
    if fail:
        return (False, fail, details)
    fail = _check(details, any(re.search(r"\d+", ln) for ln in lines[-2:] if ln), "Завд.3: вивід суми", "Завдання 3: виведи суму")
    if fail:
        return (False, fail, details)
    return True, "Всі три завдання виконано!", details


def check_lesson_02_types(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(
        details,
        "a" in code and "b" in code and ("17" in code or "5" in code),
        "Завд.1: a, b",
        "Завдання 1: створи a=17 та b=5",
    )
    if fail:
        return (False, fail, details)
    fail = _check(
        details,
        all(op in code for op in ["/", "//", "%", "**"]),
        "Завд.1: операції /, //, %, **",
        "Завдання 1: використай усі операції: /, //, %, **",
    )
    if fail:
        return (False, fail, details)
    fail = _check(
        details,
        "text" in code and all(m in code for m in [".strip()", ".capitalize()", ".count(", ".replace(", ".split("]),
        "Завд.2: рядкові методи",
        "Завдання 2: застосуй strip/capitalize/count/replace/split",
    )
    if fail:
        return (False, fail, details)
    fail = _check(
        details,
        "def safe_int" in code and "int(" in code and "except" in code,
        "Завд.3: safe_int()",
        "Завдання 3: реалізуй safe_int(value) з try/except",
    )
    if fail:
        return (False, fail, details)
    fail = _check(
        details,
        ("truthy" in output.lower() or "falsy" in output.lower()) or ("truthy" in code and "falsy" in code),
        "Завд.4: truthy/falsy",
        "Завдання 4: виведи truthy/falsy для набору значень",
    )
    if fail:
        return (False, fail, details)
    details.append("ℹ️ Завд.5 (challenge): input() або platform-симуляція приймаються обидва")
    return True, "Базові завдання уроку виконано!", details


def check_lesson_03_flow(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    code_l = code.lower()
    output_l = output.lower()

    fail = _check(
        details,
        ("def grade" in code_l)
        and any(word in code_l for word in ["відмінно", "добре", "задовільно", "незадовільно", "помилка"]),
        "Завд.1: grade()",
        "Завдання 1: реалізуй функцію grade(score) з усіма категоріями оцінки",
    )
    if fail:
        return (False, fail, details)

    fail = _check(
        details,
        ("for " in code_l and "range" in code_l)
        and "fizz" in code_l
        and "buzz" in code_l,
        "Завд.2: FizzBuzz",
        "Завдання 2: виведи FizzBuzz для чисел 1..30",
    )
    if fail:
        return (False, fail, details)

    fail = _check(
        details,
        ("2" in output and "9" in output and ("×" in output or "*" in output))
        or ("range(2, 10)" in code_l and ("×" in code or "*" in code)),
        "Завд.3: таблиця множення 2-9",
        "Завдання 3: виведи таблицю множення від 2 до 9",
    )
    if fail:
        return (False, fail, details)

    fail = _check(
        details,
        ("sentences" in code_l and "python" in code_l)
        and ("lower()" in code_l)
        and ("count" in code_l or "sum(" in code_l),
        "Завд.4: підрахунок 'Python'",
        "Завдання 4: порахуй кількість речень зі словом 'Python' без урахування регістру",
    )
    if fail:
        return (False, fail, details)

    fail = _check(
        details,
        ("fibonacci" in code_l and ("yield" in code_l or "append" in code_l))
        and ("while " in code_l)
        and ("89" in output or "fibonacci(100" in code_l),
        "Завд.5: Fibonacci",
        "Завдання 5: реалізуй генератор/функцію Fibonacci до максимуму N",
    )
    if fail:
        return (False, fail, details)
    return True, "Всі завдання уроку виконано!", details


def check_lesson_04_functions(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "def " in code, "Функції def", "Напиши функції через def")
    if fail:
        return (False, fail, details)
    fail = _check(details, "square" in code, "Завд.1: square()", "Завдання 1: функція square")
    if fail:
        return (False, fail, details)
    # Приймаємо both "greet" і "great" — назва функції у задачі може відрізнятись
    fail = _check(details, "greet" in code or "great" in code, "Завд.2: greet()/great()", "Завдання 2: функція-привітання (greet або great)")
    if fail:
        return (False, fail, details)
    fail = _check(details, "is_even" in code, "Завд.3: is_even()", "Завдання 3: функція is_even")
    if fail:
        return (False, fail, details)
    fail = _check(details, "max_of_two" in code or "max" in code, "Завд.4: max_of_two()", "Завдання 4: функція max_of_two")
    if fail:
        return (False, fail, details)
    fail = _check(details, "25" in output or "True" in output or "20" in output, "Вивід результатів", "Виведи результати функцій")
    if fail:
        return (False, fail, details)
    return True, "Всі функції виконано!", details


# === Junior: Data structures ===
def check_lesson_01_lists(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "зелений" in output, "Завд.1: другий елемент (зелений)", "Завдання 1: виведи colors[1]")
    if fail:
        return (False, fail, details)
    fail = _check(details, "[20" in output or "20" in output, "Завд.2: зріз [20,30,40]", "Завдання 2: зріз nums[1:4]")
    if fail:
        return (False, fail, details)
    fail = _check(details, "зошит" in output, "Завд.3: зошит", "Завдання 3: insert зошит")
    if fail:
        return (False, fail, details)
    fail = _check(details, "5" in output and "10" in output, "Завд.4: координати 5,10", "Завдання 4: кортеж coords")
    if fail:
        return (False, fail, details)
    fail = _check(details, "append" in code or "insert" in code, "Методи списку", "Використай append/insert")
    if fail:
        return (False, fail, details)
    return True, "Всі завдання виконано!", details


def check_lesson_02_dicts_sets(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "Телефон" in output, "Завд.1: product Телефон", "Завдання 1: словник product")
    if fail:
        return (False, fail, details)
    fail = _check(details, "{" in code and "}" in code, "Словники", "Використай словники")
    if fail:
        return (False, fail, details)
    fail = _check(details, ".items()" in code or "items()" in code, "Завд.2: .items()", "Завдання 2: цикл for key, value in items()")
    if fail:
        return (False, fail, details)
    fail = _check(details, "{" in output or "set" in output.lower(), "Завд.3-4: множини", "Завдання 3-4: множини")
    if fail:
        return (False, fail, details)
    return True, "Всі завдання виконано!", details


def check_lesson_03_comprehensions(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "for " in code and " in " in code and "[" in code, "List comprehension", "Завд.1-2: list comprehension")
    if fail:
        return (False, fail, details)
    fail = _check(details, "27" in output or "64" in output or "125" in output, "Завд.1: куби", "Завдання 1: куби 1-5")
    if fail:
        return (False, fail, details)
    fail = _check(details, "{" in code and "for " in code and ":" in code, "Dict/Set comprehension", "Завд.3-4: dict/set comprehension")
    if fail:
        return (False, fail, details)
    return True, "Всі завдання виконано!", details


# === Junior: OOP ===
def check_lesson_01_classes(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "class " in code, "Клас", "Створи клас")
    if fail:
        return (False, fail, details)
    fail = _check(details, "Book" in code or "Rectangle" in code or "BankAccount" in code, "Завд.1-3: класи", "Створи класи Book, Rectangle, BankAccount")
    if fail:
        return (False, fail, details)
    fail = _check(details, "info" in code or "area" in code or "deposit" in code, "Методи", "Додай методи info/area/deposit")
    if fail:
        return (False, fail, details)
    fail = _check(details, "__init__" in code, "__init__", "Конструктор __init__")
    if fail:
        return (False, fail, details)
    return True, "Всі класи виконано!", details


def check_lesson_02_inheritance(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "class " in code, "Класи", "Створи класи")
    if fail:
        return (False, fail, details)
    fail = _check(details, "super" in code or "Animal" in code or "Vehicle" in code, "Наслідування", "Використай наслідування")
    if fail:
        return (False, fail, details)
    fail = _check(details, "Гав" in output or "дверей" in output, "Вивід Dog/Car", "Виведи speak() та info()")
    if fail:
        return (False, fail, details)
    return True, "Наслідування виконано!", details


# === Junior: Files & Exceptions ===
def check_lesson_01_files(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "open" in code, "open()", "Використай open()")
    if fail:
        return (False, fail, details)
    fail = _check(details, "Замітка" in output or "1." in output, "Завд.1-2: notes.txt", "Створи та прочитай notes.txt")
    if fail:
        return (False, fail, details)
    fail = _check(details, "append" in code.lower() or '"a"' in code or "'a'" in code, "Завд.3: append", "Функція append_line")
    if fail:
        return (False, fail, details)
    return True, "Робота з файлами виконано!", details


def check_lesson_02_exceptions(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "try" in code and "except" in code, "try/except", "Використай try/except")
    if fail:
        return (False, fail, details)
    fail = _check(details, "ZeroDivisionError" in code or "ділення" in output.lower() or "нуль" in output.lower(), "Завд.1: ділення на 0", "Оброби ZeroDivisionError")
    if fail:
        return (False, fail, details)
    fail = _check(details, "safe_divide" in code or "def " in code, "Завд.2: safe_divide", "Функція safe_divide")
    if fail:
        return (False, fail, details)
    fail = _check(details, "None" in output or "Exception" in code or "Error" in code, "Завд.3: NegativeNumberError", "Клас NegativeNumberError")
    if fail:
        return (False, fail, details)
    return True, "Винятки виконано!", details


# === Middle ===
def check_lesson_01_oop_advanced(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "class " in code, "Клас", "Створи класи")
    if fail:
        return (False, fail, details)
    fail = _check(details, "__str__" in code or "__eq__" in code, "Завд.1: магічні методи", "Fraction: __str__, __eq__")
    if fail:
        return (False, fail, details)
    fail = _check(details, "count_calls" in code or "call_count" in code, "Завд.2: декоратор", "Декоратор count_calls")
    if fail:
        return (False, fail, details)
    fail = _check(details, "@property" in code or "property" in code, "Завд.3: property", "Circle з @property area")
    if fail:
        return (False, fail, details)
    return True, "Поглиблене ООП виконано!", details


def check_lesson_02_async(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "async " in code or "await " in code, "async/await", "Асинхронні функції")
    if fail:
        return (False, fail, details)
    fail = _check(details, "asyncio" in code or "gather" in code, "asyncio", "Використай asyncio")
    if fail:
        return (False, fail, details)
    return True, "Асинхронність виконано!", details


# === Senior ===
def check_lesson_01_architecture(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "class " in code and ("Logger" in code or "logger" in code.lower()), "Logger", "Абстрактний Logger")
    if fail:
        return (False, fail, details)
    fail = _check(details, "ABC" in code or "abstract" in code, "ABC", "Абстрактний клас")
    if fail:
        return (False, fail, details)
    fail = _check(details, "App" in code or "log" in code.lower(), "DI", "Клас App з Dependency Injection")
    if fail:
        return (False, fail, details)
    return True, "Архітектура виконано!", details


def check_lesson_02_design_patterns(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "Exporter" in code or "exporter" in code or "export" in code, "Factory", "Factory для експортерів")
    if fail:
        return (False, fail, details)
    fail = _check(details, "Validator" in code or "Strategy" in code or "validate" in code, "Strategy", "Strategy для валідації")
    if fail:
        return (False, fail, details)
    return True, "Design Patterns виконано!", details


def check_lesson_03_system_design(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "cache" in code.lower() or "get" in code or "set" in code, "Кеш", "Кеш з get/set")
    if fail:
        return (False, fail, details)
    fail = _check(details, "ttl" in code.lower() or "TTL" in code or "None" in code, "TTL", "TTL для кешу")
    if fail:
        return (False, fail, details)
    return True, "Системний дизайн виконано!", details


def check_lesson_05_security(output: str, code: str) -> Tuple[bool, str, List[str]]:
    details = []
    fail = _check(details, "safe_query" in code or "def " in code, "safe_query", "Функція safe_query")
    if fail:
        return (False, fail, details)
    fail = _check(details, "ValueError" in code or "raise " in code, "Валідація", "Перевірка user_id")
    if fail:
        return (False, fail, details)
    fail = _check(details, "isdigit" in code or "isdigit()" in code, "Перевірка цифр", "Перевір що user_id — цифри")
    if fail:
        return (False, fail, details)
    return True, "Безпека виконано!", details


def run_code(code: str, stdin: Optional[str] = None) -> dict:
    """Запускає Python-код. stdin — для input()."""
    if not code or not code.strip():
        err = "Порожній код"
        return {"output": "", "error": err, "debug": explain_error(err, code)}

    if len(code) > MAX_CODE_SIZE:
        err = f"Код занадто великий (максимум {MAX_CODE_SIZE // 1024} KB)"
        return {"output": "", "error": err, "debug": explain_error(err, code)}

    match = _FORBIDDEN_RE.search(code)
    if match:
        err = f"Заборонена операція: {match.group()!r}"
        return {"output": "", "error": err, "debug": explain_error(err, code)}

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "user_code.py"
        script_path.write_text(code, encoding="utf-8")

        try:
            result = subprocess.run(
                [os.environ.get("PYTHON", "python3"), str(script_path)],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
                cwd=tmpdir,
                input=stdin,
            )
            output = result.stdout or ""
            error = result.stderr.strip() if result.stderr else None
            if result.returncode != 0 and error:
                if "EOFError: EOF when reading a line" in error:
                    error = f"{error}\n\nПідказка: {EOF_INPUT_HINT}"
                return {"output": output, "error": error, "debug": explain_error(error, code)}
            return {"output": output, "error": None, "debug": None}
        except subprocess.TimeoutExpired:
            err = "TimeoutError: Час виконання перевищено (5 сек)"
            return {"output": "", "error": err, "debug": explain_error(err, code)}
        except Exception as e:
            err = str(e)
            return {"output": "", "error": err, "debug": explain_error(err, code)}


def check_task(lesson_id: str, code: str) -> dict:
    tests = TASK_TESTS.get(lesson_id, {"type": "run"})
    stdin = tests.get("stdin")

    run_result = run_code(code, stdin=stdin)
    if run_result.get("error"):
        debug = run_result.get("debug") or {}
        details = []
        if debug.get("title"):
            details.append(f"🔎 {debug['title']}: {debug.get('summary', '')}")
        if debug.get("line"):
            details.append(f"📍 Рядок: {debug['line']}")
        for fix in debug.get("fix", [])[:3]:
            details.append(f"💡 {fix}")
        details.append("—")
        details.append(run_result["error"])
        return {"passed": False, "message": "Код не виконався", "details": details}

    output = run_result.get("output", "")

    if tests["type"] == "run":
        return {"passed": True, "message": "Код виконався успішно!", "details": []}

    if tests["type"] == "custom":
        handler = globals().get(tests.get("handler"))
        if handler and callable(handler):
            passed, message, details = handler(output, code)
            return {"passed": passed, "message": message, "details": details}
        return {"passed": True, "message": "OK", "details": []}

    return {"passed": True, "message": "OK", "details": []}
