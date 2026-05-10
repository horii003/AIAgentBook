"""データモデルの単体テスト"""
import pytest
from pydantic import ValidationError
from models.data_models import (
    TransportCalculatorInput,
    TransportItem,
    TransportFormInput,
    ExpenseItem,
    ExpenseFormInput,
    validate_station_name,
    validate_transport_type,
    validate_expense_category,
    validate_date_format,
)


class TestValidateStationName:
    def test_removes_station_suffix(self):
        assert validate_station_name("東京駅") == "東京"

    def test_removes_bus_stop_suffix(self):
        assert validate_station_name("新宿バス停") == "新宿"

    def test_removes_airport_suffix(self):
        assert validate_station_name("羽田空港") == "羽田"

    def test_no_suffix(self):
        assert validate_station_name("東京") == "東京"


class TestValidateTransportType:
    def test_train_english(self):
        assert validate_transport_type("train") == "電車"

    def test_taxi_english(self):
        assert validate_transport_type("taxi") == "タクシー"

    def test_airplane_english(self):
        assert validate_transport_type("airplane") == "飛行機"

    def test_bus_english(self):
        assert validate_transport_type("bus") == "バス"

    def test_unknown_passthrough(self):
        assert validate_transport_type("自転車") == "自転車"


class TestValidateExpenseCategory:
    def test_stationery_normalization(self):
        assert validate_expense_category("事務用品") == "事務用品費"

    def test_hotel_normalization(self):
        assert validate_expense_category("ホテル") == "宿泊費"

    def test_qualification_normalization(self):
        assert validate_expense_category("資格") == "資格精算費"

    def test_other_normalization(self):
        assert validate_expense_category("その他") == "その他経費"

    def test_unknown_passthrough(self):
        assert validate_expense_category("交際費") == "交際費"


class TestValidateDateFormat:
    def test_valid_date(self):
        assert validate_date_format("2026-05-10") == "2026-05-10"

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            validate_date_format("2026/05/10")


class TestTransportCalculatorInput:
    def test_valid_input(self):
        # TC-UNIT-020
        obj = TransportCalculatorInput(
            departure="東京", destination="大阪",
            transport_type="電車", travel_date="2026-05-10"
        )
        assert obj.transport_type == "電車"

    def test_transport_type_normalization(self):
        # TC-UNIT-021
        obj = TransportCalculatorInput(
            departure="東京", destination="大阪",
            transport_type="train", travel_date="2026-05-10"
        )
        assert obj.transport_type == "電車"

    def test_invalid_transport_type(self):
        # TC-UNIT-022
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="東京", destination="大阪",
                transport_type="自転車", travel_date="2026-05-10"
            )

    def test_station_name_normalization(self):
        # TC-UNIT-023
        obj = TransportCalculatorInput(
            departure="東京駅", destination="大阪駅",
            transport_type="電車", travel_date="2026-05-10"
        )
        assert obj.departure == "東京"
        assert obj.destination == "大阪"

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="東京", destination="大阪",
                transport_type="電車", travel_date="2026/05/10"
            )


class TestExpenseItem:
    def test_valid_expense_category(self):
        # TC-UNIT-024
        item = ExpenseItem(
            purchase_date="2026-05-10", item_name="ノート",
            amount=500, expense_category="事務用品費", purpose="業務用"
        )
        assert item.expense_category == "事務用品費"

    def test_expense_category_normalization(self):
        # TC-UNIT-025
        item = ExpenseItem(
            purchase_date="2026-05-10", item_name="ノート",
            amount=500, expense_category="事務用品", purpose="業務用"
        )
        assert item.expense_category == "事務用品費"

    def test_invalid_expense_category(self):
        # TC-UNIT-026
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-05-10", item_name="接待費",
                amount=5000, expense_category="交際費", purpose="業務用"
            )

    def test_empty_purpose_raises(self):
        # TC-UNIT-027
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-05-10", item_name="ノート",
                amount=500, expense_category="事務用品費", purpose=""
            )

    def test_zero_amount_valid(self):
        # TC-UNIT-029
        item = ExpenseItem(
            purchase_date="2026-05-10", item_name="ノート",
            amount=0, expense_category="事務用品費", purpose="業務用"
        )
        assert item.amount == 0

    def test_negative_amount_raises(self):
        # TC-UNIT-030
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-05-10", item_name="ノート",
                amount=-100, expense_category="事務用品費", purpose="業務用"
            )


class TestTransportFormInput:
    def test_empty_items_raises(self):
        # TC-UNIT-028
        with pytest.raises(ValidationError):
            TransportFormInput(
                applicant_name="田中太郎",
                application_date="2026-05-10",
                items=[]
            )

    def test_valid_input(self):
        obj = TransportFormInput(
            applicant_name="田中太郎",
            application_date="2026-05-10",
            items=[TransportItem(
                travel_date="2026-05-10", departure="東京", destination="大阪",
                transport_type="電車", fare=13240, purpose="出張"
            )]
        )
        assert obj.applicant_name == "田中太郎"
