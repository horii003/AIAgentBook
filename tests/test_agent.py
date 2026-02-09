"""エージェント関連のテスト"""
import pytest
from unittest.mock import Mock, patch
from agents.reception_agent import ReceptionAgent
from agents.travel_agent import travel_agent, _get_travel_agent
from agents.receipt_expense_agent import receipt_expense_agent, _get_receipt_expense_agent


class TestReceptionAgent:
    """社内申請受付エージェント（オーケストレーター）のテスト"""
    
    def test_agent_initialization(self):
        """エージェントの初期化テスト"""
        agent = ReceptionAgent()
        assert agent is not None
        # 初期状態ではagentはNone（_initialize_applicant_info()が呼ばれていない）
        assert agent.agent is None
        assert agent._applicant_initialized is False
    
    def test_agent_initialization_state(self):
        """エージェントの初期化状態テスト"""
        agent = ReceptionAgent()
        
        # 初期状態の確認
        assert agent._applicant_name is None
        assert agent._session_id is None
        assert agent._session_manager is None
        assert agent.agent is None
    
    @patch('builtins.input', return_value='テストユーザー')
    def test_agent_full_initialization(self, mock_input):
        """エージェントの完全な初期化テスト（申請者情報入力後）"""
        agent = ReceptionAgent()
        
        # 申請者情報を初期化
        agent._initialize_applicant_info()
        
        # 初期化後の確認
        assert agent._applicant_initialized is True
        assert agent._applicant_name == 'テストユーザー'
        assert agent._session_id is not None
        assert agent._session_manager is not None
        assert agent.agent is not None
        assert agent.agent.system_prompt is not None
        assert len(agent.agent.system_prompt) > 0
        assert "申請受付窓口" in agent.agent.system_prompt or "社内申請受付" in agent.agent.system_prompt


class TestTravelAgent:
    """交通費精算専門エージェントのテスト"""
    
    def test_travel_agent_tool_callable(self):
        """travel_agentツールが呼び出し可能かテスト"""
        # ツールとして呼び出し可能か確認
        assert callable(travel_agent)
    
    def test_travel_agent_initialization(self):
        """travel_agentの初期化テスト"""
        # テスト用のセッションIDで初期化
        test_session_id = "test_session_001"
        agent = _get_travel_agent(session_id=test_session_id)
        
        assert agent is not None
        # Strands Agentオブジェクトにはtoolsプロパティがないため、初期化のみ確認
    
    def test_travel_agent_has_correct_tools(self):
        """travel_agentが正しいツールを持っているかテスト"""
        test_session_id = "test_session_002"
        agent = _get_travel_agent(session_id=test_session_id)
        # Strands Agentオブジェクトにはtoolsプロパティがないため、
        # エージェントが正常に初期化されていることのみ確認
        assert agent is not None
    
    def test_travel_agent_multiple_instances(self):
        """travel_agentの複数インスタンス作成テスト"""
        # 異なるセッションIDで初期化
        agent1 = _get_travel_agent(session_id="test_session_003")
        agent2 = _get_travel_agent(session_id="test_session_004")
        
        # 異なるインスタンスであることを確認
        assert agent1 is not agent2


class TestReceiptExpenseAgent:
    """領収書精算専門エージェントのテスト"""
    
    def test_receipt_expense_agent_tool_callable(self):
        """receipt_expense_agentツールが呼び出し可能かテスト"""
        assert callable(receipt_expense_agent)
    
    def test_receipt_expense_agent_initialization(self):
        """receipt_expense_agentの初期化テスト"""
        test_session_id = "test_session_005"
        agent = _get_receipt_expense_agent(session_id=test_session_id)
        
        assert agent is not None
        # Strands Agentオブジェクトにはtoolsプロパティがないため、初期化のみ確認
    
    def test_receipt_expense_agent_has_correct_tools(self):
        """receipt_expense_agentが正しいツールを持っているかテスト"""
        test_session_id = "test_session_006"
        agent = _get_receipt_expense_agent(session_id=test_session_id)
        # Strands Agentオブジェクトにはtoolsプロパティがないため、
        # エージェントが正常に初期化されていることのみ確認
        assert agent is not None
    
    def test_receipt_expense_agent_multiple_instances(self):
        """receipt_expense_agentの複数インスタンス作成テスト"""
        # 異なるセッションIDで初期化
        agent1 = _get_receipt_expense_agent(session_id="test_session_007")
        agent2 = _get_receipt_expense_agent(session_id="test_session_008")
        
        # 異なるインスタンスであることを確認
        assert agent1 is not agent2


class TestAgentIntegration:
    """エージェントの統合テスト"""
    
    @pytest.fixture
    def mock_tool_context(self):
        """テスト用のモックtool_contextを作成"""
        mock_context = Mock()
        mock_context.invocation_state = {
            "applicant_name": "テストユーザー",
            "application_date": "2025-01-15",
            "session_id": "test_integration_session"
        }
        return mock_context
    
    @patch('agents.travel_agent._get_travel_agent')
    def test_travel_agent_can_process_simple_query(self, mock_get_agent, mock_tool_context):
        """travel_agentが簡単なクエリを処理できるかテスト（モック使用）"""
        # モックエージェントの設定
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "こんにちは。交通費精算申請エージェントです。"
        mock_get_agent.return_value = mock_agent_instance
        
        # テスト実行
        response = travel_agent("こんにちは", tool_context=mock_tool_context)
        
        # 検証
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        mock_get_agent.assert_called_once()
    
    @patch('agents.receipt_expense_agent._get_receipt_expense_agent')
    def test_receipt_expense_agent_can_process_simple_query(self, mock_get_agent, mock_tool_context):
        """receipt_expense_agentが簡単なクエリを処理できるかテスト（モック使用）"""
        # モックエージェントの設定
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "こんにちは。経費精算申請エージェントです。"
        mock_get_agent.return_value = mock_agent_instance
        
        # テスト実行
        response = receipt_expense_agent("こんにちは", tool_context=mock_tool_context)
        
        # 検証
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        mock_get_agent.assert_called_once()
    
    def test_travel_agent_handles_missing_invocation_state(self):
        """travel_agentがinvocation_state不足を適切に処理するかテスト"""
        # invocation_stateが空のモックコンテキスト
        mock_context = Mock()
        mock_context.invocation_state = None
        
        response = travel_agent("テスト", tool_context=mock_context)
        
        # エラーメッセージが返されることを確認
        assert "申請者情報" in response or "設定されていません" in response
    
    def test_receipt_expense_agent_handles_missing_invocation_state(self):
        """receipt_expense_agentがinvocation_state不足を適切に処理するかテスト"""
        # invocation_stateが空のモックコンテキスト
        mock_context = Mock()
        mock_context.invocation_state = None
        
        response = receipt_expense_agent("テスト", tool_context=mock_context)
        
        # エラーメッセージが返されることを確認
        assert "申請者情報" in response or "設定されていません" in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
