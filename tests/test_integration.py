"""統合テスト"""
import pytest
import os
import json
from agents.reception_agent import ReceptionAgent
from agents.travel_agent import travel_agent, reset_travel_agent
from agents.receipt_expense_agent import receipt_expense_agent, reset_receipt_expense_agent
from tools.fare_tools import calculate_fare
from tools.excel_generator import travel_excel_generator


class TestEndToEndWorkflow:
    """エンドツーエンドのワークフローテスト"""
    
    def test_complete_expense_report_workflow(self):
        """完全な交通費申請ワークフローのテスト"""
        # 1. 経路データの作成
        routes = []
        
        # 経路1: 渋谷 → 東京（電車）
        fare1 = calculate_fare(
            departure="渋谷",
            destination="東京",
            transport_type="train"
        )
        assert fare1["success"] is True
        
        routes.append({
            "departure": "渋谷",
            "destination": "東京",
            "date": "2025-01-15",
            "transport_type": "train",
            "cost": fare1["cost"],
            "notes": ""
        })
        
        # 経路2: 東京 → 新宿（バス）
        fare2 = calculate_fare(
            departure="東京",
            destination="新宿",
            transport_type="bus"
        )
        assert fare2["success"] is True
        
        routes.append({
            "departure": "東京",
            "destination": "新宿",
            "date": "2025-01-15",
            "transport_type": "bus",
            "cost": fare2["cost"],
            "notes": ""
        })
        
        # 2. 申請書の生成（Excel）
        result_excel = travel_excel_generator(
            routes=routes,
            user_id="integration_test"
        )
        
        assert result_excel["success"] is True
        assert os.path.exists(result_excel["file_path"])
        assert result_excel["total_cost"] == fare1["cost"] + fare2["cost"]
        
        # クリーンアップ
        if os.path.exists(result_excel["file_path"]):
            os.remove(result_excel["file_path"])
    
    def test_multiple_transport_types(self):
        """複数の交通手段を使用したワークフローのテスト"""
        routes = []
        
        # 電車
        fare_train = calculate_fare("渋谷", "東京", "train")
        routes.append({
            "departure": "渋谷",
            "destination": "東京",
            "date": "2025-01-15",
            "transport_type": "train",
            "cost": fare_train["cost"],
            "notes": ""
        })
        
        # バス
        fare_bus = calculate_fare("東京", "新宿", "bus")
        routes.append({
            "departure": "東京",
            "destination": "新宿",
            "date": "2025-01-15",
            "transport_type": "bus",
            "cost": fare_bus["cost"],
            "notes": ""
        })
        
        # タクシー
        fare_taxi = calculate_fare("新宿", "渋谷", "taxi")
        routes.append({
            "departure": "新宿",
            "destination": "渋谷",
            "date": "2025-01-15",
            "transport_type": "taxi",
            "cost": fare_taxi["cost"],
            "notes": ""
        })
        
        # 飛行機
        fare_airplane = calculate_fare("東京", "大阪", "airplane")
        routes.append({
            "departure": "東京",
            "destination": "大阪",
            "date": "2025-01-16",
            "transport_type": "airplane",
            "cost": fare_airplane["cost"],
            "notes": "出張"
        })
        
        # 申請書生成
        result = travel_excel_generator(
            routes=routes,
            user_id="multi_transport_test"
        )
        
        assert result["success"] is True
        expected_total = (
            fare_train["cost"] + 
            fare_bus["cost"] + 
            fare_taxi["cost"] + 
            fare_airplane["cost"]
        )
        assert result["total_cost"] == expected_total
        
        # クリーンアップ
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])


class TestMultiAgentIntegration:
    """マルチエージェント連携のテスト"""
    
    def test_orchestrator_initialization(self):
        """オーケストレーターの初期化テスト"""
        agent = ReceptionAgent()
        
        assert agent is not None
        assert agent.agent is not None
        assert len(agent.agent.tools) == 2
    
    def test_travel_agent_as_tool(self):
        """travel_agentがツールとして動作するかテスト"""
        # 注意: このテストは実際のLLMを呼び出すため、スキップします
        pytest.skip("LLM呼び出しが必要なため、手動テストで実行してください")
        
        # 実際のテストコード（手動実行用）
        # reset_travel_agent()
        # response = travel_agent("渋谷から東京まで電車で移動しました")
        # assert response is not None
        # assert isinstance(response, str)
    
    def test_receipt_expense_agent_as_tool(self):
        """receipt_expense_agentがツールとして動作するかテスト"""
        pytest.skip("LLM呼び出しが必要なため、手動テストで実行してください")
        
        # 実際のテストコード（手動実行用）
        # reset_receipt_expense_agent()
        # response = receipt_expense_agent("領収書の画像を処理したいです")
        # assert response is not None
        # assert isinstance(response, str)
    
    def test_agent_reset_functionality(self):
        """エージェントのリセット機能テスト"""
        # travel_agentのリセット
        reset_travel_agent()
        
        # receipt_expense_agentのリセット
        reset_receipt_expense_agent()
        
        # リセット後も再度使用可能であることを確認
        assert callable(travel_agent)
        assert callable(receipt_expense_agent)


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_invalid_route_handling(self):
        """無効な経路のエラーハンドリングテスト"""
        fare = calculate_fare(
            departure="存在しない駅A",
            destination="存在しない駅B",
            transport_type="train"
        )
        
        assert fare["success"] is False
        assert "見つかりません" in fare["message"]
    
    def test_invalid_format_handling(self):
        """無効なデータのエラーハンドリングテスト"""
        routes = [{
            "departure": "渋谷",
            "destination": "東京",
            "date": "2025-01-15",
            "transport_type": "train",
            "cost": 200,
            "notes": ""
        }]
        
        # 必須キーが不足している場合のテスト
        invalid_routes = [{"departure": "渋谷"}]
        result = travel_excel_generator(
            routes=invalid_routes,
            user_id="error_test"
        )
        
        assert result["success"] is False
        assert "不足" in result["message"]
    
    def test_empty_routes_handling(self):
        """空の経路データのエラーハンドリングテスト"""
        result = travel_excel_generator(
            routes=[],
            user_id="empty_test"
        )
        
        assert result["success"] is False
        assert "空" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
