"""実際のツールでのPydanticバリデーションの動作テスト"""
import pytest
from tools.excel_generator import transportation_excel_generator
from tools.fare_tools import load_fare_data, calculate_fare
from pydantic import ValidationError


class TestRealWorldExcelGeneratorValidation:
    """実際のExcel生成ツールでのバリデーションテスト"""
    
    def test_valid_routes_generation(self):
        """正常なデータでExcel生成が成功する"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0,
                "notes": "出張"
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is True
        assert result["total_cost"] == 200.0
        print("\n✅ 正常なデータでExcel生成成功")
        print(f"   ファイル: {result['file_path']}")
        print(f"   合計: ¥{result['total_cost']:,.0f}")
        
        # クリーンアップ
        import os
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])
    
    def test_invalid_transport_type_in_excel_generator(self):
        """無効な交通手段でエラーが返される"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "helicopter",  # ❌ 無効な交通手段
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "データが不正" in result["message"]
        assert "train" in result["message"] or "bus" in result["message"]
        print("\n❌ 無効な交通手段を検出")
        print(f"   エラーメッセージ: {result['message']}")
    
    def test_missing_required_fields_in_excel_generator(self):
        """必須フィールドが欠落している場合のエラー"""
        routes = [
            {
                "departure": "渋谷",
                # destination が欠落 ❌
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "destination" in result["message"]
        assert "Field required" in result["message"]
        print("\n❌ 必須フィールドの欠落を検出")
        print(f"   エラーメッセージ: {result['message']}")
    
    def test_invalid_date_format_in_excel_generator(self):
        """無効な日付形式でエラーが返される"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025/01/15",  # ❌ スラッシュ区切りは無効
                "transport_type": "train",
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "YYYY-MM-DD" in result["message"]
        print("\n❌ 無効な日付形式を検出")
        print(f"   エラーメッセージ: {result['message']}")
    
    def test_negative_cost_in_excel_generator(self):
        """負の費用でエラーが返される"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": -200.0  # ❌ 負の費用
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "greater than or equal to 0" in result["message"]
        print("\n❌ 負の費用を検出")
        print(f"   エラーメッセージ: {result['message']}")
    
    def test_string_cost_auto_conversion(self):
        """文字列の費用が自動的に数値に変換される"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": "200"  # 文字列で渡す
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is True
        assert result["total_cost"] == 200.0
        assert isinstance(result["total_cost"], float)
        print("\n✅ 文字列から数値への自動変換が機能")
        print(f"   入力: '200' (文字列)")
        print(f"   変換後: {result['total_cost']} (float)")
        
        # クリーンアップ
        import os
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])
    
    def test_multiple_routes_with_mixed_errors(self):
        """複数の経路で一部にエラーがある場合"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0
            },
            {
                "departure": "東京",
                "destination": "新宿",
                "date": "2025-01-15",
                "transport_type": "spaceship",  # ❌ 2番目の経路にエラー
                "cost": 300.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "経路2" in result["message"]  # 2番目の経路でエラー
        print("\n❌ 複数経路の中から問題のある経路を特定")
        print(f"   エラーメッセージ: {result['message']}")


class TestRealWorldFareToolsValidation:
    """実際の運賃計算ツールでのバリデーションテスト"""
    
    def test_valid_fare_calculation(self):
        """正常な運賃計算"""
        result = calculate_fare(
            departure="渋谷",
            destination="東京",
            transport_type="train",
            date="2025-01-15"
        )
        
        assert "fare" in result
        assert result["fare"] > 0
        print("\n✅ 正常な運賃計算が成功")
        print(f"   経路: 渋谷 → 東京")
        print(f"   運賃: ¥{result['fare']:,.0f}")
    
    def test_invalid_transport_type_in_fare_calculation(self):
        """無効な交通手段で例外が発生"""
        with pytest.raises(ValueError) as exc_info:
            calculate_fare(
                departure="渋谷",
                destination="東京",
                transport_type="submarine",  # ❌ 無効な交通手段
                date="2025-01-15"
            )
        
        assert "無効な交通手段" in str(exc_info.value)
        print("\n❌ 無効な交通手段を検出")
        print(f"   エラー: {exc_info.value}")
    
    def test_fare_data_loading_with_validation(self):
        """運賃データの読み込みとバリデーション"""
        result = load_fare_data()
        
        assert "train_fares" in result
        assert "fixed_fares" in result
        assert len(result["train_fares"]) > 0
        assert "bus" in result["fixed_fares"]
        assert "taxi" in result["fixed_fares"]
        assert "airplane" in result["fixed_fares"]
        print("\n✅ 運賃データの読み込みとバリデーション成功")
        print(f"   電車運賃データ: {len(result['train_fares'])}件")
        print(f"   固定運賃: {list(result['fixed_fares'].keys())}")


class TestEdgeCases:
    """エッジケースのテスト"""
    
    def test_empty_string_fields(self):
        """空文字列フィールドの検証"""
        routes = [
            {
                "departure": "",  # ❌ 空文字列
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "departure" in result["message"]
        assert "at least 1 character" in result["message"]
        print("\n❌ 空文字列フィールドを検出")
        print(f"   エラーメッセージ: {result['message']}")
    
    def test_whitespace_only_fields(self):
        """空白のみのフィールドの検証"""
        routes = [
            {
                "departure": "   ",  # 空白のみ
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        # Pydanticは空白を許可するが、実際のビジネスロジックで検証可能
        print("\n⚠️  空白のみのフィールド")
        print(f"   結果: {result['success']}")
        print(f"   メッセージ: {result.get('message', 'N/A')}")
    
    def test_very_large_cost(self):
        """非常に大きな費用の検証"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 999999999.0  # 非常に大きな値
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        # RouteInputには上限チェックがないため成功する
        # RouteDataには上限チェックがある
        print("\n⚠️  非常に大きな費用")
        print(f"   結果: {result['success']}")
        if result["success"]:
            print(f"   合計: ¥{result['total_cost']:,.0f}")
            # クリーンアップ
            import os
            if os.path.exists(result["file_path"]):
                os.remove(result["file_path"])
    
    def test_zero_cost(self):
        """費用が0の場合"""
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 0.0  # 0円
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is True
        assert result["total_cost"] == 0.0
        print("\n✅ 費用0円は許可される")
        print(f"   合計: ¥{result['total_cost']:,.0f}")
        
        # クリーンアップ
        import os
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])
    
    def test_unicode_characters_in_location(self):
        """ロケーション名にUnicode文字を使用"""
        routes = [
            {
                "departure": "東京駅🚉",  # 絵文字を含む
                "destination": "新宿駅🏢",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": 200.0
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is True
        print("\n✅ Unicode文字（絵文字）を含むロケーション名が許可される")
        print(f"   出発地: 東京駅🚉")
        print(f"   目的地: 新宿駅🏢")
        
        # クリーンアップ
        import os
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])


class TestComparisonWithManualValidation:
    """手動検証との比較テスト"""
    
    def test_manual_validation_would_miss_type_error(self):
        """手動検証では見逃しやすい型エラー"""
        # 従来の手動検証では、この種のエラーは実行時まで検出されない可能性がある
        routes = [
            {
                "departure": "渋谷",
                "destination": "東京",
                "date": "2025-01-15",
                "transport_type": "train",
                "cost": "invalid"  # ❌ 数値に変換できない文字列
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        assert "unable to parse" in result["message"] or "valid number" in result["message"]
        print("\n❌ 手動検証では見逃しやすい型エラーをPydanticが検出")
        print(f"   入力: 'invalid' (文字列)")
        print(f"   エラー: {result['message']}")
    
    def test_comprehensive_error_reporting(self):
        """包括的なエラーレポート"""
        routes = [
            {
                # departure が欠落 ❌
                "destination": "東京",
                "date": "invalid-date",  # ❌ 無効な日付
                "transport_type": "rocket",  # ❌ 無効な交通手段
                "cost": -100  # ❌ 負の費用
            }
        ]
        
        result = transportation_excel_generator(routes=routes, user_id="test001")
        
        assert result["success"] is False
        # Pydanticは複数のエラーを一度に報告する
        print("\n❌ 複数のエラーを包括的に報告")
        print(f"   エラーメッセージ: {result['message']}")
        print("   従来の手動検証では、最初のエラーで停止することが多い")
        print("   Pydanticは全てのエラーを一度に報告できる")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


