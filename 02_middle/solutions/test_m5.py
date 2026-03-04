"""
Рішення — Урок 5 (Testing)

Запуск: pytest solutions/test_m5.py -v
"""
import pytest


def is_palindrome(s: str) -> bool:
    return s == s[::-1]


def get_item(lst: list, index: int):
    if index < 0 or index >= len(lst):
        raise IndexError("Index out of range")
    return lst[index]


def test_palindrome_aba() -> None:
    assert is_palindrome("aba") is True


def test_palindrome_hello() -> None:
    assert is_palindrome("hello") is False


def test_palindrome_empty() -> None:
    assert is_palindrome("") is True


@pytest.mark.parametrize("s,expected", [("aba", True), ("ab", False), ("a", True)])
def test_palindrome_parametrized(s: str, expected: bool) -> None:
    assert is_palindrome(s) == expected


def test_get_item_index_error() -> None:
    with pytest.raises(IndexError, match="out of range"):
        get_item([1, 2, 3], 10)
