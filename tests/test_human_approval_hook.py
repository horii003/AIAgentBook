"""
Human Approval Hookのテスト
"""

import pytest
from unittest.mock import Mock, patch
from handlers.human_approval_hook import HumanApprovalHook
from strands.hooks import BeforeToolCallEvent


class TestHumanApprovalHook:
    """HumanApprovalHookのテストクラス"""
    
    def test_approval_hook_initialization(self):
        """フックの初期化テスト"""
        hook = HumanApprovalHook()
        assert hook is not None
        assert hook.approval_callback is not None
    
    def test_approval_hook_with_custom_callback(self):
        """カスタムコールバックでの初期化テスト"""
        def custom_callback(tool_name, tool_params):
            return True, ""
        
        hook = HumanApprovalHook(approval_callback=custom_callback)
        assert hook.approval_callback == custom_callback
    
    def test_request_approval_for_receipt_excel_generator_approved(self):
        """receipt_excel_generatorツールの承認テスト"""
        # モックコールバック（承認）
        def mock_callback(tool_name, tool_params):
            return True, ""
        
        hook = HumanApprovalHook(approval_callback=mock_callback)
        
        # モックイベントの作成
        event = Mock(spec=BeforeToolCallEvent)
        event.tool_use = {
            "name": "receipt_excel_generator",
            "input": {
                "store_name": "テスト店舗",
                "amount": 1000,
                "date": "2024-01-01",
                "items": ["商品A"],
                "expense_category": "事務用品費"
            }
        }
        event.cancel_tool = None
        
        # 承認リクエストを実行
        hook.request_approval(event)
        
        # ツールがキャンセルされていないことを確認
        assert event.cancel_tool is None
    
    def test_request_approval_for_receipt_excel_generator_rejected(self):
        """receipt_excel_generatorツールのキャンセルテスト"""
        # モックコールバック（キャンセル）
        def mock_callback(tool_name, tool_params):
            return False, "CANCEL"
        
        hook = HumanApprovalHook(approval_callback=mock_callback)
        
        # モックイベントの作成
        event = Mock(spec=BeforeToolCallEvent)
        event.tool_use = {
            "name": "receipt_excel_generator",
            "input": {
                "store_name": "テスト店舗",
                "amount": 1000,
                "date": "2024-01-01",
                "items": ["商品A"],
                "expense_category": "事務用品費"
            }
        }
        event.cancel_tool = None
        
        # 承認リクエストを実行
        hook.request_approval(event)
        
        # ツールがキャンセルされていることを確認
        assert event.cancel_tool is not None
        assert "キャンセルしました" in event.cancel_tool
        assert "承知いたしました" in event.cancel_tool
    
    def test_request_approval_for_receipt_excel_generator_with_feedback(self):
        """receipt_excel_generatorツールの修正要望テスト"""
        # モックコールバック（修正要望）
        def mock_callback(tool_name, tool_params):
            return False, "金額を2000円に修正してください"
        
        hook = HumanApprovalHook(approval_callback=mock_callback)
        
        # モックイベントの作成
        event = Mock(spec=BeforeToolCallEvent)
        event.tool_use = {
            "name": "receipt_excel_generator",
            "input": {
                "store_name": "テスト店舗",
                "amount": 1000,
                "date": "2024-01-01",
                "items": ["商品A"],
                "expense_category": "事務用品費"
            }
        }
        event.cancel_tool = None
        
        # 承認リクエストを実行
        hook.request_approval(event)
        
        # ツールがキャンセルされ、修正要望が含まれていることを確認
        assert event.cancel_tool is not None
        assert "修正要望" in event.cancel_tool
        assert "金額を2000円に修正してください" in event.cancel_tool
    
    def test_request_approval_for_travel_excel_generator_approved(self):
        """travel_excel_generatorツールの承認テスト"""
        # モックコールバック（承認）
        def mock_callback(tool_name, tool_params):
            return True, ""
        
        hook = HumanApprovalHook(approval_callback=mock_callback)
        
        # モックイベントの作成
        event = Mock(spec=BeforeToolCallEvent)
        event.tool_use = {
            "name": "travel_excel_generator",
            "input": {
                "routes": [
                    {
                        "departure": "東京",
                        "destination": "大阪",
                        "date": "2024-01-01",
                        "transport_type": "train",
                        "cost": 13000
                    }
                ]
            }
        }
        event.cancel_tool = None
        
        # 承認リクエストを実行
        hook.request_approval(event)
        
        # ツールがキャンセルされていないことを確認
        assert event.cancel_tool is None
    
    def test_request_approval_for_other_tools(self):
        """他のツールは承認チェックをスキップすることを確認"""
        # モックコールバック（常にキャンセル）
        def mock_callback(tool_name, tool_params):
            return False, "キャンセル"
        
        hook = HumanApprovalHook(approval_callback=mock_callback)
        
        # モックイベントの作成（他のツール）
        event = Mock(spec=BeforeToolCallEvent)
        event.tool_use = {
            "name": "calculate_fare",
            "input": {
                "departure": "東京",
                "destination": "大阪"
            }
        }
        event.cancel_tool = None
        
        # 承認リクエストを実行
        hook.request_approval(event)
        
        # ツールがキャンセルされていないことを確認（承認チェックがスキップされる）
        assert event.cancel_tool is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
