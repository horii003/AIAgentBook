"""データモデル定義の単体テスト"""
import pytest
from pydantic import ValidationError

from models.data_models import (
    InvocationState,
    normalize_expense_category,
    normalize_transport_type,
    validate_date_format,
)


class TestValidateDateFormat:
    """validate_date_format のテスト"""

    def test_valid_date(self):
        """有効な日付文字列を受け入れること"""
        result = validate_date_format(None, "2026-05-21")
        assert result == "2026-05-21"

    def test_invalid_format_slash(self):
        """スラッシュ区切りの日付を拒否すること"""
        with pytest.raises(ValueError):
            validate_date_format(None, "2026/05/21")

    def test_invalid_month(self):
        """無効な月（13月）を拒否すること"""
        with pytest.raises(ValueError):
            validate_date_format(None, "2026-13-01")

    def test_invalid_string(self):
        """日付でない文字列を拒否すること"""
        with pytest.raises(ValueError):
            validate_date_format(None, "not-a-date")

    def test_valid_date_boundary(self):
        """年末日付が有効であること"""
        result = validate_date_format(None, "2026-12-31")
        assert result == "2026-12-31"


class TestNormalizeTransportType:
    """normalize_transport_type のテスト"""

    def test_train_english(self):
        """'train' が '電車' に正規化されること"""
        assert normalize_transport_type(None, "train") == "電車"

    def test_bus_english(self):
        """'bus' が 'バス' に正規化されること"""
        assert normalize_transport_type(None, "bus") == "バス"

    def test_taxi_english(self):
        """'taxi' が 'タクシー' に正規化されること"""
        assert normalize_transport_type(None, "taxi") == "タクシー"

    def test_airplane_english(self):
        """'airplane' が '飛行機' に正規化されること"""
        assert normalize_transport_type(None, "airplane") == "飛行機"

    def test_plane_english(self):
        """'plane' が '飛行機' に正規化されること"""
        assert normalize_transport_type(None, "plane") == "飛行機"

    def test_japanese_passthrough(self):
        """日本語表記はそのまま返すこと"""
        assert normalize_transport_type(None, "電車") == "電車"

    def test_unknown_passthrough(self):
        """未知の値はそのまま返すこと"""
        assert normalize_transport_type(None, "自転車") == "自転車"


class TestNormalizeExpenseCategory:
    """normalize_expense_category のテスト"""

    def test_office_supplies(self):
        """'office_supplies' が '事務用品費' に正規化されること"""
        assert normalize_expense_category(None, "office_supplies") == "事務用品費"

    def test_accommodation(self):
        """'accommodation' が '宿泊費' に正規化されること"""
        assert normalize_expense_category(None, "accommodation") == "宿泊費"

    def test_qualification(self):
        """'qualification' が '資格精算費' に正規化されること"""
        assert normalize_expense_category(None, "qualification") == "資格精算費"

    def test_other_english(self):
        """'other' が 'その他経費' に正規化されること"""
        assert normalize_expense_category(None, "other") == "その他経費"

    def test_other_japanese(self):
        """'その他' が 'その他経費' に正規化されること"""
        assert normalize_expense_category(None, "その他") == "その他経費"

    def test_japanese_passthrough(self):
        """日本語表記はそのまま返すこと"""
        assert normalize_expense_category(None, "事務用品費") == "事務用品費"


class TestInvocationState:
    """InvocationState モデルのテスト"""

    def test_valid_state(self):
        """有効なフィールドでインスタンスが生成されること"""
        state = InvocationState(
            user_name="山田太郎",
            request_date="2026-05-21",
            session_id="20260521_120000_abcd1234",
        )
        assert state.user_name == "山田太郎"
        assert state.request_date == "2026-05-21"
        assert state.session_id == "20260521_120000_abcd1234"

    def test_missing_user_name(self):
        """user_name が欠けている場合にValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            InvocationState(
                request_date="2026-05-21",
                session_id="20260521_120000_abcd1234",
            )

    def test_missing_request_date(self):
        """request_date が欠けている場合にValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            InvocationState(
                user_name="山田太郎",
                session_id="20260521_120000_abcd1234",
            )

    def test_missing_session_id(self):
        """session_id が欠けている場合にValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            InvocationState(
                user_name="山田太郎",
                request_date="2026-05-21",
            )

    def test_invalid_request_date_format(self):
        """不正な日付形式でValidationErrorが発生すること"""
        with pytest.raises(ValidationError):
            InvocationState(
                user_name="山田太郎",
                request_date="2026/05/21",
                session_id="20260521_120000_abcd1234",
            )

    def test_model_dump(self):
        """model_dump()が辞書を返すこと"""
        state = InvocationState(
            user_name="山田太郎",
            request_date="2026-05-21",
            session_id="20260521_120000_abcd1234",
        )
        dumped = state.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["user_name"] == "山田太郎"
        assert dumped["request_date"] == "2026-05-21"
        assert dumped["session_id"] == "20260521_120000_abcd1234"
