"""エージェント関連のテスト"""
import pytest
from agents.reception_agent import ReceptionAgent
from agents.travel_agent import travel_agent, reset_travel_agent, _get_travel_agent
from agents.receipt_expense_agent import receipt_expense_agent, reset_receipt_expense_agent, _get_receipt_expense_agent


class TestReceptionAgent:
    """社内申請受付エージェント（オーケストレーター）のテスト"""
    
    @pytest.fixture
    def agent(self):
        """テスト用のエージェントインスタンス"""
        return ReceptionAgent()
    
    def test_agent_initialization(self, agent):
        """エージェントの初期化テスト"""
        assert agent is not None
        assert agent.agent is not None
        assert len(agent.agent.tools) == 2  # 2つの専門エージェントが登録されている
    
    def test_agent_has_correct_tools(self, agent):
        """エージェントが正しいツール（専門エージェント）を持っているかテスト"""
        tool_names = [tool.__name__ for tool in agent.agent.tools]
        
        expected_tools = [
            "travel_agent",
            "receipt_expense_agent"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_agent_system_prompt(self, agent):
        """エージェントのシステムプロンプトが設定されているかテスト"""
        assert agent.agent.system_prompt is not None
        assert len(agent.agent.system_prompt) > 0
        assert "オーケストラレーター" in agent.agent.system_prompt or "社内申請受付" in agent.agent.system_prompt


class TestTravelAgent:
    """交通費精算専門エージェントのテスト"""
    
    def test_travel_agent_tool_callable(self):
        """travel_agentツールが呼び出し可能かテスト"""
        # リセットしてクリーンな状態から開始
        reset_travel_agent()
        
        # ツールとして呼び出し可能か確認
        assert callable(travel_agent)
    
    def test_travel_agent_initialization(self):
        """travel_agentの初期化テスト"""
        reset_travel_agent()
        
        agent = _get_travel_agent()
        
        assert agent is not None
        assert len(agent.tools) == 3  # calculate_fare, validate_input, generate_report
    
    def test_travel_agent_has_correct_tools(self):
        """travel_agentが正しいツールを持っているかテスト"""
        reset_travel_agent()
        
        agent = _get_travel_agent()
        tool_names = [tool.__name__ for tool in agent.tools]
        
        expected_tools = [
            "calculate_fare",
            "validate_input",
            "generate_report"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_travel_agent_reset(self):
        """travel_agentのリセット機能テスト"""
        # エージェントを初期化
        agent1 = _get_travel_agent()
        
        # リセット
        reset_travel_agent()
        
        # 再度初期化（新しいインスタンスが作成される）
        agent2 = _get_travel_agent()
        
        # 異なるインスタンスであることを確認
        assert agent1 is not agent2


class TestReceiptExpenseAgent:
    """領収書精算専門エージェントのテスト"""
    
    def test_receipt_expense_agent_tool_callable(self):
        """receipt_expense_agentツールが呼び出し可能かテスト"""
        reset_receipt_expense_agent()
        
        assert callable(receipt_expense_agent)
    
    def test_receipt_expense_agent_initialization(self):
        """receipt_expense_agentの初期化テスト"""
        reset_receipt_expense_agent()
        
        agent = _get_receipt_expense_agent()
        
        assert agent is not None
        assert len(agent.tools) == 3  # image_reader, excel_generator, config_updater
    
    def test_receipt_expense_agent_has_correct_tools(self):
        """receipt_expense_agentが正しいツールを持っているかテスト"""
        reset_receipt_expense_agent()
        
        agent = _get_receipt_expense_agent()
        tool_names = [tool.__name__ for tool in agent.tools]
        
        expected_tools = [
            "image_reader",
            "excel_generator",
            "config_updater"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_receipt_expense_agent_reset(self):
        """receipt_expense_agentのリセット機能テスト"""
        # エージェントを初期化
        agent1 = _get_receipt_expense_agent()
        
        # リセット
        reset_receipt_expense_agent()
        
        # 再度初期化（新しいインスタンスが作成される）
        agent2 = _get_receipt_expense_agent()
        
        # 異なるインスタンスであることを確認
        assert agent1 is not agent2


class TestAgentIntegration:
    """エージェントの統合テスト"""
    
    def test_travel_agent_can_process_simple_query(self):
        """travel_agentが簡単なクエリを処理できるかテスト"""
        # 注意: このテストは実際のLLMを呼び出すため、
        # AWS認証情報が必要で、実行に時間がかかります
        
        pytest.skip("LLM呼び出しが必要なため、手動テストで実行してください")
        
        # 実際のテストコード（手動実行用）
        # reset_travel_agent()
        # response = travel_agent("こんにちは")
        # assert response is not None
        # assert isinstance(response, str)
    
    def test_receipt_expense_agent_can_process_simple_query(self):
        """receipt_expense_agentが簡単なクエリを処理できるかテスト"""
        pytest.skip("LLM呼び出しが必要なため、手動テストで実行してください")
        
        # 実際のテストコード（手動実行用）
        # reset_receipt_expense_agent()
        # response = receipt_expense_agent("こんにちは")
        # assert response is not None
        # assert isinstance(response, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
