"""Human-in-the-Loop承認フックの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, call
from handlers.human_approval_hook import HumanApprovalHook


def _make_tool_event(tool_name: str, tool_params: dict = None):
    """BeforeToolCallEvent のモックを作成する。"""
    event = MagicMock()
    event.tool_use = {"name": tool_name, "input": tool_params or {}}
    event.cancel_tool = False
    return event


class TestHumanApprovalHook:
    """HumanApprovalHook のテスト"""

    def test_non_target_tool_does_not_call_callback(self):
        """対象外ツールの場合にコールバックが呼ばれないこと"""
        callback = MagicMock()
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("calculate_transport_fare")
        hook._on_before_tool_call(event)
        callback.assert_not_called()

    def test_approved_true_does_not_set_cancel_tool(self):
        """approved=True の場合に event.cancel_tool が設定されないこと"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_expense_report", {"items": []})
        hook._on_before_tool_call(event)
        # cancel_tool は初期値 False のまま
        assert event.cancel_tool is False

    def test_approved_false_cancel_sets_cancel_tool(self):
        """approved=False, feedback="CANCEL" の場合に event.cancel_tool にメッセージが設定されること"""
        callback = MagicMock(return_value=(False, "CANCEL"))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_transport_report")
        hook._on_before_tool_call(event)
        assert isinstance(event.cancel_tool, str)
        assert len(event.cancel_tool) > 0

    def test_approved_false_with_feedback_sets_revision_message(self):
        """approved=False, feedback="修正内容" の場合に修正要望メッセージが設定されること"""
        callback = MagicMock(return_value=(False, "金額を修正してください"))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_expense_report")
        hook._on_before_tool_call(event)
        assert isinstance(event.cancel_tool, str)
        assert "金額を修正してください" in event.cancel_tool

    def test_custom_approval_required_tools_overrides_default(self):
        """approval_required_tools を明示指定した場合にデフォルトが上書きされること"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(
            approval_callback=callback,
            approval_required_tools=["custom_tool"],
        )
        # デフォルトのツールはスキップされる
        event_default = _make_tool_event("generate_expense_report")
        hook._on_before_tool_call(event_default)
        callback.assert_not_called()

        # カスタムツールは承認が求められる
        event_custom = _make_tool_event("custom_tool")
        hook._on_before_tool_call(event_custom)
        callback.assert_called_once()
