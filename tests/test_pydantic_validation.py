"""Pydanticバリデーション機能の具体的なテスト"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from models.data_models import RouteData, RouteInput, ExpenseReport, FareData, TrainFareRoute


class TestRouteDataValidation:
    """RouteDataモデルのバリデーションテスト"""
    
    def test_valid_route_data(self):
        """正常なデータの検証"""
        route = RouteData(
            departure="渋谷",
            destination="東京",
            date=datetime(2025, 1, 15),
            transport_type="train",
            cost=200.0
        )
        assert route.departure == "渋谷"
        assert route.cost == 200.0
        print("✅ 正常なデータは問題なく作成できる")
    
    def test_invalid_transport_type(self):
        """無効な交通手段の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="car",  # 無効な値（train/bus/taxi/airplaneのみ許可）
                cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "transport_type" in str(error["loc"])
        print(f"✅ 無効な交通手段を検出: {error['msg']}")
    
    def test_negative_cost(self):
        """負の費用の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=-100.0  # 負の値は許可されない
            )
        
        error = exc_info.value.errors()[0]
        assert "cost" in str(error["loc"])
        assert "0以上" in str(error["msg"]) or "greater than or equal" in str(error["msg"])
        print(f"✅ 負の費用を検出: {error['msg']}")
    
    def test_excessive_cost(self):
        """過大な費用の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=2000000.0  # 100万円を超える
            )
        
        error = exc_info.value.errors()[0]
        assert "cost" in str(error["loc"])
        assert "100万円" in str(error["msg"]) or "1000000" in str(error["msg"])
        print(f"✅ 過大な費用を検出: {error['msg']}")
    
    def test_empty_departure(self):
        """空の出発地の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="",  # 空文字列は許可されない
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "departure" in str(error["loc"])
        print(f"✅ 空の出発地を検出: {error['msg']}")
    
    def test_missing_required_field(self):
        """必須フィールドの欠落検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="渋谷",
                # destination が欠落
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "destination" in str(error["loc"])
        assert "missing" in error["type"] or "required" in error["type"]
        print(f"✅ 必須フィールドの欠落を検出: {error['msg']}")


