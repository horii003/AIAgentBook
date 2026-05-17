"""データモデルの単体テスト"""

import pytest
from pydantic import ValidationError

from models.data_models import (
    ExpenseItem,
    ExpenseReportInput,
    ReportOutput,
    TrainRouteRecord,
    TransportCalculatorInput,
    TransportCalculatorOutput,
    TransportItem,
    TransportReportInput,
    normalize_transport_type,
    validate_date_format,
    validate_station_name,
)


class TestValidateStationName:
    """validate_station_name のテスト"""

    def test_normal_station(self):
        assert validate_station_name("渋谷") == "渋谷"

    def test_remove_suffix(self):
        assert validate_station_name("渋谷駅") == "渋谷"

    def test_strip_whitespace(self):
        assert validate_station_name("  東京  ") == "東京"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            validate_station_name("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            validate_station_name("   ")


class TestNormalizeTransportType:
    """normalize_transport_type のテスト"""

    def test_japanese(self):
        assert normalize_transport_type("電車") == "電車"
        assert normalize_transport_type("バス") == "バス"

    def test_english(self):
        assert normalize_transport_type("train") == "電車"
        assert normalize_transport_type("bus") == "バス"
        assert normalize_transport_type("taxi") == "タクシー"
        assert normalize_transport_type("airplane") == "飛行機"
        assert normalize_transport_type("plane") == "飛行機"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            normalize_transport_type("自転車")


class TestValidateDateFormat:
    """validate_date_format のテスト"""

    def test_standard_format(self):
        assert validate_date_format("2026-05-17") == "2026-05-17"

    def test_slash_format(self):
        assert validate_date_format("2026/05/17") == "2026-05-17"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            validate_date_format("invalid-date")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            validate_date_format("")


class TestTransportCalculatorInput:
    """TransportCalculatorInput のテスト"""

    def test_valid_input(self):
        model = TransportCalculatorInput(
            departure="渋谷駅",
            destination="新宿",
            transport_type="train",
            travel_date="2026-05-17",
        )
        assert model.departure == "渋谷"
        assert model.destination == "新宿"
        assert model.transport_type == "電車"
        assert model.travel_date == "2026-05-17"

    def test_empty_departure_raises(self):
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="",
                destination="新宿",
                transport_type="電車",
                travel_date="2026-05-17",
            )

    def test_invalid_transport_type_raises(self):
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="渋谷",
                destination="新宿",
                transport_type="自転車",
                travel_date="2026-05-17",
            )

    def test_model_dump_normalized(self):
        model = TransportCalculatorInput(
            departure="渋谷駅",
            destination="東京駅",
            transport_type="train",
            travel_date="2026/05/17",
        )
        data = model.model_dump()
        assert data["departure"] == "渋谷"
        assert data["destination"] == "東京"
        assert data["transport_type"] == "電車"
        assert data["travel_date"] == "2026-05-17"


class TestTransportCalculatorOutput:
    """TransportCalculatorOutput のテスト"""

    def test_success(self):
        model = TransportCalculatorOutput(success=True, fare=200)
        assert model.success is True
        assert model.fare == 200

    def test_fare_zero_allowed(self):
        model = TransportCalculatorOutput(success=True, fare=0)
        assert model.fare == 0

    def test_fare_negative_raises(self):
        with pytest.raises(ValidationError):
            TransportCalculatorOutput(success=True, fare=-1)


class TestTrainRouteRecord:
    """TrainRouteRecord のテスト"""

    def test_valid(self):
        model = TrainRouteRecord(departure="渋谷", destination="新宿", fare=170)
        assert model.fare == 170

    def test_fare_one_allowed(self):
        model = TrainRouteRecord(departure="A", destination="B", fare=1)
        assert model.fare == 1

    def test_fare_zero_raises(self):
        with pytest.raises(ValidationError):
            TrainRouteRecord(departure="A", destination="B", fare=0)


class TestExpenseItem:
    """ExpenseItem のテスト"""

    def test_valid(self):
        item = ExpenseItem(
            purchase_date="2026-05-17",
            store_name="文具店",
            item_name="ボールペン",
            expense_category="事務用品費",
            amount=500,
            business_purpose="業務用",
        )
        assert item.amount == 500

    def test_amount_zero_allowed(self):
        item = ExpenseItem(
            purchase_date="2026-05-17",
            store_name="店",
            item_name="品",
            expense_category="事務用品費",
            amount=0,
            business_purpose="目的",
        )
        assert item.amount == 0

    def test_amount_negative_raises(self):
        with pytest.raises(ValidationError):
            ExpenseItem(
                purchase_date="2026-05-17",
                store_name="店",
                item_name="品",
                expense_category="事務用品費",
                amount=-1,
                business_purpose="目的",
            )


class TestExpenseReportInput:
    """ExpenseReportInput のテスト"""

    def test_valid(self):
        model = ExpenseReportInput(
            items=[
                ExpenseItem(
                    purchase_date="2026-05-17",
                    store_name="店",
                    item_name="品",
                    expense_category="事務用品費",
                    amount=100,
                    business_purpose="目的",
                )
            ]
        )
        assert len(model.items) == 1

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError):
            ExpenseReportInput(items=[])


class TestTransportReportInput:
    """TransportReportInput のテスト"""

    def test_valid(self):
        model = TransportReportInput(
            items=[
                TransportItem(
                    travel_date="2026-05-17",
                    departure="渋谷",
                    destination="新宿",
                    transport_type="電車",
                    fare=170,
                    business_purpose="打合せ",
                )
            ]
        )
        assert len(model.items) == 1

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError):
            TransportReportInput(items=[])
