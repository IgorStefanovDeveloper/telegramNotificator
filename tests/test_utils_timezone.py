"""Tests for timezone utilities."""
from datetime import datetime

import pytest

from utils_timezone import local_to_utc, utc_to_local, format_utc_for_display, utc_now


def test_local_to_utc_ho_chi_minh():
    """Vietnam (Nha Trang) UTC+7: 12:00 local = 05:00 UTC."""
    dt = datetime(2025, 1, 15, 12, 0)
    result = local_to_utc(dt, "Asia/Ho_Chi_Minh")
    assert result.hour == 5
    assert result.minute == 0
    assert result.day == 15


def test_local_to_utc_moscow():
    """14:30 Moscow = 11:30 UTC (Moscow UTC+3)."""
    dt = datetime(2025, 5, 19, 14, 30)
    result = local_to_utc(dt, "Europe/Moscow")
    assert result.year == 2025
    assert result.month == 5
    assert result.day == 19
    assert result.hour == 11
    assert result.minute == 30


def test_local_to_utc_utc_unchanged():
    """UTC timezone: local = UTC, no conversion."""
    dt = datetime(2025, 6, 1, 12, 0)
    result = local_to_utc(dt, "UTC")
    assert result == dt


def test_utc_to_local():
    """UTC converts back to local."""
    dt_utc = datetime(2025, 5, 19, 11, 30)
    result = utc_to_local(dt_utc, "Europe/Moscow")
    assert result.hour == 14
    assert result.minute == 30
    assert result.day == 19


def test_local_to_utc_roundtrip():
    """local_to_utc then utc_to_local returns original (for Moscow)."""
    original = datetime(2025, 7, 20, 18, 45)
    utc = local_to_utc(original, "Europe/Moscow")
    back = utc_to_local(utc, "Europe/Moscow")
    assert back == original


def test_format_utc_for_display():
    """UTC datetime formats correctly in Moscow timezone."""
    # 11:30 UTC = 14:30 Moscow
    dt_utc = datetime(2025, 5, 19, 11, 30)
    result = format_utc_for_display(dt_utc, "Europe/Moscow")
    assert "19.05.2025" in result
    assert "14:30" in result


def test_utc_now_returns_naive():
    """utc_now returns naive datetime (no tzinfo)."""
    result = utc_now()
    assert result.tzinfo is None
