"""オーケストレータープロンプトの単体テスト"""

from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT


class TestOrchestratorPrompt:
    """ORCHESTRATOR_SYSTEM_PROMPT のテスト"""

    def test_non_empty(self):
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 0

    def test_contains_agent_names(self):
        assert "transport_agent" in ORCHESTRATOR_SYSTEM_PROMPT
        assert "expense_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_role(self):
        assert "申請受付窓口" in ORCHESTRATOR_SYSTEM_PROMPT
