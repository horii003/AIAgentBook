"""prompt_orchestrator の単体テスト"""
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT


class TestOrchestratorSystemPrompt:
    """ORCHESTRATOR_SYSTEM_PROMPT のテスト"""

    def test_is_non_empty_string(self):
        """空でない文字列であること"""
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)
        assert len(ORCHESTRATOR_SYSTEM_PROMPT.strip()) > 0

    def test_contains_transportation_expense_agent(self):
        """transportation_expense_agent が含まれること"""
        assert "transportation_expense_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_general_expense_agent(self):
        """general_expense_agent が含まれること"""
        assert "general_expense_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_japanese_content(self):
        """日本語コンテンツが含まれること"""
        assert "申請" in ORCHESTRATOR_SYSTEM_PROMPT
