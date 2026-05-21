"""エージェント共通ユーティリティの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
from strands import Agent
from agents.base_agent import calculate_deadline, create_specialist_agent, invoke_specialist_agent
from handlers.error_handler import LoopLimitError


class TestCalculateDeadline:
    """calculate_deadline のテスト"""

    def test_valid_date(self):
        """calculate_deadline("2026-01-15", 3) が "2025-10-15" を返すこと"""
        result = calculate_deadline("2026-01-15", 3)
        assert result == "2025-10-15"

    def test_invalid_date_returns_yoyo_kakunin(self):
        """calculate_deadline("invalid", 3) が "要確認" を返すこと"""
        result = calculate_deadline("invalid", 3)
        assert result == "要確認"

    def test_month_boundary(self):
        """月末日の計算が正しいこと"""
        result = calculate_deadline("2026-03-31", 3)
        assert result == "2025-12-31"


class TestCreateSpecialistAgent:
    """create_specialist_agent のテスト"""

    @patch("agents.base_agent.SessionManagerFactory.create_session_manager")
    @patch("agents.base_agent.ModelConfig.get_model")
    def test_returns_agent_instance(self, mock_get_model, mock_create_session):
        """create_specialist_agent() が Agent インスタンスを返すこと"""
        mock_get_model.return_value = MagicMock()
        mock_create_session.return_value = MagicMock()

        agent = create_specialist_agent(
            session_id="test_session",
            system_prompt="テストプロンプト",
            tools=[],
            agent_name="テストエージェント",
            window_size=15,
            max_iterations=10,
            max_attempts=6,
            initial_delay=4,
            max_delay=240,
        )
        assert isinstance(agent, Agent)


class TestInvokeSpecialistAgent:
    """invoke_specialist_agent のテスト"""

    def _make_tool_context(self):
        ctx = MagicMock()
        ctx.invocation_state = {
            "applicant_name": "山田太郎",
            "application_date": "2026-01-15",
            "session_id": "test_session",
        }
        return ctx

    def test_returns_string(self):
        """invoke_specialist_agent() が文字列を返すこと"""
        mock_agent = MagicMock()
        mock_agent.return_value = "テスト応答"

        def build_agent(session_id, applicant_name, application_date, deadline):
            return mock_agent

        ctx = self._make_tool_context()
        result = invoke_specialist_agent(
            query="テストクエリ",
            tool_context=ctx,
            agent_id="AG-TEST",
            deadline_months=3,
            build_agent=build_agent,
        )
        assert isinstance(result, str)

    def test_loop_limit_error_returns_error_message(self):
        """LoopLimitError 発生時にエラーメッセージ文字列が返ること"""
        def build_agent(session_id, applicant_name, application_date, deadline):
            mock_agent = MagicMock()
            mock_agent.side_effect = LoopLimitError(10, 10, "テストエージェント")
            return mock_agent

        ctx = self._make_tool_context()
        result = invoke_specialist_agent(
            query="テストクエリ",
            tool_context=ctx,
            agent_id="AG-TEST",
            deadline_months=3,
            build_agent=build_agent,
        )
        assert isinstance(result, str)
        assert len(result) > 0
