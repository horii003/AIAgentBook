"""オーケストレーターシステムプロンプトの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT


class TestOrchestratorSystemPrompt:
    """ORCHESTRATOR_SYSTEM_PROMPT のテスト"""

    def test_is_string(self):
        """ORCHESTRATOR_SYSTEM_PROMPT が文字列型であること"""
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)

    def test_not_empty(self):
        """プロンプトが空でないこと"""
        assert len(ORCHESTRATOR_SYSTEM_PROMPT.strip()) > 0

    def test_contains_expense_agent(self):
        """expense_agent の振り分け基準が含まれること"""
        assert "expense_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_transport_agent(self):
        """transport_agent の振り分け基準が含まれること"""
        assert "transport_agent" in ORCHESTRATOR_SYSTEM_PROMPT
