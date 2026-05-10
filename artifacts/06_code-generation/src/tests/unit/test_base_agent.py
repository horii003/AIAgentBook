"""base_agentの単体テスト"""
import pytest
from unittest.mock import MagicMock, patch
from agents.base_agent import calculate_deadline


class TestCalculateDeadline:
    def test_valid_date(self):
        """calculate_deadline("2026-05-10", 3)が"2026-02-10"を返すこと"""
        result = calculate_deadline("2026-05-10", 3)
        assert result == "2026-02-10"

    def test_invalid_date_returns_yokakunin(self):
        """calculate_deadline("invalid", 3)が"要確認"を返すこと"""
        result = calculate_deadline("invalid", 3)
        assert result == "要確認"

    def test_month_boundary(self):
        """月末日の計算が正しいこと"""
        result = calculate_deadline("2026-03-31", 1)
        assert result == "2026-02-28"

    def test_zero_months(self):
        """0ヶ月の場合は同日を返すこと"""
        result = calculate_deadline("2026-05-10", 0)
        assert result == "2026-05-10"
