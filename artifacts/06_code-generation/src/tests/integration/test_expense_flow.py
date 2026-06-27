"""経費精算フローの結合テスト

複数モジュールを組み合わせた連携動作を検証する。
"""
import pytest
from unittest.mock import MagicMock, patch

from agents.base_agent import calculate_deadline, invoke_specialist_agent
from handlers.error_handler import LoopLimitError


class TestInvocationStatePropagation:
    """invocation_state伝播のテスト"""

    def test_session_id_excluded_from_child_invocation_state(self):
        """子エージェントへの invocation_state に session_id が含まれないこと"""
        captured_invocation_state = {}

        def mock_build_agent(session_id, applicant_name, application_date, deadline):
            agent = MagicMock()

            def mock_call(query, invocation_state=None):
                captured_invocation_state.update(invocation_state or {})
                return "テスト応答"

            agent.__call__ = mock_call
            return agent

        tool_context = MagicMock()
        tool_context.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-05-23",
            "session_id": "session_20260523_143022_a1b2c3d4",
        }

        with patch("agents.base_agent.SessionManagerFactory"):
            with patch("agents.base_agent.HumanApprovalHook"):
                with patch("agents.base_agent.LoopControlHook"):
                    with patch("agents.base_agent.Agent") as mock_agent_cls:
                        mock_agent = MagicMock()
                        mock_agent.return_value = "テスト応答"
                        mock_agent_cls.return_value = mock_agent

                        result = invoke_specialist_agent(
                            query="テストクエリ",
                            tool_context=tool_context,
                            agent_id="AG-002",
                            deadline_months=3,
                            build_agent=mock_build_agent,
                        )

        # session_id が子エージェントに渡されていないこと
        assert "session_id" not in captured_invocation_state
        assert captured_invocation_state.get("applicant_name") == "山田太郎"
        assert captured_invocation_state.get("application_date") == "2026-05-23"

    def test_loop_limit_error_returns_error_message(self):
        """LoopLimitError発生時にエラーメッセージが返ること"""
        def mock_build_agent(session_id, applicant_name, application_date, deadline):
            agent = MagicMock()
            agent.side_effect = LoopLimitError(10, 10, "テストエージェント")
            return agent

        tool_context = MagicMock()
        tool_context.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-05-23",
            "session_id": "test_session",
        }

        with patch("agents.base_agent.SessionManagerFactory"):
            with patch("agents.base_agent.HumanApprovalHook"):
                with patch("agents.base_agent.LoopControlHook"):
                    with patch("agents.base_agent.Agent") as mock_agent_cls:
                        mock_agent = MagicMock()
                        mock_agent.side_effect = LoopLimitError(10, 10, "テストエージェント")
                        mock_agent_cls.return_value = mock_agent

                        result = invoke_specialist_agent(
                            query="テストクエリ",
                            tool_context=tool_context,
                            agent_id="AG-002",
                            deadline_months=3,
                            build_agent=mock_build_agent,
                        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_unexpected_error_returns_error_message(self):
        """予期しないエラー発生時にエラーメッセージが返ること"""
        def mock_build_agent(session_id, applicant_name, application_date, deadline):
            agent = MagicMock()
            agent.side_effect = RuntimeError("予期しないエラー")
            return agent

        tool_context = MagicMock()
        tool_context.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-05-23",
            "session_id": "test_session",
        }

        with patch("agents.base_agent.SessionManagerFactory"):
            with patch("agents.base_agent.HumanApprovalHook"):
                with patch("agents.base_agent.LoopControlHook"):
                    with patch("agents.base_agent.Agent") as mock_agent_cls:
                        mock_agent = MagicMock()
                        mock_agent.side_effect = RuntimeError("予期しないエラー")
                        mock_agent_cls.return_value = mock_agent

                        result = invoke_specialist_agent(
                            query="テストクエリ",
                            tool_context=tool_context,
                            agent_id="AG-002",
                            deadline_months=3,
                            build_agent=mock_build_agent,
                        )

        assert isinstance(result, str)
        assert len(result) > 0


class TestCalculateDeadlineIntegration:
    """calculate_deadline結合テスト"""

    def test_deadline_calculation_with_settings(self):
        """settings.transportation_expense.deadline_monthsを使った期限計算"""
        from config.settings import settings
        deadline = calculate_deadline("2026-05-23", settings.transportation_expense.deadline_months)
        assert deadline == "2026-02-23"

    def test_deadline_calculation_general_expense(self):
        """settings.general_expense.deadline_monthsを使った期限計算"""
        from config.settings import settings
        deadline = calculate_deadline("2026-05-23", settings.general_expense.deadline_months)
        assert deadline == "2026-02-23"
