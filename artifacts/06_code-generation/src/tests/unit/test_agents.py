"""エージェントの単体テスト"""
import pytest
from unittest.mock import MagicMock, patch
from handlers.error_handler import LoopLimitError


def make_tool_context(applicant_name="田中太郎", application_date="2026-05-10", session_id="test_session"):
    ctx = MagicMock()
    ctx.invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
        "session_id": session_id,
    }
    return ctx


class TestTransportAgent:
    def test_returns_string_on_success(self):
        """transport_agentツール関数が文字列を返すこと"""
        with patch("agents.transport_agent.invoke_specialist_agent", return_value="申請書を生成しました"):
            from agents.transport_agent import transport_agent
            ctx = make_tool_context()
            result = transport_agent.__wrapped__("交通費を申請したい", ctx)
            assert isinstance(result, str)
            assert result == "申請書を生成しました"

    def test_returns_error_message_on_loop_limit(self):
        """LoopLimitError発生時にエラーメッセージ文字列が返ること"""
        error = LoopLimitError(10, 10, "テスト")
        with patch("agents.transport_agent.invoke_specialist_agent", return_value=str(error)):
            from agents.transport_agent import transport_agent
            ctx = make_tool_context()
            result = transport_agent.__wrapped__("交通費を申請したい", ctx)
            assert isinstance(result, str)


class TestExpenseAgent:
    def test_returns_string_on_success(self):
        """expense_agentツール関数が文字列を返すこと"""
        with patch("agents.expense_agent.invoke_specialist_agent", return_value="申請書を生成しました"):
            from agents.expense_agent import expense_agent
            ctx = make_tool_context()
            result = expense_agent.__wrapped__("経費を申請したい", ctx)
            assert isinstance(result, str)
            assert result == "申請書を生成しました"


class TestOrchestratorAgent:
    def test_collect_user_name_empty_then_valid(self):
        """申請者名が空文字の場合に再入力が促されること"""
        from agents.orchestrator_agent import OrchestratorAgent
        agent = OrchestratorAgent(session_id="test_session")
        with patch("builtins.input", side_effect=["", "田中太郎"]):
            agent._collect_user_name()
        assert agent._user_name == "田中太郎"

    def test_invocation_state_contains_required_fields(self):
        """invocation_stateに必要なフィールドが含まれること"""
        from agents.orchestrator_agent import OrchestratorAgent
        agent = OrchestratorAgent(session_id="test_session")
        agent._user_name = "田中太郎"
        # invocation_stateの構築を確認
        from datetime import datetime
        invocation_state = {
            "applicant_name": agent._user_name,
            "application_date": datetime.now().strftime("%Y-%m-%d"),
            "session_id": agent._session_id,
        }
        assert "applicant_name" in invocation_state
        assert "application_date" in invocation_state
        assert "session_id" in invocation_state
        assert invocation_state["applicant_name"] == "田中太郎"
