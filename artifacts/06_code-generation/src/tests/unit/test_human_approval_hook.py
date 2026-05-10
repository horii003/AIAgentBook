"""コンソール承認アダプターとHumanApprovalHookの単体テスト"""
import pytest
from unittest.mock import MagicMock, patch
from handlers.console_approval_adapter import console_approval_callback
from handlers.human_approval_hook import HumanApprovalHook


class TestConsoleApprovalAdapter:
    def test_choice_1_returns_approved(self):
        with patch("builtins.input", return_value="1"):
            result = console_approval_callback("test_tool", {})
        assert result == (True, "")

    def test_choice_2_returns_revision(self):
        with patch("builtins.input", side_effect=["2", "修正してください"]):
            result = console_approval_callback("test_tool", {})
        assert result == (False, "修正してください")

    def test_choice_3_returns_cancel(self):
        with patch("builtins.input", return_value="3"):
            result = console_approval_callback("test_tool", {})
        assert result == (False, "CANCEL")

    def test_invalid_choice_returns_cancel(self):
        with patch("builtins.input", return_value="9"):
            result = console_approval_callback("test_tool", {})
        assert result == (False, "CANCEL")


class TestHumanApprovalHook:
    def _make_event(self, tool_name: str):
        event = MagicMock()
        event.tool_use = {"name": tool_name, "input": {}}
        event.cancel_tool = False
        return event

    def test_approved_does_not_cancel(self):
        """TC-UNIT-046: コールバックが(True, "")を返した場合にツール実行が許可されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: (True, ""),
        )
        event = self._make_event("generate_transport_form")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False

    def test_revision_sets_cancel_tool(self):
        """TC-UNIT-047: コールバックが(False, "修正内容")を返した場合にキャンセルされること"""
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: (False, "修正してください"),
        )
        event = self._make_event("generate_transport_form")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool == "修正してください"

    def test_cancel_sets_cancel_message(self):
        """コールバックが(False, "CANCEL")を返した場合にキャンセルメッセージが設定されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: (False, "CANCEL"),
        )
        event = self._make_event("generate_transport_form")
        hook._handle_before_tool_call(event)
        assert "キャンセル" in event.cancel_tool

    def test_non_target_tool_skipped(self):
        """TC-UNIT-048: 対象外ツール呼び出し時にスキップされること"""
        called = []
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: called.append(t) or (True, ""),
        )
        event = self._make_event("calculate_transport_fare")
        hook._handle_before_tool_call(event)
        assert len(called) == 0
