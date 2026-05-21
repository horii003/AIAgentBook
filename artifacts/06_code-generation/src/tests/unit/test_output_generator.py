"""申請書生成ツールの単体テスト"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
from openpyxl import Workbook
import tools.output_generator as og


def _make_tool_context(applicant_name="山田太郎", application_date="2026-01-15"):
    ctx = MagicMock()
    ctx.invocation_state = {"applicant_name": applicant_name, "application_date": application_date}
    return ctx


def _create_mock_template(tmp_path, filename="template.xlsx"):
    """モックテンプレートExcelファイルを作成する。"""
    wb = Workbook()
    ws = wb.active
    path = str(tmp_path / filename)
    wb.save(path)
    return path


class TestGenerateExpenseReport:
    """generate_expense_report のテスト"""

    def test_success_with_valid_items(self, tmp_path):
        """正常系: モックテンプレートを使用して申請書を生成できること"""
        template_path = _create_mock_template(tmp_path, "expense_template.xlsx")
        output_dir = str(tmp_path / "output")

        original_template = og._EXPENSE_TEMPLATE_PATH
        original_output = og._OUTPUT_DIR
        og._EXPENSE_TEMPLATE_PATH = template_path
        og._OUTPUT_DIR = output_dir

        try:
            ctx = _make_tool_context()
            items = [{
                "purchase_date": "2026-01-10",
                "store_name": "テスト店",
                "item_name": "ボールペン",
                "expense_category": "事務用品費",
                "amount": 500,
                "business_purpose": "業務用",
            }]
            result = og.generate_expense_report.__wrapped__(items=items, tool_context=ctx)
            assert result["success"] is True
            assert result["file_path"] is not None
            assert os.path.exists(result["file_path"])
        finally:
            og._EXPENSE_TEMPLATE_PATH = original_template
            og._OUTPUT_DIR = original_output

    def test_validation_error_returns_failure(self, tmp_path):
        """バリデーションエラー時に success=False が返ること"""
        ctx = _make_tool_context()
        items = [{"purchase_date": "invalid-date", "store_name": "", "item_name": "", "expense_category": "不正区分", "amount": -1, "business_purpose": ""}]
        result = og.generate_expense_report.__wrapped__(items=items, tool_context=ctx)
        assert result["success"] is False
        assert result["file_path"] is None


class TestGenerateTransportReport:
    """generate_transport_report のテスト"""

    def test_success_with_valid_items(self, tmp_path):
        """正常系: モックテンプレートを使用して申請書を生成できること"""
        template_path = _create_mock_template(tmp_path, "transport_template.xlsx")
        output_dir = str(tmp_path / "output")

        original_template = og._TRANSPORT_TEMPLATE_PATH
        original_output = og._OUTPUT_DIR
        og._TRANSPORT_TEMPLATE_PATH = template_path
        og._OUTPUT_DIR = output_dir

        try:
            ctx = _make_tool_context()
            items = [{
                "travel_date": "2026-01-10",
                "departure": "渋谷",
                "destination": "新宿",
                "transport_type": "電車",
                "fare": 200,
                "business_purpose": "業務出張",
            }]
            result = og.generate_transport_report.__wrapped__(items=items, tool_context=ctx)
            assert result["success"] is True
            assert result["file_path"] is not None
            assert os.path.exists(result["file_path"])
        finally:
            og._TRANSPORT_TEMPLATE_PATH = original_template
            og._OUTPUT_DIR = original_output

    def test_validation_error_returns_failure(self):
        """バリデーションエラー時に success=False が返ること"""
        ctx = _make_tool_context()
        items = []  # 空リストはバリデーションエラー
        result = og.generate_transport_report.__wrapped__(items=items, tool_context=ctx)
        assert result["success"] is False
        assert result["file_path"] is None
