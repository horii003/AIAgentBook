"""専門エージェントの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
from strands import Agent
from handlers.error_handler import LoopLimitError


class TestTransportAgent:
    """transport_agent のテスト"""

    def test_build_transport_agent_returns_agent(self):
        """_build_transport_agent() が Agent インスタンスを返すこと"""
        with patch("agents.transport_agent.create_specialist_agent") as mock_create:
            mock_create.return_value = MagicMock(spec=Agent)
            from agents.transport_agent import _build_transport_agent
            result = _build_transport_agent(
                session_id="test",
                applicant_name="山田太郎",
                application_date="2026-01-15",
                deadline="2025-10-15",
            )
            mock_create.assert_called_once()
            assert result is not None

    def test_transport_agent_tool_returns_string(self):
        """transport_agent ツール関数が文字列を返すこと"""
        mock_agent = MagicMock()
        mock_agent.return_value = "交通費申請書を生成しました"

        def mock_build(session_id, applicant_name, application_date, deadline):
            return mock_agent

        ctx = MagicMock()
        ctx.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-01-15",
            "session_id": "test_session",
        }

        with patch("agents.transport_agent._build_transport_agent", mock_build):
            from agents.transport_agent import transport_agent
            result = transport_agent.__wrapped__(query="交通費申請", tool_context=ctx)
            assert isinstance(result, str)

    def test_transport_agent_loop_limit_error_returns_message(self):
        """LoopLimitError 発生時にエラーメッセージ文字列が返ること"""
        def mock_build(session_id, applicant_name, application_date, deadline):
            mock_agent = MagicMock()
            mock_agent.side_effect = LoopLimitError(10, 10, "交通費精算申請エージェント")
            return mock_agent

        ctx = MagicMock()
        ctx.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-01-15",
            "session_id": "test_session",
        }

        with patch("agents.transport_agent._build_transport_agent", mock_build):
            from agents.transport_agent import transport_agent
            result = transport_agent.__wrapped__(query="交通費申請", tool_context=ctx)
            assert isinstance(result, str)
            assert len(result) > 0


class TestExpenseAgent:
    """expense_agent のテスト"""

    def test_build_expense_agent_returns_agent(self):
        """_build_expense_agent() が Agent インスタンスを返すこと"""
        with patch("agents.expense_agent.create_specialist_agent") as mock_create:
            mock_create.return_value = MagicMock(spec=Agent)
            from agents.expense_agent import _build_expense_agent
            result = _build_expense_agent(
                session_id="test",
                applicant_name="山田太郎",
                application_date="2026-01-15",
                deadline="2025-10-15",
            )
            mock_create.assert_called_once()
            assert result is not None

    def test_expense_agent_tool_returns_string(self):
        """expense_agent ツール関数が文字列を返すこと"""
        mock_agent = MagicMock()
        mock_agent.return_value = "経費申請書を生成しました"

        def mock_build(session_id, applicant_name, application_date, deadline):
            return mock_agent

        ctx = MagicMock()
        ctx.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-01-15",
            "session_id": "test_session",
        }

        with patch("agents.expense_agent._build_expense_agent", mock_build):
            from agents.expense_agent import expense_agent
            result = expense_agent.__wrapped__(query="経費申請", tool_context=ctx)
            assert isinstance(result, str)
