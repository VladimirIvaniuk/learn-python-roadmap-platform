"""
Розв'язки — Testing з pytest (Middle)
Запуск: pytest solution.py -v
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Optional

# ─────────────── Код під тести ────────────────────────────────────────────────
def calculate_bmi(weight: float, height: float) -> float:
    if height <= 0 or weight <= 0:
        raise ValueError("Weight and height must be positive")
    return weight / (height ** 2)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:   return "Недостатня вага"
    if bmi < 25.0:   return "Норма"
    if bmi < 30.0:   return "Надлишкова вага"
    return "Ожиріння"

def fetch_user(user_id: int, api_client) -> dict:
    response = api_client.get(f"/users/{user_id}")
    if response.status_code == 404:
        raise ValueError(f"User {user_id} not found")
    return response.json()

class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, name: str, email: str) -> dict:
        if "@" not in email:
            raise ValueError("Invalid email")
        user = {"id": 1, "name": name, "email": email}
        self.db.save(user)
        return user

# ─────────────── Fixtures ────────────────────────────────────────────────────
@pytest.fixture
def mock_db():
    db = MagicMock()
    db.save.return_value = None
    return db

@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)

@pytest.fixture
def mock_api():
    client = MagicMock()
    return client

# ─────────────── Тести Завдання 1 ────────────────────────────────────────────
class TestCalculateBMI:
    def test_normal(self):
        bmi = calculate_bmi(70, 1.75)
        assert round(bmi, 2) == 22.86

    def test_zero_height(self):
        with pytest.raises(ValueError, match="positive"):
            calculate_bmi(70, 0)

    def test_negative_weight(self):
        with pytest.raises(ValueError):
            calculate_bmi(-10, 1.75)

    @pytest.mark.parametrize("weight,height,expected", [
        (50,  1.75, "Недостатня вага"),
        (70,  1.75, "Норма"),
        (90,  1.75, "Надлишкова вага"),
        (110, 1.75, "Ожиріння"),
    ])
    def test_classify(self, weight, height, expected):
        bmi = calculate_bmi(weight, height)
        assert classify_bmi(bmi) == expected

# ─────────────── Тести Завдання 2 (мокінг) ───────────────────────────────────
class TestFetchUser:
    def test_success(self, mock_api):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"id": 1, "name": "Alice"}
        mock_api.get.return_value = response

        result = fetch_user(1, mock_api)
        assert result == {"id": 1, "name": "Alice"}
        mock_api.get.assert_called_once_with("/users/1")

    def test_not_found(self, mock_api):
        response = MagicMock()
        response.status_code = 404
        mock_api.get.return_value = response

        with pytest.raises(ValueError, match="not found"):
            fetch_user(99, mock_api)

# ─────────────── Тести Завдання 3 (UserService) ───────────────────────────────
class TestUserService:
    def test_create_user_success(self, user_service, mock_db):
        user = user_service.create_user("Bob", "bob@test.com")
        assert user["name"] == "Bob"
        assert user["email"] == "bob@test.com"
        mock_db.save.assert_called_once_with(user)

    def test_create_user_invalid_email(self, user_service, mock_db):
        with pytest.raises(ValueError, match="Invalid email"):
            user_service.create_user("Bob", "not-an-email")
        mock_db.save.assert_not_called()

# ─────────────── TDD — PasswordValidator ─────────────────────────────────────
class PasswordValidator:
    """Мінімальна реалізація, написана після тестів (TDD)."""

    MIN_LENGTH = 8

    def validate(self, password: str) -> list[str]:
        errors = []
        if len(password) < self.MIN_LENGTH:
            errors.append(f"Мінімум {self.MIN_LENGTH} символів")
        if not any(c.isupper() for c in password):
            errors.append("Потрібна велика літера")
        if not any(c.isdigit() for c in password):
            errors.append("Потрібна цифра")
        if not any(c in "!@#$%^&*" for c in password):
            errors.append("Потрібен спецсимвол")
        return errors

    def is_valid(self, password: str) -> bool:
        return len(self.validate(password)) == 0

class TestPasswordValidator:
    @pytest.fixture
    def validator(self):
        return PasswordValidator()

    def test_strong_password(self, validator):
        assert validator.is_valid("Str0ng!Pass") is True

    def test_too_short(self, validator):
        errs = validator.validate("Ab1!")
        assert any("8 символів" in e for e in errs)

    def test_no_uppercase(self, validator):
        errs = validator.validate("weakpass1!")
        assert any("велика" in e for e in errs)

    def test_no_digit(self, validator):
        errs = validator.validate("StrongPass!")
        assert any("цифра" in e for e in errs)

    def test_no_special(self, validator):
        errs = validator.validate("StrongPass1")
        assert any("спецсимвол" in e for e in errs)

    def test_multiple_errors(self, validator):
        errs = validator.validate("weak")
        assert len(errs) >= 3
