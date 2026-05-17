"""設定管理の単体テスト"""

from config.settings import (
    ExpenseSettings,
    OrchestratorSettings,
    TransportSettings,
    _Settings,
    settings,
)


class TestSettings:
    """settings のテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されること"""
        assert settings.orchestrator.window_size == 30
        assert settings.orchestrator.max_iterations == 10
        assert settings.transport.window_size == 20
        assert settings.transport.deadline_months == 3
        assert settings.expense.window_size == 15
        assert settings.expense.deadline_months == 3

    def test_access_via_module_variable(self):
        """settings モジュール変数からアクセスできること"""
        assert hasattr(settings, "orchestrator")
        assert hasattr(settings, "transport")
        assert hasattr(settings, "expense")

    def test_orchestrator_settings(self):
        s = OrchestratorSettings()
        assert s.max_turn_count == 30
        assert s.max_input_length == 500

    def test_transport_settings(self):
        s = TransportSettings()
        assert s.approval_threshold == 10000

    def test_expense_settings(self):
        s = ExpenseSettings()
        assert s.approval_threshold == 10000