class TestRouteInputValidation:
    """RouteInputモデルのバリデーションテスト（ツール入力用）"""
    
    def test_valid_route_input(self):
        """正常な入力データの検証"""
        route = RouteInput(
            departure="渋谷",
            destination="東京",
            date="2025-01-15",
            transport_type="train",
            cost=200.0
        )
        assert route.date == "2025-01-15"
        print("✅ 正常な入力データは問題なく作成できる")
    
    def test_invalid_date_format(self):
        """無効な日付形式の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteInput(
                departure="渋谷",
                destination="東京",
                date="2025/01/15",  # スラッシュ区切りは無効
                transport_type="train",
                cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "date" in str(error["loc"])
        assert "YYYY-MM-DD" in str(error["msg"])
        print(f"✅ 無効な日付形式を検出: {error['msg']}")
    
    def test_invalid_date_value(self):
        """無効な日付値の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteInput(
                departure="渋谷",
                destination="東京",
                date="2025-13-45",  # 存在しない日付
                transport_type="train",
                cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "date" in str(error["loc"])
        print(f"✅ 無効な日付値を検出: {error['msg']}")


class TestExpenseReportValidation:
    """ExpenseReportモデルのバリデーションテスト"""
    
    def test_valid_expense_report(self):
        """正常な申請書の検証"""
        routes = [
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=200.0
            )
        ]
        
        report = ExpenseReport(
            user_id="test001",
            report_date=datetime(2025, 1, 20),
            routes=routes,
            total_cost=200.0
        )
        
        assert report.user_id == "test001"
        assert len(report.routes) == 1
        print("✅ 正常な申請書は問題なく作成できる")
    
    def test_empty_user_id(self):
        """空のユーザーIDの検証"""
        routes = [
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=200.0
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseReport(
                user_id="",  # 空文字列は許可されない
                report_date=datetime(2025, 1, 20),
                routes=routes,
                total_cost=200.0
            )
        
        error = exc_info.value.errors()[0]
        assert "user_id" in str(error["loc"])
        print(f"✅ 空のユーザーIDを検出: {error['msg']}")
    
    def test_empty_routes_list(self):
        """空の経路リストの検証"""
        with pytest.raises(ValidationError) as exc_info:
            ExpenseReport(
                user_id="test001",
                report_date=datetime(2025, 1, 20),
                routes=[],  # 空のリストは許可されない
                total_cost=0.0
            )
        
        error = exc_info.value.errors()[0]
        assert "routes" in str(error["loc"])
        # Pydanticのエラーメッセージは英語または日本語
        assert "at least 1" in str(error["msg"]) or "空" in str(error["msg"])
        print(f"✅ 空の経路リストを検出: {error['msg']}")
    
    def test_negative_total_cost(self):
        """負の合計費用の検証"""
        routes = [
            RouteData(
                departure="渋谷",
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="train",
                cost=200.0
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseReport(
                user_id="test001",
                report_date=datetime(2025, 1, 20),
                routes=routes,
                total_cost=-100.0  # 負の値は許可されない
            )
        
        error = exc_info.value.errors()[0]
        assert "total_cost" in str(error["loc"])
        print(f"✅ 負の合計費用を検出: {error['msg']}")


class TestFareDataValidation:
    """FareDataモデルのバリデーションテスト"""
    
    def test_valid_fare_data(self):
        """正常な運賃データの検証"""
        fare_data = FareData(
            train_fares=[
                TrainFareRoute(departure="渋谷", destination="東京", fare=200.0)
            ],
            fixed_fares={
                "bus": 220,
                "taxi": 1500,
                "airplane": 15000
            }
        )
        
        assert len(fare_data.train_fares) == 1
        assert fare_data.fixed_fares["bus"] == 220
        print("✅ 正常な運賃データは問題なく作成できる")
    
    def test_missing_transport_type_in_fixed_fares(self):
        """固定運賃に必須の交通手段が欠落している検証"""
        with pytest.raises(ValidationError) as exc_info:
            FareData(
                train_fares=[
                    TrainFareRoute(departure="渋谷", destination="東京", fare=200.0)
                ],
                fixed_fares={
                    "bus": 220,
                    # taxi と airplane が欠落
                }
            )
        
        error = exc_info.value.errors()[0]
        assert "fixed_fares" in str(error["loc"])
        assert "taxi" in str(error["msg"]) or "airplane" in str(error["msg"])
        print(f"✅ 必須の交通手段の欠落を検出: {error['msg']}")
    
    def test_invalid_train_fare(self):
        """無効な電車運賃の検証"""
        with pytest.raises(ValidationError) as exc_info:
            FareData(
                train_fares=[
                    TrainFareRoute(departure="渋谷", destination="東京", fare=-100.0)  # 負の運賃
                ],
                fixed_fares={
                    "bus": 220,
                    "taxi": 1500,
                    "airplane": 15000
                }
            )
        
        error = exc_info.value.errors()[0]
        assert "fare" in str(error["loc"])
        print(f"✅ 無効な電車運賃を検出: {error['msg']}")


class TestMultipleErrorsValidation:
    """複数のエラーを同時に検出するテスト"""
    
    def test_multiple_validation_errors(self):
        """複数のバリデーションエラーを同時に検出"""
        with pytest.raises(ValidationError) as exc_info:
            RouteData(
                departure="",  # エラー1: 空の出発地
                destination="東京",
                date=datetime(2025, 1, 15),
                transport_type="car",  # エラー2: 無効な交通手段
                cost=-100.0  # エラー3: 負の費用
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2  # 複数のエラーが検出される
        
        error_fields = [str(error["loc"]) for error in errors]
        print(f"✅ 複数のエラーを同時に検出: {len(errors)}個")
        for error in errors:
            print(f"   - {error['loc']}: {error['msg']}")


class TestTypeCoercion:
    """型変換のテスト"""
    
    def test_string_to_float_coercion(self):
        """文字列から数値への自動変換"""
        route = RouteInput(
            departure="渋谷",
            destination="東京",
            date="2025-01-15",
            transport_type="train",
            cost="200"  # 文字列で渡しても自動的にfloatに変換される
        )
        
        assert isinstance(route.cost, float)
        assert route.cost == 200.0
        print("✅ 文字列から数値への自動変換が機能")
    
    def test_invalid_type_coercion(self):
        """変換できない型の検証"""
        with pytest.raises(ValidationError) as exc_info:
            RouteInput(
                departure="渋谷",
                destination="東京",
                date="2025-01-15",
                transport_type="train",
                cost="invalid_number"  # 数値に変換できない文字列
            )
        
        error = exc_info.value.errors()[0]
        assert "cost" in str(error["loc"])
        print(f"✅ 変換できない型を検出: {error['msg']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
