"""Human-in-the-Loop承認フックの単体テスト"""

from unittest.mock import MagicMock

from handlers.human_approval_hook import HumanApprovalHook


def _make_event(tool_name="generate_expense_report", tool_input=None):
    event = MagicMock()
    event.tool_use = {"name": tool_name, "input": tool_input or {}, "toolUseId": "id1"}
    event.cancel_tool = False
    return event


class TestHumanApprovalHook:
    """HumanApprovalHook のテスト"""

    def test_skip_non_target_tool(self):
        """対象外ツールではスキップされること"""
        hook = HumanApprovalHook(
            target_tools=["generate_expense_report"],
            approval_callback=lambda n, p: (True, ""),
        )
        event = _make_event(tool_name="calculate_transport_fare")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False

    def test_approved_ok(self):
        """承認OK時にツールが実行されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_expense_report"],
            approval_callback=lambda n, p: (True, ""),
        )
        event = _make_event()
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False

    def test_correction(self):
        """修正指示時にevent.cancel_toolにメッセージが設定されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_expense_report"],
            approval_callback=lambda n, p: (False, "金額を修正してください"),
        )
        event = _make_event()
        hook._handle_before_tool_call(event)
        assert event.cancel_tool == "金額を修正してください"

    def test_cancel(self):
        """キャンセル時にevent.cancel_toolにキャンセルメッセージが設定されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_expense_report"],
            approval_callback=lambda n, p: (False, "CANCEL"),
        )
        event = _make_event()
        hook._handle_before_tool_call(event)
        assert "キャンセル" in event.cancel_tool

    def test_multiple_target_tools(self):
        """複数の対象ツールで承認ゲートが発火すること"""
        hook = HumanApprovalHook(
            target_tools=["generate_expense_report", "generate_transport_report"],
            approval_callback=lambda n, p: (True, ""),
        )
        event = _make_event(tool_name="generate_transport_report")
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False
