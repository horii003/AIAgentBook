"""output_generator の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

import pytest

# strands モジュールをモックとして登録
if "strands" not in sys.modules:
    mock_strands = MagicMock()
    sys.modules["strands"] = mock_strands
    sys.modules["strands.models"] = mock_strands.models

# @tool デコレータをモック（関数をそのまま返す）
import strands
strands.tool = lambda *args, **kwargs: (lambda f: f) if args and callable(args[0]) else (lambda f: f)
strands.ToolContext = MagicMock

# openpyxl をモック
mock_openpyxl = MagicMock()
mock_wb = MagicMock()
mock_ws = MagicMock()
mock_wb.active = mock_ws
mock_openpyxl.load_workbook.return_value = mock_wb
sys.modules["openpyxl"] = mock_openpyxl

# モジュールをリロード
if "tools.output_generator" in sys.modules:
    del sys.modules["tools.output_generator"]

import tools.output_generator as og


def _make_tool_context(user_name="山田太郎", request_date="2026-05-21"):
    """ToolContext のモックを作成する"""
    ctx = MagicMock()
    ctx.invocation_state = {"user_name": user_name, "request_date": request_date}
    return ctx


def _make_transport_records():
    """有効な移動区間データを返す"""
    return [
        {
            "travel_date": "2026-05-21",
            "departure": "東京",
            "destination": "新宿",
            "transport_type": "電車",
            "fare": 200,
            "business_purpose": "顧客訪問",
        }
    ]


def _make_expense_records():
    """有効な経費データを返す"""
    return [
        {
            "expense_date": "2026-05-21",
            "store_name": "文具店",
            "item_name": "ボールペン",
            "amount": 500,
            "category": "事務用品費",
            "business_purpose": "業務用",
        }
    ]


class TestGenerateTransportExpenseForm:
    """generate_transport_expense_form のテスト"""

    def setup_method(self):
        """各テスト前にモックをリセットする"""
        mock_openpyxl.load_workbook.reset_mock()
        mock_wb.save.reset_mock()

    def test_success_with_template(self):
        """テンプレートが存在する場合に正常生成されること"""
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                ctx = _make_tool_context()
                result = og.generate_transport_expense_form(
                    transport_records=_make_transport_records(),
                    needs_approval=False,
                    tool_context=ctx,
                )
        assert result["success"] is True
        assert result["file_path"] is not None
        assert result["error_message"] is None

    def test_template_not_found(self):
        """テンプレートファイルが存在しない場合にエラーが返ること"""
        with patch("os.path.exists", return_value=False):
            ctx = _make_tool_context()
            result = og.generate_transport_expense_form(
                transport_records=_make_transport_records(),
                needs_approval=False,
                tool_context=ctx,
            )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_validation_error_empty_records(self):
        """空のリストでバリデーションエラーが返ること"""
        ctx = _make_tool_context()
        result = og.generate_transport_expense_form(
            transport_records=[],
            needs_approval=False,
            tool_context=ctx,
        )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_needs_approval_true(self):
        """needs_approval=True の場合に正常生成されること"""
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                ctx = _make_tool_context()
                result = og.generate_transport_expense_form(
                    transport_records=_make_transport_records(),
                    needs_approval=True,
                    tool_context=ctx,
                )
        assert result["success"] is True

    def test_invocation_state_used(self):
        """invocation_state から申請者名・申請日が取得されること"""
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                ctx = _make_tool_context(user_name="鈴木花子", request_date="2026-06-01")
                og.generate_transport_expense_form(
                    transport_records=_make_transport_records(),
                    needs_approval=False,
                    tool_context=ctx,
                )
        # ヘッダーセルへの書き込みを確認
        mock_ws.__setitem__.assert_any_call("B1", "鈴木花子")


class TestGenerateGeneralExpenseForm:
    """generate_general_expense_form のテスト"""

    def setup_method(self):
        """各テスト前にモックをリセットする"""
        mock_openpyxl.load_workbook.reset_mock()
        mock_wb.save.reset_mock()

    def test_success_with_template(self):
        """テンプレートが存在する場合に正常生成されること"""
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                ctx = _make_tool_context()
                result = og.generate_general_expense_form(
                    expense_records=_make_expense_records(),
                    needs_approval=False,
                    tool_context=ctx,
                )
        assert result["success"] is True
        assert result["file_path"] is not None

    def test_template_not_found(self):
        """テンプレートファイルが存在しない場合にエラーが返ること"""
        with patch("os.path.exists", return_value=False):
            ctx = _make_tool_context()
            result = og.generate_general_expense_form(
                expense_records=_make_expense_records(),
                needs_approval=False,
                tool_context=ctx,
            )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_validation_error_empty_records(self):
        """空のリストでバリデーションエラーが返ること"""
        ctx = _make_tool_context()
        result = og.generate_general_expense_form(
            expense_records=[],
            needs_approval=False,
            tool_context=ctx,
        )
        assert result["success"] is False
        assert result["error_message"] is not None


class TestGenerateFormHelper:
    """_generate_form ヘルパーのテスト"""

    def test_io_error_returns_error(self):
        """IOError 発生時にエラーが返ること"""
        mock_wb.save.side_effect = IOError("書き込みエラー")
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                ctx = _make_tool_context()
                result = og.generate_transport_expense_form(
                    transport_records=_make_transport_records(),
                    needs_approval=False,
                    tool_context=ctx,
                )
        assert result["success"] is False
        assert result["error_message"] is not None
        mock_wb.save.side_effect = None  # リセット
