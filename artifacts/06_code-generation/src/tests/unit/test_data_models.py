"""データモデル定義の単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from pydantic import ValidationError
from models.data_models import (
    InvocationState,
    TransportCalculatorInput,
    TransportCalculatorOutput,
    ExpenseItem,
    ExpenseReportInput,
    TransportItem,
    TransportReportInput,
    ReportOutput,
    TrainRouteRecord,
    validate_station_name,
    normalize_transport_type,
    validate_date_format,
)


class TestInvocationState:
    """InvocationState モデルのテスト"""

    def test_valid_all_fields(self):
        """全フィールド指定の正常系"""
        state = InvocationState(
            applicant_name="山田太郎",
            application_date="2026-01-15",
            session_id="20260115120000_abc12345",
        )
        assert state.applicant_name == "山田太郎"
        assert state.application_date == "2026-01-15"
        assert state.session_id == "20260115120000_abc12345"


class TestTransportCalculatorInput:
    """TransportCalculatorInput モデルのテスト"""

    def test_valid_input(self):
        """正常系バリデーション"""
        inp = TransportCalculatorInput(
            departure="渋谷",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-01-15",
        )
        assert inp.departure == "渋谷"
        assert inp.destination == "新宿"
        assert inp.transport_type == "電車"
        assert inp.travel_date == "2026-01-15"

    def test_station_name_normalization(self):
        """駅名正規化（末尾「駅」除去）"""
        inp = TransportCalculatorInput(
            departure="渋谷駅",
            destination="新宿駅",
            transport_type="電車",
            travel_date="2026-01-15",
        )
        assert inp.departure == "渋谷"
        assert inp.destination == "新宿"

    def test_transport_type_english_normalization(self):
        """英語表記の交通手段を日本語に正規化"""
        inp = TransportCalculatorInput(
            departure="渋谷",
            destination="新宿",
            transport_type="train",
            travel_date="2026-01-15",
        )
        assert inp.transport_type == "電車"

    def test_invalid_transport_type(self):
        """不正な交通手段でバリデーションエラー"""
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="渋谷",
                destination="新宿",
                transport_type="自転車",
                travel_date="2026-01-15",
            )


class TestExpenseItem:
    """ExpenseItem モデルのテスト"""

    def test_valid_expense_category(self):
        """許可された経費区分の正常系"""
        for category in ["事務用品費", "宿泊費", "資格精算費", "その他経費"]:
            item = ExpenseItem(
                purchase_date="2026-01-15",
                store_name="テスト店",
                item_name="テスト品目",
                expense_category=category,
                amount=1000,
                business_purpose="業務目的",
            )
            assert item.expense_category == category

    def test_invalid_expense_category(self):
        """不正な経費区分でバリデーションエラー"""
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-01-15",
                store_name="テスト店",
                item_name="テスト品目",
                expense_category="交通費",
                amount=1000,
                business_purpose="業務目的",
            )

    def test_amount_zero_valid(self):
        """金額0は許容される（ge=0）"""
        item = ExpenseItem(
            purchase_date="2026-01-15",
            store_name="テスト店",
            item_name="テスト品目",
            expense_category="事務用品費",
            amount=0,
            business_purpose="業務目的",
        )
        assert item.amount == 0

    def test_amount_negative_invalid(self):
        """負の金額はバリデーションエラー"""
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-01-15",
                store_name="テスト店",
                item_name="テスト品目",
                expense_category="事務用品費",
                amount=-1,
                business_purpose="業務目的",
            )


class TestTrainRouteRecord:
    """TrainRouteRecord モデルのテスト"""

    def test_valid_record(self):
        """正常系バリデーション"""
        record = TrainRouteRecord(departure="渋谷", destination="新宿", fare=200)
        assert record.departure == "渋谷"
        assert record.destination == "新宿"
        assert record.fare == 200

    def test_fare_zero_invalid(self):
        """運賃0はバリデーションエラー（gt=0）"""
        with pytest.raises(ValidationError):
            TrainRouteRecord(departure="渋谷", destination="新宿", fare=0)


class TestValidateStationName:
    """validate_station_name 共通バリデーター関数のテスト"""

    def test_remove_suffix_station(self):
        """末尾「駅」を除去する"""
        assert validate_station_name("渋谷駅") == "渋谷"

    def test_no_suffix(self):
        """「駅」なしはそのまま返す"""
        assert validate_station_name("渋谷") == "渋谷"

    def test_empty_string_raises(self):
        """空文字列はValueError"""
        with pytest.raises(ValueError):
            validate_station_name("")

    def test_whitespace_only_raises(self):
        """空白のみはValueError"""
        with pytest.raises(ValueError):
            validate_station_name("   ")
