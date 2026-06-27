"""base_agentの単体テスト"""
import logging
import pytest
from unittest.mock import MagicMock, patch

from agents.base_agent import calculate_deadline


class TestCalculateDeadline:
    """calculate_deadline関数のテスト"""

    def test_3_months_before(self):
        result = calculate_deadline("2026-05-23", 3)
        assert result == "2026-02-23"

    def test_6_months_before(self):
        result = calculate_deadline("2026-06-01", 6)
        assert result == "2025-12-01"

    def test_invalid_date_returns_yoakumin(self):
        result = calculate_deadline("invalid-date", 3)
        assert result == "要確認"

    def test_empty_date_returns_yoakumin(self):
        result = calculate_deadline("", 3)
        assert result == "要確認"

    def test_invalid_date_logs_warning(self, caplog):
        with caplog.at_level(logging.WARNING, logger="agents.base_agent"):
            calculate_deadline("invalid-date", 3)
        assert "申請期限の計算に失敗しました" in caplog.text
        assert "application_date='invalid-date'" in caplog.text
