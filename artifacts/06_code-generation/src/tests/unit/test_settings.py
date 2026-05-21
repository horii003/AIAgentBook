"""エージェント動作パラメータ設定の単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from config.settings import settings, OrchestratorSettings, TransportSettings, ExpenseSettings


class TestSettings:
    """settings のテスト"""

    def test_orchestrator_window_size(self):
        """settings.orchestrator.window_size が 30 であること"""
        assert settings.orchestrator.window_size == 30

    def test_transport_deadline_months(self):
        """settings.transport.deadline_months が 3 であること"""
        assert settings.transport.deadline_months == 3

    def test_expense_approval_threshold(self):
        """settings.expense.approval_threshold が 5000 であること"""
        assert settings.expense.approval_threshold == 5000

    def test_transport_env_override(self, monkeypatch):
        """環境変数 ECAAS_TRANSPORT_MAX_ITERATIONS=15 を設定した場合に上書きされること"""
        monkeypatch.setenv("ECAAS_TRANSPORT_MAX_ITERATIONS", "15")
        transport = TransportSettings()
        assert transport.max_iterations == 15

    def test_orchestrator_max_turn_count(self):
        """settings.orchestrator.max_turn_count が 30 であること"""
        assert settings.orchestrator.max_turn_count == 30

    def test_expense_window_size(self):
        """settings.expense.window_size が 15 であること"""
        assert settings.expense.window_size == 15
