"""申請書生成ツールの単体テスト"""
import os
import pytest
from unittest.mock import MagicMock, patch
import openpyxl
import tools.output_generator as og


def make_tool_context(applicant_name="田中太郎", application_date="2026-05-10"):
    """ToolContextのモックを作成する"""
    ctx = MagicMock()
    ctx.invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
    }
    return ctx


def make_transport_items():
    return [
        {
            "travel_date": "2026-05-10",
            "departure": "東京",
            "destination": "大阪",
            "transport_type": "電車",
            "fare": 13240.0,
            "purpose": "出張",
        }
    ]


def make_expense_items():
    return [
        {
            "purchase_date": "2026-05-10",
            "item_name": "ノート",
            "amount": 500.0,
            "expense_category": "事務用品費",
            "purpose": "業務用",
        }
    ]


@pytest.fixture
def transport_template(tmp_path, monkeypatch):
    """テスト用交通費テンプレートを作成する"""
    wb = openpyxl.Workbook()
    ws = wb.active
    template_path = str(tmp_path / "transport_template.xlsx")
    wb.save(template_path)
    monkeypatch.setattr(og, "_TRANSPORT_TEMPLATE_PATH", template_path)
    monkeypatch.setattr(og, "_OUTPUT_DIR", str(tmp_path / "output"))
    return template_path


@pytest.fixture
def expense_template(tmp_path, monkeypatch):
    """テスト用経費テンプレートを作成する"""
    wb = openpyxl.Workbook()
    ws = wb.active
    template_path = str(tmp_path / "expense_template.xlsx")
    wb.save(template_path)
    monkeypatch.setattr(og, "_EXPENSE_TEMPLATE_PATH", template_path)
    monkeypatch.setattr(og, "_OUTPUT_DIR", str(tmp_path / "output"))
    return template_path


class TestGenerateTransportForm:
    def test_valid_items_generates_file(self, transport_template, tmp_path):
        """TC-UNIT-010: 有効な移動明細で申請書が生成されること"""
        ctx = make_tool_context()
        result = og.generate_transport_form.__wrapped__(make_transport_items(), ctx)
        assert result["success"] is True
        assert len(result["file_path"]) > 0
        assert os.path.exists(result["file_path"])

    def test_missing_template_returns_error(self, monkeypatch, tmp_path):
        """TC-UNIT-011: テンプレート不存在時にsuccess=Falseが返ること"""
        monkeypatch.setattr(og, "_TRANSPORT_TEMPLATE_PATH", "nonexistent.xlsx")
        monkeypatch.setattr(og, "_OUTPUT_DIR", str(tmp_path / "output"))
        ctx = make_tool_context()
        result = og.generate_transport_form.__wrapped__(make_transport_items(), ctx)
        assert result["success"] is False
        assert len(result["error_message"]) > 0

    def test_empty_items_returns_error(self, transport_template):
        """TC-UNIT-012: 移動明細が空の場合にsuccess=Falseが返ること"""
        ctx = make_tool_context()
        result = og.generate_transport_form.__wrapped__([], ctx)
        assert result["success"] is False
        assert len(result["error_message"]) > 0


class TestGenerateExpenseForm:
    def test_valid_items_generates_file(self, expense_template, tmp_path):
        """TC-UNIT-013: 有効な経費明細で申請書が生成されること"""
        ctx = make_tool_context()
        result = og.generate_expense_form.__wrapped__(make_expense_items(), ctx)
        assert result["success"] is True
        assert len(result["file_path"]) > 0
        assert os.path.exists(result["file_path"])

    def test_empty_items_returns_error(self, expense_template):
        """TC-UNIT-014: 経費明細が空の場合にsuccess=Falseが返ること"""
        ctx = make_tool_context()
        result = og.generate_expense_form.__wrapped__([], ctx)
        assert result["success"] is False
        assert len(result["error_message"]) > 0

    def test_missing_applicant_name_returns_error(self, expense_template):
        """applicant_nameがない場合にsuccess=Falseが返ること"""
        ctx = make_tool_context(applicant_name="")
        result = og.generate_expense_form.__wrapped__(make_expense_items(), ctx)
        assert result["success"] is False
