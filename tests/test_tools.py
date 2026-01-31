"""ツール関連のテスト"""
import pytest
import os
import json
from datetime import datetime
from unittest.mock import Mock
from tools.fare_tools import load_fare_data, calculate_fare
from tools.excel_generator import travel_excel_generator


class TestFareTools:
    """運賃計算ツールのテスト"""
    
    def test_load_fare_data(self):
        """運賃データの読み込みテスト"""
        result = load_fare_data()
        
        # Pydantic移行後は辞書形式で返される
        assert "train_fares" in result
        assert "fixed_fares" in result
        assert len(result["train_fares"]) > 0
        assert "bus" in result["fixed_fares"]
    
    def test_calculate_fare_train_valid(self):
        """電車運賃の計算テスト（有効な経路）"""
        result = calculate_fare(
            departure="渋谷",
            destination="東京",
            transport_type="train",
            date="2025-01-15"
        )
        
        # Pydantic移行後は辞書形式で返される
        assert "fare" in result
        assert result["fare"] > 0
        assert "calculation_method" in result
    
    def test_calculate_fare_train_invalid_route(self):
        """電車運賃の計算テスト（無効な経路）"""
        with pytest.raises(ValueError) as exc_info:
            calculate_fare(
                departure="存在しない駅A",
                destination="存在しない駅B",
                transport_type="train",
                date="2025-01-15"
            )
        
        assert "見つかりません" in str(exc_info.value)
    
    def test_calculate_fare_bus(self):
        """バス運賃の計算テスト"""
        result = calculate_fare(
            departure="渋谷",
            destination="新宿",
            transport_type="bus",
            date="2025-01-15"
        )
        
        assert "fare" in result
        assert result["fare"] == 220
    
    def test_calculate_fare_taxi(self):
        """タクシー運賃の計算テスト"""
        result = calculate_fare(
            departure="渋谷",
            destination="新宿",
            transport_type="taxi",
            date="2025-01-15"
        )
        
        assert "fare" in result
        assert result["fare"] == 1500
    
    def test_calculate_fare_airplane(self):
        """飛行機運賃の計算テスト"""
        result = calculate_fare(
            departure="東京",
            destination="大阪",
            transport_type="airplane",
            date="2025-01-15"
        )
        
        assert "fare" in result
        assert result["fare"] == 15000
    
    def test_calculate_fare_invalid_transport(self):
        """無効な交通手段のテスト"""
        with pytest.raises(ValueError) as exc_info:
            calculate_fare(
                departure="渋谷",
                destination="東京",
                transport_type="invalid_type",
                date="2025-01-15"
            )
        
        assert "無効な交通手段" in str(exc_info.value)


class TestExcelGeneratorTools:
    """Excel申請書生成ツールのテスト"""
    
    @pytest.fixture
    def sample_routes(self):
        """テスト用の経路データ"""
        return [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200,
                "notes": ""
            },
            {
                "departure": "東京",
                "destination": "新宿",
                "date": "2025-01-15",
                "transport_type": "bus",
                "cost": 220,
                "notes": ""
            }
        ]
    
    def test_generate_excel_report(self, sample_routes):
        """Excel申請書の生成テスト"""
        # モックのtool_contextを作成
        mock_context = Mock()
        mock_context.invocation_state = {"applicant_name": "test001"}
        
        result = travel_excel_generator(
            routes=sample_routes,
            tool_context=mock_context
        )
        
        assert result["success"] is True
        assert result["total_cost"] == 420
        assert os.path.exists(result["file_path"])
        assert result["file_path"].endswith(".xlsx")
        
        # テスト後のクリーンアップ
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])
    
    def test_generate_excel_empty_routes(self):
        """空の経路データでの申請書生成テスト"""
        # モックのtool_contextを作成
        mock_context = Mock()
        mock_context.invocation_state = {"applicant_name": "test003"}
        
        result = travel_excel_generator(
            routes=[],
            tool_context=mock_context
        )
        
        assert result["success"] is False
        assert "空" in result["message"]
    
    def test_generate_excel_missing_keys(self):
        """必須キーが不足している経路データのテスト"""
        invalid_routes = [
            {
                "departure": "渋谷",
                # destination が不足
                "transport_type": "train",
                "cost": 200
            }
        ]
        
        # モックのtool_contextを作成
        mock_context = Mock()
        mock_context.invocation_state = {"applicant_name": "test005"}
        
        result = travel_excel_generator(
            routes=invalid_routes,
            tool_context=mock_context
        )
        
        assert result["success"] is False
        # Pydanticのエラーメッセージに合わせて修正
        assert "データが不正" in result["message"] or "Field required" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
