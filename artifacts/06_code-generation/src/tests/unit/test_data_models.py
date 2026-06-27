"""データモデルの単体テスト"""
import pytest
from pydantic import ValidationError

from models.data_models import (
    validate_date,
    validate_amount,
    normalize_transport_type,
    normalize_expense_category,
    TransportCalculatorInput,
    TransportationExpenseFormInput,
    GeneralExpenseFormInput,
    RouteData,
)


class TestValidateDate:
    """validate_date関数のテスト"""

    def test_yyyy_mm_dd(self):
        assert validate_date("2026-05-23") == "2026-05-23"

    def test_yyyy_slash_mm_slash_dd(self):
        assert validate_date("2026/05/23") == "2026-05-23"

    def test_japanese_format(self):
        assert validate_date("2026年5月23日") == "2026-05-23"

    def test_japanese_format_single_digit(self):
        assert validate_date("2026年5月3日") == "2026-05-03"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            validate_date("20260523")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            validate_date("")


class TestValidateAmount:
    """validate_amount関数のテスト"""

    def test_int(self):
        assert validate_amount(1000) == 1000

    def test_float(self):
        assert validate_amount(1000.0) == 1000

    def test_comma_string(self):
        assert validate_amount("1,000") == 1000

    def test_yen_string(self):
        assert validate_amount("1000円") == 1000

    def test_zero(self):
        assert validate_amount(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            validate_amount(-100)

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            validate_amount("abc")


class TestNormalizeTransportType:
    """normalize_transport_type関数のテスト"""

    def test_railroad(self):
        assert normalize_transport_type("鉄道") == "電車"

    def test_jr(self):
        assert normalize_transport_type("JR") == "電車"

    def test_subway(self):
        assert normalize_transport_type("地下鉄") == "電車"

    def test_bus(self):
        assert normalize_transport_type("路線バス") == "バス"

    def test_airplane(self):
        assert normalize_transport_type("航空機") == "飛行機"

    def test_already_normalized(self):
        assert normalize_transport_type("電車") == "電車"

    def test_unknown(self):
        assert normalize_transport_type("自転車") == "自転車"


class TestNormalizeExpenseCategory:
    """normalize_expense_category関数のテスト"""

    def test_office_supplies(self):
        assert normalize_expense_category("事務用品") == "事務用品費"

    def test_accommodation(self):
        assert normalize_expense_category("宿泊") == "宿泊費"

    def test_hotel(self):
        assert normalize_expense_category("ホテル") == "宿泊費"

    def test_qualification(self):
        assert normalize_expense_category("資格") == "資格精算費"

    def test_exam(self):
        assert normalize_expense_category("試験") == "資格精算費"

    def test_other(self):
        assert normalize_expense_category("その他") == "その他経費"

    def test_already_normalized(self):
        assert normalize_expense_category("事務用品費") == "事務用品費"


class TestTransportCalculatorInput:
    """TransportCalculatorInputモデルのテスト"""

    def test_valid(self):
        m = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-05-23",
        )
        assert m.departure == "東京"
        assert m.transport_type == "電車"

    def test_empty_departure_raises(self):
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="",
                destination="新宿",
                transport_type="電車",
                travel_date="2026-05-23",
            )

    def test_invalid_transport_type_raises(self):
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="東京",
                destination="新宿",
                transport_type="自転車",
                travel_date="2026-05-23",
            )

    def test_transport_type_normalization(self):
        m = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="JR",
            travel_date="2026-05-23",
        )
        assert m.transport_type == "電車"

    def test_date_normalization(self):
        m = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="電車",
            travel_date="2026/05/23",
        )
        assert m.travel_date == "2026-05-23"


class TestTransportationExpenseFormInput:
    """TransportationExpenseFormInputモデルのテスト"""

    def test_valid(self):
        m = TransportationExpenseFormInput(items=[{
            "travel_date": "2026-05-23",
            "departure": "東京",
            "destination": "新宿",
            "transport_type": "電車",
            "amount": 200,
            "purpose": "顧客訪問",
        }])
        assert len(m.items) == 1

    def test_empty_items_raises(self):
        with pytest.raises(ValidationError):
            TransportationExpenseFormInput(items=[])

    def test_date_normalization_in_items(self):
        m = TransportationExpenseFormInput(items=[{
            "travel_date": "2026/05/23",
            "departure": "東京",
            "destination": "新宿",
            "transport_type": "電車",
            "amount": 200,
            "purpose": "顧客訪問",
        }])
        assert m.items[0]["travel_date"] == "2026-05-23"

    def test_amount_normalization_in_items(self):
        m = TransportationExpenseFormInput(items=[{
            "travel_date": "2026-05-23",
            "departure": "東京",
            "destination": "新宿",
            "transport_type": "電車",
            "amount": "1,000",
            "purpose": "顧客訪問",
        }])
        assert m.items[0]["amount"] == 1000


class TestGeneralExpenseFormInput:
    """GeneralExpenseFormInputモデルのテスト"""

    def test_valid(self):
        m = GeneralExpenseFormInput(items=[{
            "purchase_date": "2026-05-23",
            "store_name": "文具堂",
            "item_name": "ノート",
            "expense_category": "事務用品費",
            "amount": 500,
            "purpose": "業務用",
        }])
        assert len(m.items) == 1

    def test_empty_items_raises(self):
        with pytest.raises(ValidationError):
            GeneralExpenseFormInput(items=[])

    def test_expense_category_normalization(self):
        m = GeneralExpenseFormInput(items=[{
            "purchase_date": "2026-05-23",
            "store_name": "文具堂",
            "item_name": "ノート",
            "expense_category": "事務用品",
            "amount": 500,
            "purpose": "業務用",
        }])
        assert m.items[0]["expense_category"] == "事務用品費"
