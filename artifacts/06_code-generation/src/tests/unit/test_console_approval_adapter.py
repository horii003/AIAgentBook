"""console_approval_adapter の単体テスト"""
from unittest.mock import patch

from handlers.console_approval_adapter import console_approval_callback


class TestConsoleApprovalCallback:
    """console_approval_callback のテスト"""

    def test_approval_returns_true_empty_string(self):
        """承認入力時に (True, "") を返すこと"""
        with patch("builtins.input", return_value="1"):
            result = console_approval_callback("test_tool", {"key": "value"})
        assert result == (True, "")

    def test_cancel_returns_false_cancel(self):
        """キャンセル入力時に (False, "CANCEL") を返すこと"""
        with patch("builtins.input", return_value="3"):
            result = console_approval_callback("test_tool", {"key": "value"})
        assert result == (False, "CANCEL")

    def test_feedback_returns_false_with_message(self):
        """修正要望入力時に (False, "修正内容文字列") を返すこと"""
        with patch("builtins.input", side_effect=["2", "移動日を修正してください"]):
            result = console_approval_callback("test_tool", {"key": "value"})
        assert result == (False, "移動日を修正してください")

    def test_invalid_then_approval(self):
        """無効な入力後に承認した場合に (True, "") を返すこと"""
        with patch("builtins.input", side_effect=["invalid", "1"]):
            result = console_approval_callback("test_tool", {})
        assert result == (True, "")

    def test_empty_feedback_then_cancel(self):
        """修正内容が空の場合に再入力を促し、その後キャンセルできること"""
        with patch("builtins.input", side_effect=["2", "", "3"]):
            result = console_approval_callback("test_tool", {})
        assert result == (False, "CANCEL")
