"""settingsの単体テスト"""
from config.settings import settings


class TestSettings:
    def test_orchestrator_window_size(self):
        assert settings.orchestrator.window_size == 30

    def test_transport_agent_deadline_months(self):
        assert settings.transport_agent.deadline_months == 3

    def test_transport_agent_approval_threshold(self):
        assert settings.transport_agent.approval_threshold == 10000

    def test_expense_agent_deadline_months(self):
        assert settings.expense_agent.deadline_months == 3

    def test_expense_agent_approval_threshold(self):
        assert settings.expense_agent.approval_threshold == 5000

    def test_common_max_iterations(self):
        assert settings.orchestrator.max_iterations == 10
        assert settings.transport_agent.max_iterations == 10
        assert settings.expense_agent.max_iterations == 10
