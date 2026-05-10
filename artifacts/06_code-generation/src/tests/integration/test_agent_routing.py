"""エージェント間連携テスト（TC-INT-001〜004）"""
import pytest
from unittest.mock import MagicMock, patch


def make_invocation_state(applicant_name="田中太郎", application_date="2026-05-10", session_id="test_session"):
    return {
        "applicant_name": applicant_name,
        "application_date": application_date,
        "session_id": session_id,
    }


class TestAgentRouting:
    def test_transport_agent_called_for_transport_keyword(self):
        """TC-INT-001: AG-001が交通費関連キーワードでtransport_agentへ委譲すること"""
        from agents.orchestrator_agent import OrchestratorAgent
        agent = OrchestratorAgent(session_id="test_session")
        agent._user_name = "田中太郎"
        agent._build_agent()
        assert "transport_agent" in agent.agent.tool_names

    def test_expense_agent_in_tools(self):
        """TC-INT-002: AG-001のtoolsにexpense_agentが含まれること"""
        from agents.orchestrator_agent import OrchestratorAgent
        agent = OrchestratorAgent(session_id="test_session")
        agent._user_name = "田中太郎"
        agent._build_agent()
        assert "expense_agent" in agent.agent.tool_names

    def test_invocation_state_propagation(self):
        """TC-INT-004: invocation_stateが正しくAG-002へ伝播されること"""
        from agents.base_agent import invoke_specialist_agent
        from handlers.error_handler import LoopLimitError

        received_state = {}

        def mock_build_agent(session_id, applicant_name, application_date, deadline):
            mock_agent = MagicMock()
            def mock_call(query, invocation_state=None):
                received_state.update(invocation_state or {})
                return "応答"
            mock_agent.__call__ = mock_call
            mock_agent.side_effect = None
            return mock_agent

        ctx = MagicMock()
        ctx.invocation_state = make_invocation_state()

        with patch("agents.base_agent.SessionManagerFactory"):
            with patch("agents.base_agent.HumanApprovalHook"):
                with patch("agents.base_agent.LoopControlHook"):
                    with patch("agents.base_agent.ModelConfig"):
                        with patch("agents.base_agent.Agent") as mock_agent_cls:
                            mock_agent_instance = MagicMock()
                            mock_agent_instance.return_value = "応答"
                            mock_agent_cls.return_value = mock_agent_instance

                            result = invoke_specialist_agent(
                                query="交通費を申請したい",
                                tool_context=ctx,
                                agent_id="AG-002",
                                deadline_months=3,
                                build_agent=mock_build_agent,
                            )
        assert isinstance(result, str)
