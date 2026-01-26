"""ツール関連のテスト"""
import pytest
import os
import json
from datetime import datetime
from tools.fare_tools import load_fare_data, calculate_fare
from tools.validation_tools import validate_input
from tools.excel_generator import travel_excel_generator


class TestFareTools:
    """運賃計算ツールのテスト"""
    
    def test_load_fare_data(self):
        """運賃データの読み込みテスト"""
        result = load_fare_data()
        
        assert result["success"] is True
        assert "train_fares" in result
        assert "fixed_fares" in result
        assert len(result["train_fares"]) > 0
        assert "bus" in result["fixed_fares"]
    
    def test_calculate_fare_train_valid(self):
        """電車運賃の計算テスト（有効な経路）"""
        result = calculate_fare(
            departure="渋谷",
            destination="東京",
            transport_type="train"
        )
        
        assert result["success"] is True
        assert result["cost"] > 0
        assert result["transport_type"] == "train"
    
    def test_calculate_fare_train_invalid_route(self):
        """電車運賃の計算テスト（無効な経路）"""
        result = calculate_fare(
            departure="存在しない駅A",
            destination="存在しない駅B",
            transport_type="train"
        )
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_calculate_fare_bus(self):
        """バス運賃の計算テスト"""
        result = calculate_fare(
            departure="渋谷",
            destination="新宿",
            transport_type="bus"
        )
        
        assert result["success"] is True
        assert result["cost"] == 220
        assert result["transport_type"] == "bus"
    
    def test_calculate_fare_taxi(self):
        """タクシー運賃の計算テスト"""
        result = calculate_fare(
            departure="渋谷",
            destination="新宿",
            transport_type="taxi"
        )
        
        assert result["success"] is True
        assert result["cost"] == 1500
        assert result["transport_type"] == "taxi"
    
    def test_calculate_fare_airplane(self):
        """飛行機運賃の計算テスト"""
        result = calculate_fare(
            departure="東京",
            destination="大阪",
            transport_type="airplane"
        )
        
        assert result["success"] is True
        assert result["cost"] == 15000
        assert result["transport_type"] == "airplane"
    
    def test_calculate_fare_invalid_transport(self):
        """無効な交通手段のテスト"""
        result = calculate_fare(
            departure="渋谷",
            destination="東京",
            transport_type="invalid_type"
        )
        
        assert result["success"] is False
        assert "無効な交通手段" in result["message"]


class TestValidationTools:
    """入力検証ツールのテスト"""
    
    def test_validate_date_valid(self):
        """有効な日付の検証テスト"""
        result = validate_input(
            input_type="date",
            value="2025-01-15"
        )
        
        assert result["valid"] is True
    
    def test_validate_date_invalid_format(self):
        """無効な日付形式の検証テスト"""
        result = validate_input(
            input_type="date",
            value="2025/01/15"
        )
        
        assert result["valid"] is False
        assert "YYYY-MM-DD" in result["message"]
    
    def test_validate_date_future(self):
        """未来の日付の検証テスト"""
        future_date = "2030-12-31"
        result = validate_input(
            input_type="date",
            value=future_date
        )
        
        assert result["valid"] is False
        assert "未来の日付" in result["message"]
    
    def test_validate_location_valid(self):
        """有効な場所の検証テスト"""
        result = validate_input(
            input_type="location",
            value="東京駅"
        )
        
        assert result["valid"] is True
    
    def test_validate_location_empty(self):
        """空の場所の検証テスト"""
        result = validate_input(
            input_type="location",
            value=""
        )
        
        assert result["valid"] is False
        assert "空" in result["message"]
    
    def test_validate_amount_valid(self):
        """有効な金額の検証テスト"""
        result = validate_input(
            input_type="amount",
            value="1000"
        )
        
        assert result["valid"] is True
    
    def test_validate_amount_negative(self):
        """負の金額の検証テスト"""
        result = validate_input(
            input_type="amount",
            value="-500"
        )
        
        assert result["valid"] is False
        assert "正の数値" in result["message"]
    
    def test_validate_amount_invalid(self):
        """無効な金額形式の検証テスト"""
        result = validate_input(
            input_type="amount",
            value="abc"
        )
        
        assert result["valid"] is False
        assert "数値" in result["message"]


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
        result = travel_excel_generator(
            routes=sample_routes,
            user_id="test001"
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
        result = travel_excel_generator(
            routes=[],
            user_id="test003"
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
        
        result = travel_excel_generator(
            routes=invalid_routes,
            user_id="test005"
        )
        
        assert result["success"] is False
        assert "不足" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
