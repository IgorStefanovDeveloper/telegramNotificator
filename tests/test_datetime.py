"""Tests for _parse_datetime."""
from datetime import datetime

import pytest

from handlers.events import _parse_datetime


@pytest.mark.parametrize("text,expected", [
    ("19.03.2025 14:30", datetime(2025, 3, 19, 14, 30)),
    ("01.01.2026 00:00", datetime(2026, 1, 1, 0, 0)),
    ("31.12.2024 23:59", datetime(2024, 12, 31, 23, 59)),
    ("  19.03.2025 14:30  ", datetime(2025, 3, 19, 14, 30)),
])
def test_parse_datetime_valid(text, expected):
    assert _parse_datetime(text) == expected


@pytest.mark.parametrize("text", [
    "32.01.2025 12:00",
    "19.13.2025 12:00",
    "19.03.2025 25:00",
    "invalid",
    "",
    "19.03.2025",
    "19.03.2025 14",
    "19-03-2025 14:30",
])
def test_parse_datetime_invalid(text):
    assert _parse_datetime(text) is None
