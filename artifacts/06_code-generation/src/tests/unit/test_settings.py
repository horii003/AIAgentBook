"""settings.py の単体テスト"""
import os
import sys

import pytest


class TestOrchestratorSettings:
    """OrchestratorSettings のテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されていること"""
        from config.settings import OrchestratorSettings
        s = OrchestratorSettings()
        assert s.window_size == 30
        assert s.max_turn_count == 30
        assert s.max_input_length == 500
        assert s.max_iterations == 10
        assert s.max_attempts == 6
        assert s.initial_delay == 4
        assert s.max_delay == 240

    def test_env_override(self):
        """環境変数でデフォルト値を上書きできること"""
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("ORCHESTRATOR_MAX_ITERATIONS", "15")
            from config.settings import OrchestratorSettings
            s = OrchestratorSettings()
            assert s.max_iterations == 15


class TestTransportationExpenseSettings:
    """TransportationExpenseSettings のテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されていること"""
        from config.settings import TransportationExpenseSettings
        s = TransportationExpenseSettings()
        assert s.window_size == 20
        assert s.deadline_months == 3
        assert s.approval_threshold == 10000
        assert s.max_iterations == 10

    def test_env_override(self):
        """環境変数でデフォルト値を上書きできること"""
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("TRANSPORTATION_EXPENSE_DEADLINE_MONTHS", "6")
            from config.settings import TransportationExpenseSettings
            s = TransportationExpenseSettings()
            assert s.deadline_months == 6


class TestGeneralExpenseSettings:
    """GeneralExpenseSettings のテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されていること"""
        from config.settings import GeneralExpenseSettings
        s = GeneralExpenseSettings()
        assert s.window_size == 15
        assert s.deadline_months == 3
        assert s.approval_threshold == 5000
        assert s.max_iterations == 10

    def test_env_override(self):
        """環境変数でデフォルト値を上書きできること"""
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("GENERAL_EXPENSE_APPROVAL_THRESHOLD", "10000")
            from config.settings import GeneralExpenseSettings
            s = GeneralExpenseSettings()
            assert s.approval_threshold == 10000


class TestSettings:
    """_Settings 集約クラスのテスト"""

    def test_settings_orchestrator_access(self):
        """settings.orchestrator にアクセスできること"""
        from config.settings import settings
        assert settings.orchestrator is not None
        assert settings.orchestrator.window_size == 30

    def test_settings_transportation_expense_access(self):
        """settings.transportation_expense にアクセスできること"""
        from config.settings import settings
        assert settings.transportation_expense is not None
        assert settings.transportation_expense.window_size == 20

    def test_settings_general_expense_access(self):
        """settings.general_expense にアクセスできること"""
        from config.settings import settings
        assert settings.general_expense is not None
        assert settings.general_expense.window_size == 15
