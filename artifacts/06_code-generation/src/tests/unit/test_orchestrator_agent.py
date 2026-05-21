"""オーケストレーターエージェントの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
from strands import Agent
from handlers.error_handler import LoopLimitError


class TestOrchestratorAgent:
    """OrchestratorAgent のテスト"""

    def _create_agent_with_mocks(self):
        """モックを使ってエージェントを作成するヘルパー。"""
        with patch("agents.orchestrator_agent.ModelConfig.get_model") as mock_model, \
             patch("agents.orchestrator_agent.SessionManagerFactory.create_session_manager") as mock_session, \
             patch("agents.expense_agent.create_specialist_agent") as mock_create_expense, \
             patch("agents.transport_agent.create_specialist_agent") as mock_create_transport:
            mock_model.return_value = MagicMock()
            mock_session.return_value = MagicMock()
            mock_create_expense.return_value = MagicMock(spec=Agent)
            mock_create_transport.return_value = MagicMock(spec=Agent)
            from agents.orchestrator_agent import OrchestratorAgent
            return OrchestratorAgent(applicant_name="山田太郎", session_id="test_session")

    def test_initialize_creates_agent(self):
        """_initialize() が Agent インスタンスを生成すること"""
        with patch("agents.orchestrator_agent.ModelConfig.get_model") as mock_model, \
             patch("agents.orchestrator_agent.SessionManagerFactory.create_session_manager") as mock_session:
            mock_model.return_value = MagicMock()
            mock_session.return_value = MagicMock()
            from agents.orchestrator_agent import OrchestratorAgent
            agent = OrchestratorAgent(applicant_name="山田太郎", session_id="test_session")
            assert isinstance(agent.agent, Agent)

    def test_run_exits_on_quit_command(self):
        """終了コマンドでループが終了すること"""
        with patch("agents.orchestrator_agent.ModelConfig.get_model") as mock_model, \
             patch("agents.orchestrator_agent.SessionManagerFactory.create_session_manager") as mock_session, \
             patch("builtins.input", return_value="quit"), \
             patch("builtins.print"):
            mock_model.return_value = MagicMock()
            mock_session.return_value = MagicMock()
            from agents.orchestrator_agent import OrchestratorAgent
            agent = OrchestratorAgent(applicant_name="山田太郎", session_id="test_session")
            agent.run()  # quit で終了するはず

    def test_run_shows_error_on_long_input(self):
        """500文字超の入力でエラーメッセージが表示されること"""
        long_input = "あ" * 501
        inputs = iter([long_input, "quit"])

        with patch("agents.orchestrator_agent.ModelConfig.get_model") as mock_model, \
             patch("agents.orchestrator_agent.SessionManagerFactory.create_session_manager") as mock_session, \
             patch("builtins.input", side_effect=inputs):
            mock_model.return_value = MagicMock()
            mock_session.return_value = MagicMock()
            printed = []
            with patch("builtins.print", side_effect=lambda *a, **k: printed.append(str(a))):
                from agents.orchestrator_agent import OrchestratorAgent
                agent = OrchestratorAgent(applicant_name="山田太郎", session_id="test_session")
                agent.run()
            assert any("500" in p for p in printed)

    def test_run_continues_on_loop_limit_error(self):
        """LoopLimitError 発生時にループが継続すること（continue）"""
        mock_agent_instance = MagicMock()
        mock_agent_instance.side_effect = [
            LoopLimitError(10, 10, "テスト"),
            "応答",
        ]

        inputs = iter(["交通費申請", "quit"])

        with patch("agents.orchestrator_agent.ModelConfig.get_model") as mock_model, \
             patch("agents.orchestrator_agent.SessionManagerFactory.create_session_manager") as mock_session, \
             patch("builtins.input", side_effect=inputs), \
             patch("builtins.print"):
            mock_model.return_value = MagicMock()
            mock_session.return_value = MagicMock()
            from agents.orchestrator_agent import OrchestratorAgent
            agent = OrchestratorAgent(applicant_name="山田太郎", session_id="test_session")
            agent.agent = mock_agent_instance
            agent.run()  # LoopLimitError 後も continue して quit で終了
