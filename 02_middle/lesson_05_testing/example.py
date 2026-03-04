"""
Урок Middle 5 — Приклади: pytest тести

Запуск: pytest example.py -v
або:   python -m pytest example.py -v
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


# ── Код що тестуємо ───────────────────────────────────────────────────────────
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be positive")
    return weight_kg / height_m ** 2


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


def safe_divide(a: float, b: float) -> float | None:
    try:
        return a / b
    except (ZeroDivisionError, TypeError):
        return None


class EmailService:
    def send(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("Real implementation would send email")


def register_user(email: str, username: str, email_service: EmailService) -> dict:
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    user = {"id": 1, "email": email, "username": username}
    email_service.send(to=email, subject="Welcome!", body=f"Hello {username}!")
    return user


# ── Unit тести ────────────────────────────────────────────────────────────────
class TestBMI:
    def test_normal_bmi(self):
        bmi = calculate_bmi(70, 1.75)
        assert abs(bmi - 22.86) < 0.01

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError, match="positive"):
            calculate_bmi(0, 1.75)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70, -1.75)

    @pytest.mark.parametrize("weight, height, expected_category", [
        (50, 1.75, "underweight"),
        (70, 1.75, "normal"),
        (90, 1.75, "overweight"),
        (120, 1.75, "obese"),
    ])
    def test_bmi_categories(self, weight, height, expected_category):
        bmi = calculate_bmi(weight, height)
        assert classify_bmi(bmi) == expected_category


class TestSafeDivide:
    def test_normal_division(self):
        assert safe_divide(10, 2) == 5.0

    def test_division_by_zero(self):
        assert safe_divide(10, 0) is None

    def test_type_error(self):
        assert safe_divide("10", 2) is None

    @pytest.mark.parametrize("a, b, expected", [
        (10, 2, 5.0),
        (0, 5, 0.0),
        (-10, 2, -5.0),
    ])
    def test_parametrized(self, a, b, expected):
        assert safe_divide(a, b) == expected


# ── Мокування ────────────────────────────────────────────────────────────────
class TestRegistration:
    def test_sends_welcome_email(self):
        mock_email = Mock(spec=EmailService)
        mock_email.send.return_value = True

        user = register_user("test@example.com", "testuser", mock_email)

        mock_email.send.assert_called_once_with(
            to="test@example.com",
            subject="Welcome!",
            body="Hello testuser!",
        )
        assert user["email"] == "test@example.com"

    def test_invalid_email_raises(self):
        mock_email = Mock(spec=EmailService)
        with pytest.raises(ValueError, match="Invalid email"):
            register_user("not-an-email", "user", mock_email)

    def test_email_not_sent_on_error(self):
        mock_email = Mock(spec=EmailService)
        try:
            register_user("", "user", mock_email)
        except ValueError:
            pass
        mock_email.send.assert_not_called()


# ── Фікстури ──────────────────────────────────────────────────────────────────
@pytest.fixture
def sample_users() -> list[dict]:
    return [
        {"id": 1, "name": "Аліса", "active": True,  "score": 92},
        {"id": 2, "name": "Боб",   "active": False, "score": 78},
        {"id": 3, "name": "Катя",  "active": True,  "score": 88},
    ]


def test_active_users_count(sample_users):
    active = [u for u in sample_users if u["active"]]
    assert len(active) == 2


def test_top_scorer(sample_users):
    top = max(sample_users, key=lambda u: u["score"])
    assert top["name"] == "Аліса"


# ── Patch ─────────────────────────────────────────────────────────────────────
@patch("builtins.open", create=True)
def test_with_mock_file(mock_open):
    mock_open.return_value.__enter__ = Mock(return_value=MagicMock(read=Mock(return_value="content")))
    mock_open.return_value.__exit__ = Mock(return_value=False)

    with open("fake.txt") as f:
        data = f.read()

    mock_open.assert_called_once_with("fake.txt")
