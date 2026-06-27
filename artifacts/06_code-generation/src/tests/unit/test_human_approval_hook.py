"""HumanApprovalHookの単体テスト"""
from unittest.mock import MagicMock
import pytest

from handlers.human_approval_hook import HumanApprovalHook


class TestHumanApprovalHook:
    """HumanApprovalHookのテスト"""

    def _make_event(self, tool_name: str, tool_input: dict = None):
        event = MagicMock()
        event.tool_use = {"name": tool_name, "input": tool_input or {}}
        event.cancel_tool = False
        return event

    def test_non_target_tool_skipped(self):
        hook = HumanApprovalHook(target_tools=["target_tool"])
        event = self._make_event("other_tool")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False

    def test_callback_approved(self):
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(
            target_tools=["target_tool"],
            approval_callback=callback,
        )
        event = self._make_event("target_tool")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False

    def test_callback_cancel(self):
        callback = MagicMock(return_value=(False, "CANCEL"))
        hook = HumanApprovalHook(
            target_tools=["target_tool"],
            approval_callback=callback,
        )
        event = self._make_event("target_tool")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool == "ユーザーによりキャンセルされました。"

    def test_callback_modification(self):
        callback = MagicMock(return_value=(False, "金額を修正してください"))
        hook = HumanApprovalHook(
            target_tools=["target_tool"],
            approval_callback=callback,
        )
        event = self._make_event("target_tool")
        hook._handle_before_tool_call(event)
        assert "修正が指示されました" in event.cancel_tool
        assert "金額を修正してください" in event.cancel_tool

    def test_register_hooks_calls_add_callback_once(self):
        hook = HumanApprovalHook(target_tools=["target_tool"])
        registry = MagicMock()
        hook.register_hooks(registry)
        assert registry.add_callback.call_count == 1
