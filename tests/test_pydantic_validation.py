"""Pydanticバリデーション機能の具体的なテスト"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from models.data_models import RouteInput, FareData, TrainFareRoute, InvocationState


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
            RouteInput(
                departure="",  # エラー1: 空の出発地
                destination="東京",
                date="2025-13-45",  # エラー2: 無効な日付
                transport_type="car",  # エラー3: 無効な交通手段
                cost=-100.0  # エラー4: 負の費用
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



class TestInvocationStateValidation:
    """InvocationStateモデルのバリデーションテスト"""
    
    def test_valid_invocation_state(self):
        """正常なinvocation_stateの検証"""
        state = InvocationState(
            applicant_name="田中太郎",
            application_date="2025-01-15",
            session_id="abc123"
        )
        assert state.applicant_name == "田中太郎"
        assert state.application_date == "2025-01-15"
        assert state.session_id == "abc123"
        print("✅ 正常なinvocation_stateは問題なく作成できる")
    
    def test_valid_invocation_state_without_session_id(self):
        """session_idなしの正常なinvocation_stateの検証"""
        state = InvocationState(
            applicant_name="田中太郎",
            application_date="2025-01-15"
        )
        assert state.applicant_name == "田中太郎"
        assert state.application_date == "2025-01-15"
        assert state.session_id is None
        print("✅ session_idなしでも作成できる")
    
    def test_empty_applicant_name(self):
        """空の申請者名の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="",  # 空文字列は許可されない
                application_date="2025-01-15"
            )
        
        error = exc_info.value.errors()[0]
        assert "applicant_name" in str(error["loc"])
        print(f"✅ 空の申請者名を検出: {error['msg']}")
    
    def test_invalid_date_format(self):
        """無効な日付形式の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="田中太郎",
                application_date="2025/01/15"  # スラッシュ区切りは無効
            )
        
        error = exc_info.value.errors()[0]
        assert "application_date" in str(error["loc"])
        assert "YYYY-MM-DD" in str(error["msg"])
        print(f"✅ 無効な日付形式を検出: {error['msg']}")
    
    def test_invalid_date_value(self):
        """無効な日付値の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="田中太郎",
                application_date="2025-13-45"  # 存在しない日付
            )
        
        error = exc_info.value.errors()[0]
        assert "application_date" in str(error["loc"])
        print(f"✅ 無効な日付値を検出: {error['msg']}")
    
    def test_missing_required_field(self):
        """必須フィールドの欠落検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="田中太郎"
                # application_date が欠落
            )
        
        error = exc_info.value.errors()[0]
        assert "application_date" in str(error["loc"])
        assert "missing" in error["type"] or "required" in error["type"]
        print(f"✅ 必須フィールドの欠落を検出: {error['msg']}")
    
    def test_wrong_type_applicant_name(self):
        """申請者名に数値が渡された場合の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name=12345,  # 数値は許可されない
                application_date="2025-01-15"
            )
        
        error = exc_info.value.errors()[0]
        assert "applicant_name" in str(error["loc"])
        print(f"✅ 不正な型（数値）を検出: {error['msg']}")
    
    def test_wrong_type_application_date(self):
        """申請日に数値が渡された場合の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="田中太郎",
                application_date=20250115  # 数値は許可されない
            )
        
        error = exc_info.value.errors()[0]
        assert "application_date" in str(error["loc"])
        print(f"✅ 不正な型（数値）を検出: {error['msg']}")
    
    def test_list_as_applicant_name(self):
        """申請者名にリストが渡された場合の検証"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name=["田中", "太郎"],  # リストは許可されない
                application_date="2025-01-15"
            )
        
        error = exc_info.value.errors()[0]
        assert "applicant_name" in str(error["loc"])
        print(f"✅ 不正な型（リスト）を検出: {error['msg']}")
    
    def test_dict_as_invocation_state(self):
        """辞書からInvocationStateへの変換テスト"""
        data = {
            "applicant_name": "田中太郎",
            "application_date": "2025-01-15",
            "session_id": "abc123"
        }
        
        state = InvocationState(**data)
        assert state.applicant_name == "田中太郎"
        assert state.application_date == "2025-01-15"
        assert state.session_id == "abc123"
        print("✅ 辞書からの変換が正常に機能")
    
    def test_multiple_validation_errors(self):
        """複数のバリデーションエラーを同時に検出"""
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(
                applicant_name="",  # エラー1: 空の申請者名
                application_date="2025/01/15"  # エラー2: 無効な日付形式
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2  # 複数のエラーが検出される
        
        print(f"✅ 複数のエラーを同時に検出: {len(errors)}個")
        for error in errors:
            print(f"   - {error['loc']}: {error['msg']}")
