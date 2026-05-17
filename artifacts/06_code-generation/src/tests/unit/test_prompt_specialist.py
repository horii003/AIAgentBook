"""専門エージェントプロンプトの単体テスト"""

from prompt.prompt_expense import get_expense_system_prompt
from prompt.prompt_transport import get_transport_system_prompt


class TestTransportPrompt:
    """get_transport_system_prompt のテスト"""

    def test_non_empty(self):
        result = get_transport_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_applicant(self):
        result = get_transport_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "山田太郎" in result

    def test_contains_dates(self):
        result = get_transport_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "2026-05-17" in result
        assert "2026-02-17" in result

    def test_contains_policies(self):
        result = get_transport_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "BRL-08" in result


class TestExpensePrompt:
    """get_expense_system_prompt のテスト"""

    def test_non_empty(self):
        result = get_expense_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_applicant(self):
        result = get_expense_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "山田太郎" in result

    def test_contains_dates(self):
        result = get_expense_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "2026-05-17" in result
        assert "2026-02-17" in result

    def test_contains_policies(self):
        result = get_expense_system_prompt("山田太郎", "2026-05-17", "2026-02-17")
        assert "BRL-09" in result
        assert "経費区分" in result
