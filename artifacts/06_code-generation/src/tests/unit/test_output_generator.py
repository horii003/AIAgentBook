"""申請書生成ツールの単体テスト"""
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open

from tools.output_generator import (
    generate_transportation_expense_form,
    generate_general_expense_form,
    _generate_form,
    _sanitize_cell,
)


def _make_tool_context(applicant_name="山田太郎", application_date="2026-05-23"):
    ctx = MagicMock()
    ctx.invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
    }
    return ctx


_VALID_TRANSPORT_ITEMS = [{
    "travel_date": "2026-05-23",
    "departure": "東京",
    "destination": "新宿",
    "transport_type": "電車",
    "amount": 200,
    "purpose": "顧客訪問",
}]

_VALID_GENERAL_ITEMS = [{
    "purchase_date": "2026-05-23",
    "store_name": "文具堂",
    "item_name": "ノート",
    "expense_category": "事務用品費",
    "amount": 500,
    "purpose": "業務用",
}]


class TestGenerateForm:
    """_generate_form関数のテスト"""

    def test_template_not_found(self):
        from models.data_models import TransportationExpenseFormInput
        validated = TransportationExpenseFormInput(items=_VALID_TRANSPORT_ITEMS)

        with patch("os.path.exists", return_value=False):
            result = _generate_form(
                template_path="nonexistent.xlsx",
                applicant_name="山田太郎",
                application_date="2026-05-23",
                validated=validated,
                write_detail_rows=lambda ws, items: None,
                output_filename_prefix="テスト",
            )

        assert result["success"] is False
        assert "テンプレート" in result["error_message"]

    def test_io_error_returns_error(self):
        from models.data_models import TransportationExpenseFormInput
        validated = TransportationExpenseFormInput(items=_VALID_TRANSPORT_ITEMS)

        with patch("os.path.exists", return_value=True):
            with patch("tools.output_generator.load_workbook", side_effect=IOError("permission denied")):
                result = _generate_form(
                    template_path="template.xlsx",
                    applicant_name="山田太郎",
                    application_date="2026-05-23",
                    validated=validated,
                    write_detail_rows=lambda ws, items: None,
                    output_filename_prefix="テスト",
                )

        assert result["success"] is False


class TestGenerateTransportationExpenseForm:
    """generate_transportation_expense_form関数のテスト"""

    def test_missing_applicant_name_returns_error(self):
        ctx = _make_tool_context(applicant_name="")
        result = generate_transportation_expense_form.__wrapped__(
            items=_VALID_TRANSPORT_ITEMS,
            tool_context=ctx,
        )
        assert result["success"] is False
        assert "申請者情報" in result["error_message"]

    def test_empty_items_returns_error(self):
        ctx = _make_tool_context()
        result = generate_transportation_expense_form.__wrapped__(
            items=[],
            tool_context=ctx,
        )
        assert result["success"] is False

    def test_output_filename_contains_timestamp(self):
        ctx = _make_tool_context()
        mock_wb = MagicMock()
        mock_wb.active = MagicMock()

        with patch("os.path.exists", return_value=True):
            with patch("tools.output_generator.load_workbook", return_value=mock_wb):
                with patch("os.makedirs"):
                    result = generate_transportation_expense_form.__wrapped__(
                        items=_VALID_TRANSPORT_ITEMS,
                        tool_context=ctx,
                    )

        if result["success"]:
            assert "交通費精算申請書" in result["file_path"]


class TestGenerateGeneralExpenseForm:
    """generate_general_expense_form関数のテスト"""

    def test_missing_applicant_name_returns_error(self):
        ctx = _make_tool_context(applicant_name="")
        result = generate_general_expense_form.__wrapped__(
            items=_VALID_GENERAL_ITEMS,
            tool_context=ctx,
        )
        assert result["success"] is False

    def test_empty_items_returns_error(self):
        ctx = _make_tool_context()
        result = generate_general_expense_form.__wrapped__(
            items=[],
            tool_context=ctx,
        )
        assert result["success"] is False


class TestSanitizeCell:
    """_sanitize_cell ヘルパーの単体テスト"""

    def test_equals_prefix_sanitized(self):
        assert _sanitize_cell("=SUM(A1:A10)") == "'=SUM(A1:A10)"

    def test_plus_prefix_sanitized(self):
        assert _sanitize_cell("+1234") == "'+1234"

    def test_minus_prefix_sanitized(self):
        assert _sanitize_cell("-1") == "'-1"

    def test_at_prefix_sanitized(self):
        assert _sanitize_cell("@SUM") == "'@SUM"

    def test_normal_string_unchanged(self):
        assert _sanitize_cell("東京") == "東京"

    def test_empty_string_unchanged(self):
        assert _sanitize_cell("") == ""

    def test_integer_unchanged(self):
        assert _sanitize_cell(200) == 200

    def test_none_unchanged(self):
        assert _sanitize_cell(None) is None
