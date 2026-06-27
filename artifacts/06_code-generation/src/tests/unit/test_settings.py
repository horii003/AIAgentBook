"""設定クラスの単体テスト"""
from config.settings import settings


class TestSettings:
    """設定クラスのテスト"""

    def test_orchestrator_window_size(self):
        assert settings.orchestrator.window_size == 30

    def test_orchestrator_max_iterations(self):
        assert settings.orchestrator.max_iterations == 10

    def test_transportation_expense_deadline_months(self):
        assert settings.transportation_expense.deadline_months == 3

    def test_transportation_expense_window_size(self):
        assert settings.transportation_expense.window_size == 20

    def test_transportation_expense_approval_threshold(self):
        assert settings.transportation_expense.approval_threshold == 10000

    def test_general_expense_deadline_months(self):
        assert settings.general_expense.deadline_months == 3

    def test_general_expense_window_size(self):
        assert settings.general_expense.window_size == 15

    def test_general_expense_approval_threshold(self):
        assert settings.general_expense.approval_threshold == 5000
