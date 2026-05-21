"""HumanApprovalHook の単体テスト"""
import sys
from unittest.mock import MagicMock

import pytest

# strands.hooks モジュールをモックとして登録（test_loop_control_hookと同様）
if "strands.hooks" not in sys.modules:
    mock_strands_hooks = MagicMock()

    class MockHookProvider:
        pass

    mock_strands_hooks.HookProvider = MockHookProvider
    mock_strands_hooks.HookRegistry = MagicMock
    mock_strands_hooks.BeforeToolCallEvent = MagicMock
    mock_strands_hooks.AfterInvocationEvent = MagicMock
    mock_strands_hooks.BeforeInvocationEvent = MagicMock
    mock_strands_hooks.AfterModelCallEvent = MagicMock
    mock_strands_hooks.BeforeModelCallEvent = MagicMock
    mock_strands_hooks.AfterToolCallEvent = MagicMock

    sys.modules.setdefault("strands", MagicMock())
    sys.modules.setdefault("strands.hooks", mock_strands_hooks)

# モジュールをリロード
if "handlers.human_approval_hook" in sys.modules:
    del sys.modules["handlers.human_approval_hook"]

from handlers.human_approval_hook import HumanApprovalHook


def _make_tool_event(tool_name: str, tool_input: dict = None):
    """BeforeToolCallEvent のモックを作成する"""
    event = MagicMock()
    event.tool_use = {"name": tool_name, "input": tool_input or {}}
    event.cancel_tool = False
    return event


class TestHumanApprovalHookInit:
    """HumanApprovalHook の初期化テスト"""

    def test_default_target_tools(self):
        """デフォルトの承認対象ツールが設定されること"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        assert "generate_transport_expense_form" in hook._target_tools
        assert "generate_general_expense_form" in hook._target_tools

    def test_custom_target_tools(self):
        """カスタムの承認対象ツールが設定されること"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(
            approval_callback=callback,
            approval_required_tools=["custom_tool"],
        )
        assert "custom_tool" in hook._target_tools
        assert "generate_transport_expense_form" not in hook._target_tools


class TestRegisterHooks:
    """register_hooks のテスト"""

    def test_registers_before_tool_call_event(self):
        """BeforeToolCallEvent が登録されること"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        registry = MagicMock()
        hook.register_hooks(registry)
        assert registry.add_callback.call_count == 1


class TestOnBeforeToolCall:
    """_on_before_tool_call のテスト"""

    def test_skips_non_target_tool(self):
        """対象外ツールの場合にコールバックが呼ばれないこと"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("calculate_transport_fare")
        hook._on_before_tool_call(event)
        callback.assert_not_called()

    def test_approval_does_not_set_cancel_tool(self):
        """承認時に event.cancel_tool が設定されないこと"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_transport_expense_form")
        hook._on_before_tool_call(event)
        # cancel_toolが変更されていないこと（Falseのまま）
        assert event.cancel_tool is False

    def test_cancel_sets_cancel_tool_message(self):
        """キャンセル時に event.cancel_tool にメッセージが設定されること"""
        callback = MagicMock(return_value=(False, "CANCEL"))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_transport_expense_form")
        hook._on_before_tool_call(event)
        assert event.cancel_tool == "申請書生成をキャンセルしました。"

    def test_feedback_sets_cancel_tool_with_feedback(self):
        """修正要望時に event.cancel_tool に修正内容が設定されること"""
        callback = MagicMock(return_value=(False, "移動日を修正してください"))
        hook = HumanApprovalHook(approval_callback=callback)
        event = _make_tool_event("generate_general_expense_form")
        hook._on_before_tool_call(event)
        assert event.cancel_tool == "移動日を修正してください"

    def test_skips_when_tool_use_is_none(self):
        """event.tool_use が None の場合にスキップされること"""
        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)
        event = MagicMock()
        event.tool_use = None
        hook._on_before_tool_call(event)
        callback.assert_not_called()


class TestBuildCancelMessage:
    """_build_cancel_message のテスト"""

    def test_cancel_message_for_cancel(self):
        """CANCEL の場合にキャンセルメッセージを返すこと"""
        callback = MagicMock()
        hook = HumanApprovalHook(approval_callback=callback)
        result = hook._build_cancel_message("test_tool", "CANCEL")
        assert "キャンセル" in result

    def test_cancel_message_for_empty_feedback(self):
        """空のフィードバックの場合にキャンセルメッセージを返すこと"""
        callback = MagicMock()
        hook = HumanApprovalHook(approval_callback=callback)
        result = hook._build_cancel_message("test_tool", "")
        assert "キャンセル" in result

    def test_feedback_message_returned_as_is(self):
        """修正内容がそのまま返されること"""
        callback = MagicMock()
        hook = HumanApprovalHook(approval_callback=callback)
        result = hook._build_cancel_message("test_tool", "移動日を修正してください")
        assert result == "移動日を修正してください"
